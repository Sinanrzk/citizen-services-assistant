"""
Flask backend for the Citizen Services Assistant.
Provides /chat endpoint for the Streamlit frontend.
"""

import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.catalog import CATEGORIES
from app.llm.pipeline import generate_response
from app.nlp.intent import detect_intent
from app.nlp.slots import SlotFiller
from app.rag.eligibility import check_eligibility
from app.rag.retriever import retrieve

app = Flask(__name__)
CORS(app)

# Track per-session state
_session_state: dict[str, dict] = {}


def _get_welcome_message(category: str) -> str:
    """Generate a welcome message for a category with example questions."""
    cat_data = CATEGORIES.get(category)
    if not cat_data:
        return (
            "👋 Welcome to the Citizen Services Assistant!\n\n"
            "I can help you with information about government schemes, "
            "eligibility checks, application steps, required documents, "
            "and office locations.\n\n"
            "Please select a category to get started."
        )

    scheme_names = [s["name"] for s in cat_data["schemes"].values()]
    scheme_list = ", ".join(scheme_names[:3])

    example_questions = []
    schemes = list(cat_data["schemes"].values())
    if schemes:
        first_scheme = schemes[0]["name"]
        example_questions.append(f"Am I eligible for {first_scheme}?")
        example_questions.append(f"How to apply for {first_scheme}?")
        example_questions.append(f"What documents are needed for {first_scheme}?")

    examples_text = "\n".join(f"  • {q}" for q in example_questions)

    return (
        f"{cat_data['icon']} Welcome to **{cat_data['name']}** services!\n\n"
        f"{cat_data['description']}\n\n"
        f"Available schemes: **{scheme_list}**\n\n"
        f"Here are some things you can ask me:\n{examples_text}\n\n"
        f"How can I help you today?"
    )


def _is_greeting(message: str) -> bool:
    """Check if a message is a greeting or empty."""
    if not message or not message.strip():
        return True
    greetings = {
        "hi", "hello", "hey", "namaste", "good morning",
        "good afternoon", "good evening", "hii", "hiii",
        "start", "help", "menu",
    }
    return message.strip().lower() in greetings


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.

    Expects JSON:
        {
            "session_id": str (optional, auto-generated if missing),
            "message": str,
            "category": str
        }

    Returns JSON:
        {
            "reply": str,
            "state": str ("greeting" | "collecting_slots" | "responding")
        }
    """
    data = request.get_json(force=True)
    session_id = data.get("session_id") or str(uuid.uuid4())
    message = data.get("message", "").strip()
    category = data.get("category", "").strip()

    # Initialize session state if new
    if session_id not in _session_state:
        _session_state[session_id] = {
            "active_slot_filling": False,
            "scheme_id": None,
            "category": category,
        }

    state = _session_state[session_id]

    # Update category if provided
    if category:
        state["category"] = category

    # ----- Handle greetings -----
    if _is_greeting(message) and not state["active_slot_filling"]:
        return jsonify({
            "reply": _get_welcome_message(state.get("category", category)),
            "state": "greeting",
            "session_id": session_id,
        })

    # ----- Handle active slot filling -----
    if state["active_slot_filling"]:
        SlotFiller.process_answer(session_id, message)

        if not SlotFiller.is_complete(session_id):
            next_q = SlotFiller.get_next_question(session_id)
            return jsonify({
                "reply": next_q,
                "state": "collecting_slots",
                "session_id": session_id,
            })

        # Slots complete — check eligibility
        filled_slots = SlotFiller.get_filled_slots(session_id)
        scheme_id = state["scheme_id"]
        cat = state["category"]

        eligibility_result = check_eligibility(cat, scheme_id, filled_slots)

        # Get scheme display name
        scheme_name = ""
        category_name = ""
        cat_data = CATEGORIES.get(cat, {})
        category_name = cat_data.get("name", cat)
        scheme_data = cat_data.get("schemes", {}).get(scheme_id, {})
        scheme_name = scheme_data.get("name", scheme_id)

        # Retrieve context for richer response
        context = retrieve(cat, f"{scheme_name} eligibility requirements")

        # Generate LLM response
        reply = generate_response(
            question=f"Check eligibility for {scheme_name}",
            context=context,
            eligibility_result=eligibility_result,
            intent="eligibility_check",
            scheme_name=scheme_name,
            category_name=category_name,
        )

        # Clear slot filling state
        state["active_slot_filling"] = False
        state["scheme_id"] = None
        SlotFiller.clear_session(session_id)

        return jsonify({
            "reply": reply,
            "state": "responding",
            "session_id": session_id,
        })

    # ----- Detect intent -----
    intent_result = detect_intent(message, state.get("category", category))
    detected_intent = intent_result["intent"]
    detected_scheme = intent_result["scheme"]
    detected_category = intent_result["category"] or state.get("category", category)

    # Update category from intent detection
    if detected_category:
        state["category"] = detected_category

    cat = state["category"]
    cat_data = CATEGORIES.get(cat, {})
    category_name = cat_data.get("name", cat)

    # ----- Eligibility check with scheme detected → start slot filling -----
    if detected_intent == "eligibility_check" and detected_scheme:
        scheme_data = cat_data.get("schemes", {}).get(detected_scheme)
        if scheme_data:
            scheme_name = scheme_data["name"]

            # Start slot filling
            try:
                SlotFiller.start_filling(session_id, detected_scheme, cat)
                state["active_slot_filling"] = True
                state["scheme_id"] = detected_scheme

                next_q = SlotFiller.get_next_question(session_id)
                if next_q:
                    intro = (
                        f"I'll help you check your eligibility for **{scheme_name}**. "
                        f"I need to ask you a few questions.\n\n{next_q}"
                    )
                    return jsonify({
                        "reply": intro,
                        "state": "collecting_slots",
                        "session_id": session_id,
                    })
            except ValueError:
                pass

    # ----- General flow: retrieve + generate -----
    scheme_name = ""
    if detected_scheme:
        scheme_data = cat_data.get("schemes", {}).get(detected_scheme, {})
        scheme_name = scheme_data.get("name", detected_scheme)

    # Retrieve relevant context
    query_for_retrieval = message
    if scheme_name:
        query_for_retrieval = f"{scheme_name} {message}"
    context = retrieve(cat, query_for_retrieval) if cat else ""

    # Generate response
    reply = generate_response(
        question=message,
        context=context,
        eligibility_result=None,
        intent=detected_intent,
        scheme_name=scheme_name,
        category_name=category_name,
    )

    return jsonify({
        "reply": reply,
        "state": "responding",
        "session_id": session_id,
    })


@app.route("/categories", methods=["GET"])
def get_categories():
    """Return all available categories for the frontend."""
    result = {}
    for cat_id, cat_info in CATEGORIES.items():
        result[cat_id] = {
            "name": cat_info["name"],
            "icon": cat_info["icon"],
            "description": cat_info["description"],
            "schemes": [
                {"id": sid, "name": sinfo["name"]}
                for sid, sinfo in cat_info["schemes"].items()
            ],
        }
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🚀 Citizen Services Assistant backend starting...")
    print("📡 API running at http://localhost:5000")
    print("📂 Available endpoints: POST /chat, GET /categories, GET /health")
    app.run(host="0.0.0.0", port=5000, debug=True)
