"""
Citizen Services Assistant — Streamlit Frontend
A two-screen app: Dashboard (service tiles) → Chat (conversational assistant).
Connects to Flask backend at http://localhost:5000/chat.
"""

import streamlit as st
import requests
from uuid import uuid4

# ──────────────────────────────────────────────
# 1. Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Citizen Services Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 2. Custom CSS — injected once at the top
# ──────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Design tokens ── */
:root {
    --primary-blue: #2C6E91;
    --primary-blue-light: #3A8BB5;
    --primary-blue-dark: #1E5270;
    --accent-amber: #F2A93B;
    --accent-amber-light: #F7C06A;
    --accent-amber-dark: #D4901E;
    --bg-off-white: #FAF8F3;
    --text-charcoal: #2B2B2B;
    --text-muted: #5A5A5A;
    --white: #FFFFFF;
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.10);
    --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.15);
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-med: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global resets ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--text-charcoal) !important;
}

/* App background */
.stApp, .main, .block-container {
    background-color: var(--bg-off-white) !important;
}

.stApp {
    background: linear-gradient(180deg, #F0F4F8 0%, var(--bg-off-white) 180px) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}

/* Reduce default top padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

/* ── Dashboard header ── */
.dashboard-header {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    margin-bottom: 1.5rem;
}

.dashboard-header h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: var(--primary-blue) !important;
    margin-bottom: 0.4rem !important;
    letter-spacing: -0.5px;
    line-height: 1.2 !important;
}

.dashboard-header .subtitle {
    font-size: 1.15rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-top: 0;
}

/* ── Tile card styling ── */
.tile-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 1.6rem 1.4rem;
    min-height: 168px;
    box-shadow: var(--shadow-sm);
    border: 1px solid rgba(44, 110, 145, 0.08);
    border-left: 5px solid var(--primary-blue);
    transition: transform var(--transition-med), box-shadow var(--transition-med), border-color var(--transition-fast);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 0.5rem;
}

.tile-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(44, 110, 145, 0.03) 0%, rgba(242, 169, 59, 0.03) 100%);
    opacity: 0;
    transition: opacity var(--transition-med);
    pointer-events: none;
}

.tile-card:hover::before {
    opacity: 1;
}

.tile-card:hover {
    transform: translateY(-4px) scale(1.015);
    box-shadow: var(--shadow-lg);
    border-left-color: var(--accent-amber);
}

.tile-card:active {
    transform: translateY(-1px) scale(0.99);
    box-shadow: var(--shadow-md);
}

.tile-card .tile-icon {
    font-size: 2.4rem;
    margin-bottom: 0.65rem;
    display: block;
    line-height: 1;
}

.tile-card .tile-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-charcoal);
    margin-bottom: 0.35rem;
    line-height: 1.3;
}

.tile-card .tile-desc {
    font-size: 0.92rem;
    color: var(--text-muted);
    line-height: 1.5;
    font-weight: 400;
}

/* The actual Streamlit button behind each tile */
.tile-btn-wrapper button[kind="secondary"],
.tile-btn-wrapper .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    font-size: 0 !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    height: 100% !important;
    min-height: 168px !important;
    cursor: pointer !important;
    z-index: 2;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: none !important;
}

.tile-btn-wrapper .stButton > button:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.tile-btn-wrapper .stButton > button:focus {
    outline: 3px solid var(--accent-amber) !important;
    outline-offset: 2px;
    background: transparent !important;
    box-shadow: none !important;
}

.tile-btn-wrapper .stButton > button:active {
    background: transparent !important;
}

.tile-btn-wrapper {
    position: relative;
}

/* ── Chat screen styles ── */
.chat-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.2rem 1.5rem;
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-light) 100%);
    border-radius: var(--radius-lg);
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow-md);
}

.chat-header .chat-icon {
    font-size: 2.2rem;
    line-height: 1;
}

.chat-header .chat-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--white) !important;
    margin: 0;
    line-height: 1.3;
}

