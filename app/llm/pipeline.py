"""
LLM pipeline for the Citizen Services Assistant.
Uses LangChain with Ollama (llama3) to generate contextual responses.
"""

from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


# Prompt template for the government services assistant
_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=[
        "context", "question", "eligibility_info",
        "intent", "scheme_name", "category_name",
    ],
    template="""You are a helpful Indian Government Citizen Services Assistant. Your role is to help citizens understand and access government schemes, services, and benefits.

Category: {category_name}
Scheme: {scheme_name}
User Intent: {intent}

Relevant Information:
{context}

Eligibility Information:
{eligibility_info}

User Question: {question}

Instructions:
- Answer in clear, simple English that any citizen can understand.
- Be accurate and helpful. Do not make up information.
- Structure your response with appropriate sections based on the user's intent:
  * For eligibility checks: Provide the eligibility result and explain the criteria.
  * For application steps: Provide a numbered list under "📝 Steps to Apply".
  * For document queries: List documents under "📄 Required Documents".
  * For office location queries: Provide information under "📍 Where to Apply".
  * For general queries: Provide a clear, concise answer.
- If the context does not contain enough information, say so honestly and suggest where the citizen can find more details.
- Always be polite and encouraging.

Response:""",
)


def generate_response(
    question: str,
    context: str,
    eligibility_result: dict | None,
    intent: str,
    scheme_name: str,
    category_name: str,
) -> str:
    """
    Generate a response using the LLM with context from RAG and eligibility check.

    Args:
        question: The user's question.
        context: Retrieved context from FAISS.
        eligibility_result: Dict with 'eligible' and 'message' keys, or None.
        intent: Detected intent string.
        scheme_name: Display name of the scheme.
        category_name: Display name of the category.

    Returns:
        The generated response string.
    """
    # Format eligibility info
    if eligibility_result:
        eligibility_info = eligibility_result.get("message", "No eligibility data available.")
    else:
        eligibility_info = "No eligibility check was performed."

    # Format context
    if not context:
        context = "No specific reference documents available for this query."

    # Build the prompt
    prompt_text = _PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        eligibility_info=eligibility_info,
        intent=intent,
        scheme_name=scheme_name or "General",
        category_name=category_name or "General",
    )

    try:
        llm = OllamaLLM(model="llama3")
        response = llm.invoke(prompt_text)
        return response.strip()
    except Exception as e:
        # Graceful fallback if Ollama is not running or model is unavailable
        fallback_parts = []
        fallback_parts.append(
            f"I'd be happy to help you with your query about **{scheme_name or category_name or 'government services'}**."
        )

        if eligibility_result:
            fallback_parts.append(f"\n\n**Eligibility Result:**\n{eligibility_result['message']}")

        if context and context != "No specific reference documents available for this query.":
            fallback_parts.append(f"\n\n**Relevant Information:**\n{context}")

        fallback_parts.append(
            "\n\n⚠️ *Note: The AI assistant is currently unavailable. "
            "The information above is based on our database. "
            "For the most accurate and up-to-date information, "
            "please visit the official government portal or your nearest "
            "Common Service Centre (CSC).*"
        )
        fallback_parts.append(f"\n\n_(Error details: {str(e)})_")

        return "".join(fallback_parts)