.chat-header .chat-hint {
    font-size: 0.88rem;
    color: rgba(255, 255, 255, 0.8);
    margin: 0;
}

/* ── Back button ── */
.back-btn-container .stButton > button {
    background: var(--white) !important;
    color: var(--primary-blue) !important;
    border: 2px solid var(--primary-blue) !important;
    border-radius: var(--radius-xl) !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 44px !important;
    cursor: pointer !important;
    transition: all var(--transition-fast) !important;
    box-shadow: var(--shadow-sm) !important;
    line-height: 1.4 !important;
}

.back-btn-container .stButton > button:hover {
    background: var(--primary-blue) !important;
    color: var(--white) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateX(-2px);
}

.back-btn-container .stButton > button:active {
    transform: scale(0.97);
}

/* ── Chat message bubbles ── */
/* Override Streamlit chat message containers */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.3rem 0 !important;
    gap: 0.6rem !important;
    max-width: 100% !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
}

/* User messages — amber tinted, right side */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
    padding-left: 12% !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: linear-gradient(135deg, #FFF8EC 0%, #FEF0D6 100%) !important;
    border: 1px solid rgba(242, 169, 59, 0.2) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 2px 8px rgba(242, 169, 59, 0.1) !important;
    color: var(--text-charcoal) !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
}

/* User avatar */
div[data-testid="chatAvatarIcon-user"] {
    background-color: var(--accent-amber) !important;
    border-radius: 50% !important;
}

/* Assistant messages — blue tinted, left side */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    padding-right: 12% !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: linear-gradient(135deg, #EEF5FA 0%, #E0EEF6 100%) !important;
    border: 1px solid rgba(44, 110, 145, 0.12) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 2px 8px rgba(44, 110, 145, 0.08) !important;
    color: var(--text-charcoal) !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
}

/* Assistant avatar */
div[data-testid="chatAvatarIcon-assistant"] {
    background-color: var(--primary-blue) !important;
    border-radius: 50% !important;
}

/* ── Chat input styling ── */
div[data-testid="stChatInput"] {
    border-radius: var(--radius-xl) !important;
    background: var(--white) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    color: var(--text-charcoal) !important;
    background: var(--white) !important;
    border: 2px solid rgba(44, 110, 145, 0.15) !important;
    border-radius: var(--radius-xl) !important;
    padding: 0.8rem 1.2rem !important;
    transition: border-color var(--transition-fast) !important;
    min-height: 48px !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border-color: var(--primary-blue) !important;
    box-shadow: 0 0 0 3px rgba(44, 110, 145, 0.12) !important;
}

div[data-testid="stChatInput"] button {
    background: var(--primary-blue) !important;
    color: var(--white) !important;
    border-radius: 50% !important;
    min-height: 44px !important;
    min-width: 44px !important;
    transition: background var(--transition-fast), transform var(--transition-fast) !important;
}

div[data-testid="stChatInput"] button:hover {
    background: var(--primary-blue-light) !important;
    transform: scale(1.08);
}

/* ── General button overrides ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: var(--radius-md) !important;
    transition: all var(--transition-fast) !important;
    min-height: 44px !important;
}

/* ── Loading / spinner ── */
.loading-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #EEF5FA 0%, #E0EEF6 100%);
    border: 1px solid rgba(44, 110, 145, 0.12);
    border-radius: 18px 18px 18px 4px;
    margin: 0.5rem 0;
    max-width: 70%;
    box-shadow: 0 2px 8px rgba(44, 110, 145, 0.08);
}

.loading-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--primary-blue);
    animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dot:nth-child(2) { animation-delay: -0.16s; }
.loading-dot:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.4); opacity: 0.4; }
    40% { transform: scale(1); opacity: 1; }
}

.loading-text {
    font-size: 0.95rem;
    color: var(--text-muted);
    font-style: italic;
}

/* ── Error toast ── */
.error-banner {
    background: linear-gradient(135deg, #FFF0F0 0%, #FFE6E6 100%);
    border: 1px solid rgba(220, 53, 69, 0.25);
    border-left: 5px solid #DC3545;
    border-radius: var(--radius-md);
    padding: 1.1rem 1.4rem;
    margin: 0.8rem 0;
    font-size: 1rem;
    line-height: 1.5;
    color: #8B1A2B;
    box-shadow: var(--shadow-sm);
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(44, 110, 145, 0.15), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(44, 110, 145, 0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(44, 110, 145, 0.4); }

/* ── Responsive adjustments ── */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .dashboard-header h1 {
        font-size: 1.8rem !important;
    }

    .dashboard-header .subtitle {
        font-size: 1rem;
    }

    .tile-card {
        min-height: 130px;
        padding: 1.2rem 1rem;
    }

    .tile-card .tile-icon {
        font-size: 2rem;
    }

    .tile-card .tile-name {
        font-size: 1.1rem;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        padding-left: 4% !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        padding-right: 4% !important;
    }

    .chat-header .chat-title {
        font-size: 1.25rem;
    }
}

@media (max-width: 480px) {
    .dashboard-header h1 {
        font-size: 1.5rem !important;
    }

    .tile-card {
        min-height: 110px;
        padding: 1rem 0.9rem;
    }

    .tile-card .tile-name {
        font-size: 1rem;
    }

    .tile-card .tile-desc {
        font-size: 0.82rem;
    }
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: fadeInUp 0.45s ease-out both;
}

.animate-in-delay-1 { animation-delay: 0.06s; }
.animate-in-delay-2 { animation-delay: 0.12s; }
.animate-in-delay-3 { animation-delay: 0.18s; }
.animate-in-delay-4 { animation-delay: 0.24s; }
.animate-in-delay-5 { animation-delay: 0.30s; }
.animate-in-delay-6 { animation-delay: 0.36s; }
.animate-in-delay-7 { animation-delay: 0.42s; }
.animate-in-delay-8 { animation-delay: 0.48s; }
.animate-in-delay-9 { animation-delay: 0.54s; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 3. Session State Initialization
# ──────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = "dashboard"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ──────────────────────────────────────────────
# 4. Category Data
# ──────────────────────────────────────────────
CATEGORIES = {
    "agriculture": {
        "icon": "🌾",
        "name": "Agriculture",
        "description": "PM-KISAN, MGNREGA, Crop Insurance",
    },
    "health": {
        "icon": "🏥",
        "name": "Health",
        "description": "Ayushman Bharat, Janani Suraksha",
    },
    "education": {
        "icon": "📚",
        "name": "Education",
        "description": "NSP Scholarship, Mid-Day Meal",
    },
    "housing": {
        "icon": "🏠",
        "name": "Housing",
        "description": "PM Awas Yojana (PMAY)",
    },
    "employment": {
        "icon": "💼",
        "name": "Employment",
        "description": "PMKVY, Startup India",
    },
    "transport": {
        "icon": "🚗",
        "name": "Transport",
        "description": "Driving Licence, Vehicle RC",
    },
    "finance": {
        "icon": "🏦",
        "name": "Finance & Banking",
        "description": "PM Jan Dhan, Mudra Loan",
    },
    "legal": {
        "icon": "📋",
        "name": "Legal & Identity",
        "description": "Aadhaar, PAN Card, Voter ID",
    },
    "utilities": {
        "icon": "💡",
        "name": "Utilities",
        "description": "Ujjwala Yojana, Saubhagya",
    },
    "social_welfare": {
        "icon": "🤝",
        "name": "Social Welfare",
        "description": "NSAP Pension, Sukanya Samriddhi",
    },
}

FLASK_BACKEND_URL = "http://localhost:5000/chat"

# ──────────────────────────────────────────────
# 5. Helper — call Flask backend
# ──────────────────────────────────────────────

def call_backend(session_id: str, message: str, category: str) -> str:
    """Send a message to the Flask backend and return the assistant reply."""
    try:
        response = requests.post(
            FLASK_BACKEND_URL,
            json={
                "session_id": session_id,
                "message": message,
                "category": category,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", data.get("reply", "I'm sorry, I couldn't process that."))
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ I'm unable to reach the service right now. "
            "Please make sure the backend server is running and try again."
        )
    except requests.exceptions.Timeout:
        return (
            "⏳ The request timed out. The server might be busy — "
            "please try again in a moment."
        )
    except requests.exceptions.RequestException as exc:
        return f"⚠️ Something went wrong: {exc}"


# ──────────────────────────────────────────────
# 6. Dashboard Screen
# ──────────────────────────────────────────────

def render_dashboard():
    """Render the service-category tile grid."""

    # Header
    st.markdown(
        """
        <div class="dashboard-header animate-in">
            <h1>🏛️ Citizen Services Assistant</h1>
            <p class="subtitle">How can we help you today?&ensp;Select a service below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render tiles in rows of 3
    category_keys = list(CATEGORIES.keys())
    for row_start in range(0, len(category_keys), 3):
        row_keys = category_keys[row_start : row_start + 3]
        cols = st.columns([1, 1, 1])

        for col, cat_key in zip(cols, row_keys):
            cat = CATEGORIES[cat_key]
            delay_class = f"animate-in-delay-{row_start // 3 + 1}"

            with col:
                # Card visual + invisible button overlay
                st.markdown(
                    f"""
                    <div class="tile-btn-wrapper">
                        <div class="tile-card {delay_class}">
                            <span class="tile-icon">{cat['icon']}</span>
                            <div class="tile-name">{cat['name']}</div>
                            <div class="tile-desc">{cat['description']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    cat["name"],
                    key=f"tile_{cat_key}",
                    use_container_width=True,
                ):
                    st.session_state.screen = "chat"
                    st.session_state.selected_category = cat_key
                    st.session_state.messages = []
                    st.session_state.session_id = str(uuid4())
                    st.rerun()


# ──────────────────────────────────────────────
# 7. Chat Screen
# ──────────────────────────────────────────────

def render_chat():
    """Render the chat interface for the selected category."""

    cat_key = st.session_state.selected_category
    if cat_key is None or cat_key not in CATEGORIES:
        st.session_state.screen = "dashboard"
        st.rerun()
        return

    cat = CATEGORIES[cat_key]

    # ── Back button ──
    st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="back_btn"):
        st.session_state.screen = "dashboard"
        st.session_state.selected_category = None
        st.session_state.messages = []
        st.session_state.session_id = str(uuid4())
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chat header ──
    st.markdown(
        f"""
        <div class="chat-header animate-in">
            <span class="chat-icon">{cat['icon']}</span>
            <div>
                <p class="chat-title">{cat['name']}</p>
                <p class="chat-hint">Ask me anything about {cat['description'].lower()}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Seed the conversation with a greeting if empty ──
    if not st.session_state.messages:
        greeting = (
            f"👋 Welcome to **{cat['name']}** services! "
            f"I can help you with information about **{cat['description']}**.\n\n"
            "Feel free to ask me:\n"
            "- Eligibility criteria\n"
            "- How to apply\n"
            "- Required documents\n"
            "- Status tracking\n\n"
            "How can I assist you today?"
        )
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # ── Render existing messages ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Chat input ──
    user_input = st.chat_input("Type your question here…")

    if user_input:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Show thinking indicator, call backend, display response
        with st.chat_message("assistant"):
            with st.spinner("Looking that up for you…"):
                reply = call_backend(
                    session_id=st.session_state.session_id,
                    message=user_input,
                    category=cat_key,
                )
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


# ──────────────────────────────────────────────
# 8. Main Router
# ──────────────────────────────────────────────

if st.session_state.screen == "dashboard":
    render_dashboard()
else:
    render_chat()
