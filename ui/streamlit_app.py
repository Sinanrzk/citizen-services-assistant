"""
Citizen Services Assistant — Streamlit Frontend
A redesigned app: Dashboard (clickable service tiles) + floating chatbot icon
→ Chat (conversational assistant per service).
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
# 2. Custom CSS — Complete redesign
# ──────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Design tokens — high contrast palette ── */
:root {
    --primary: #1D4ED8;
    --primary-light: #3B82F6;
    --primary-dark: #1E3A8A;
    --primary-bg: #EFF6FF;
    --accent: #D97706;
    --accent-light: #F59E0B;
    --accent-bg: #FFFBEB;
    --bg-main: #F8FAFC;
    --bg-card: #FFFFFF;
    --bg-chat-user: #FEF3C7;
    --bg-chat-assistant: #DBEAFE;
    --text-primary: #0F172A;
    --text-secondary: #374151;
    --text-muted: #6B7280;
    --text-chat-user: #92400E;
    --text-chat-assistant: #1E3A5F;
    --border-light: #E2E8F0;
    --border-card: #CBD5E1;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 25px rgba(0,0,0,0.12), 0 4px 10px rgba(0,0,0,0.08);
    --shadow-xl: 0 20px 40px rgba(0,0,0,0.15);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --radius-full: 9999px;
    --transition-fast: 0.15s ease;
    --transition-med: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global resets ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp, .main, .block-container {
    background-color: var(--bg-main) !important;
}

.stApp {
    background: linear-gradient(170deg, #EFF6FF 0%, var(--bg-main) 30%) !important;
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

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

/* ── Dashboard header ── */
.dashboard-header {
    text-align: center;
    padding: 2rem 1rem 0.5rem;
    margin-bottom: 1rem;
}

.dashboard-header h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: var(--primary-dark) !important;
    margin-bottom: 0.3rem !important;
    letter-spacing: -0.5px;
    line-height: 1.2 !important;
}

.dashboard-header .subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-top: 0;
}

/* ── Tile card — the visual label ── */
.tile-visual {
    pointer-events: none;
    position: relative;
    z-index: 5;
    background: #FFFFFF;
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.3rem 1.3rem;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-light);
    border-top: 4px solid var(--primary-light);
    transition: all var(--transition-med);
    margin-bottom: 0 !important;
}

.tile-visual .tile-icon {
    font-size: 2.6rem;
    margin-bottom: 0.6rem;
    display: block;
    line-height: 1;
}

.tile-visual .tile-name {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
    line-height: 1.3;
}

.tile-visual .tile-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
    font-weight: 400;
}

.tile-visual .tile-arrow {
    position: absolute;
    top: 1.2rem;
    right: 1.2rem;
    font-size: 1.2rem;
    color: var(--text-muted);
    opacity: 0;
    transition: all var(--transition-med);
}

/* ── The Streamlit button overlaid on the tile ── */
div[data-testid="stElementContainer"]:has(.tile-visual) + div[data-testid="stElementContainer"] {
    margin-top: -160px !important;
    position: relative !important;
    z-index: 10 !important;
}

div[data-testid="stElementContainer"]:has(.tile-visual) + div[data-testid="stElementContainer"] .stButton > button {
    width: 100% !important;
    height: 160px !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    font-size: 0 !important;
    cursor: pointer !important;
    box-shadow: none !important;
    border-radius: var(--radius-lg) !important;
    opacity: 0 !important;
}

div[data-testid="stElementContainer"]:has(.tile-visual) + div[data-testid="stElementContainer"] .stButton > button:hover,
div[data-testid="stElementContainer"]:has(.tile-visual) + div[data-testid="stElementContainer"] .stButton > button:focus,
div[data-testid="stElementContainer"]:has(.tile-visual) + div[data-testid="stElementContainer"] .stButton > button:active {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Hover effect on the visual card when button container is hovered */
.stColumn:hover .tile-visual {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-light);
}

.stColumn:hover .tile-visual .tile-arrow {
    opacity: 1;
    color: var(--primary);
}

.stColumn:active .tile-visual {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* ── Floating chatbot button ── */
div[data-testid="stElementContainer"]:has(#floating-chat-marker) + div[data-testid="stElementContainer"] {
    position: fixed !important;
    bottom: 2rem !important;
    right: 2rem !important;
    z-index: 9999 !important;
    width: auto !important;
}

div[data-testid="stElementContainer"]:has(#floating-chat-marker) + div[data-testid="stElementContainer"] .stButton > button {
    width: 64px !important;
    height: 64px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
    color: white !important;
    font-size: 28px !important;
    line-height: 1 !important;
    padding: 0 !important;
    box-shadow: var(--shadow-lg), 0 0 0 0 rgba(29, 78, 216, 0.4) !important;
    border: none !important;
    transition: all var(--transition-med) !important;
    animation: pulse-ring 2s ease infinite;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stElementContainer"]:has(#floating-chat-marker) + div[data-testid="stElementContainer"] .stButton > button:hover {
    transform: scale(1.1) !important;
    box-shadow: var(--shadow-xl) !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stElementContainer"]:has(#floating-chat-marker) + div[data-testid="stElementContainer"] .stButton > button p {
    font-size: 1.6rem !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}

@keyframes pulse-ring {
    0% { box-shadow: var(--shadow-lg), 0 0 0 0 rgba(29, 78, 216, 0.35); }
    70% { box-shadow: var(--shadow-lg), 0 0 0 12px rgba(29, 78, 216, 0); }
    100% { box-shadow: var(--shadow-lg), 0 0 0 0 rgba(29, 78, 216, 0); }
}

/* ── Chat popup panel ── */
.chat-popup-panel {
    position: fixed;
    bottom: 6.5rem;
    right: 2rem;
    z-index: 9998;
    width: 400px;
    max-height: 520px;
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--border-light);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.chat-popup-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: white;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.chat-popup-header .popup-icon { font-size: 1.5rem; line-height: 1; }
.chat-popup-header .popup-title { font-size: 1.05rem; font-weight: 700; }
.chat-popup-header .popup-subtitle { font-size: 0.8rem; opacity: 0.85; }

.chat-popup-body {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    max-height: 380px;
    background: var(--bg-main);
}

.popup-msg {
    margin-bottom: 0.6rem;
    display: flex;
}

.popup-msg-bot {
    justify-content: flex-start;
}

.popup-msg-user {
    justify-content: flex-end;
}

.popup-bubble {
    max-width: 85%;
    padding: 0.7rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.92rem;
    line-height: 1.55;
}

.popup-bubble-bot {
    background: var(--bg-chat-assistant);
    color: var(--text-chat-assistant);
    border-bottom-left-radius: 4px;
}

.popup-bubble-user {
    background: var(--bg-chat-user);
    color: var(--text-chat-user);
    border-bottom-right-radius: 4px;
}

/* ── Chat screen styles ── */
.chat-header-bar {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    border-radius: var(--radius-lg);
    margin-bottom: 1rem;
    box-shadow: var(--shadow-md);
}

.chat-header-bar .header-icon { font-size: 2rem; line-height: 1; }

.chat-header-bar .header-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: white !important;
    margin: 0;
    line-height: 1.3;
}

.chat-header-bar .header-hint {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.85);
    margin: 0;
}

/* ── Back button ── */
.back-btn-area .stButton > button {
    background: var(--bg-card) !important;
    color: var(--primary) !important;
    border: 2px solid var(--primary) !important;
    border-radius: var(--radius-full) !important;
    padding: 0.5rem 1.4rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 42px !important;
    cursor: pointer !important;
    transition: all var(--transition-fast) !important;
    box-shadow: var(--shadow-sm) !important;
}

.back-btn-area .stButton > button:hover {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}

/* ── Chat message bubbles — HIGH CONTRAST ── */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.4rem 0 !important;
    gap: 0.6rem !important;
    max-width: 100% !important;
}

/* === USER messages === */
/* Layout: right-aligned */
div[data-testid="stChatMessage"][data-chat-message-role="user"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
    padding-left: 15% !important;
}

/* User message content bubble */
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] {
    background: var(--bg-chat-user) !important;
    border: 1px solid #FCD34D !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 0.85rem 1.15rem !important;
    box-shadow: 0 2px 6px rgba(217, 119, 6, 0.1) !important;
}

/* User text color - robust selectors */
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"] li,
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"] span,
div[data-testid="stChatMessage"][data-chat-message-role="user"] div[data-testid="stChatMessageContent"] strong,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] li,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] span,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] strong {
    color: var(--text-chat-user) !important;
    font-size: 1.02rem !important;
    line-height: 1.65 !important;
}

/* User avatar */
div[data-testid="stChatMessageAvatar"]:has(div[data-testid="chatAvatarIcon-user"]),
div[data-testid="chatAvatarIcon-user"] {
    background-color: var(--accent) !important;
    border-radius: 50% !important;
}

/* === ASSISTANT messages === */
/* Layout: left-aligned */
div[data-testid="stChatMessage"][data-chat-message-role="assistant"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    padding-right: 10% !important;
}

/* Assistant message content bubble */
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] {
    background: var(--bg-chat-assistant) !important;
    border: 1px solid #93C5FD !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 0.85rem 1.15rem !important;
    box-shadow: 0 2px 6px rgba(29, 78, 216, 0.08) !important;
}

/* Assistant text color - robust selectors */
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"] li,
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"] span,
div[data-testid="stChatMessage"][data-chat-message-role="assistant"] div[data-testid="stChatMessageContent"] strong,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] li,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] span,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] strong {
    color: var(--text-chat-assistant) !important;
    font-size: 1.02rem !important;
    line-height: 1.65 !important;
}

/* Assistant avatar */
div[data-testid="stChatMessageAvatar"]:has(div[data-testid="chatAvatarIcon-assistant"]),
div[data-testid="chatAvatarIcon-assistant"] {
    background-color: var(--primary) !important;
    border-radius: 50% !important;
}

/* ── Chat input styling ── */
div[data-testid="stChatInput"] {
    border-radius: var(--radius-xl) !important;
    background: var(--bg-card) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border: 2px solid var(--border-light) !important;
    border-radius: var(--radius-xl) !important;
    padding: 0.75rem 1.1rem !important;
    transition: border-color var(--transition-fast) !important;
    min-height: 46px !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.12) !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

div[data-testid="stChatInput"] button {
    background: var(--primary) !important;
    color: white !important;
    border-radius: 50% !important;
    min-height: 42px !important;
    min-width: 42px !important;
    transition: all var(--transition-fast) !important;
}

div[data-testid="stChatInput"] button:hover {
    background: var(--primary-light) !important;
    transform: scale(1.08);
}

/* ── General button overrides ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: var(--radius-md) !important;
    transition: all var(--transition-fast) !important;
    min-height: 42px !important;
}

/* ── Quick-action chips on service page ── */
.quick-action-chip {
    display: inline-block;
    padding: 0.45rem 1rem;
    background: var(--primary-bg);
    color: var(--primary) !important;
    border: 1.5px solid var(--primary-light);
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast);
    margin: 0.25rem 0.3rem;
    text-decoration: none;
}

.quick-action-chip:hover {
    background: var(--primary);
    color: white !important;
    box-shadow: var(--shadow-sm);
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-light), transparent) !important;
    margin: 1.2rem 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(29, 78, 216, 0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(29, 78, 216, 0.35); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .dashboard-header h1 { font-size: 1.8rem !important; }
    .tile-card { min-height: 140px; padding: 1.2rem 1rem; }
    .chat-popup-panel { width: 92vw; right: 4vw; bottom: 5.5rem; }
    .floating-chat-btn { width: 54px; height: 54px; font-size: 1.5rem; bottom: 1.2rem; right: 1.2rem; }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) { padding-left: 5% !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) { padding-right: 5% !important; }
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.animate-in { animation: fadeInUp 0.4s ease-out both; }
.animate-slide { animation: slideUp 0.3s ease-out both; }

.anim-d1 { animation-delay: 0.05s; }
.anim-d2 { animation-delay: 0.10s; }
.anim-d3 { animation-delay: 0.15s; }
.anim-d4 { animation-delay: 0.20s; }
.anim-d5 { animation-delay: 0.25s; }
.anim-d6 { animation-delay: 0.30s; }
.anim-d7 { animation-delay: 0.35s; }
.anim-d8 { animation-delay: 0.40s; }
.anim-d9 { animation-delay: 0.45s; }
.anim-d10 { animation-delay: 0.50s; }
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
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False
if "popup_messages" not in st.session_state:
    st.session_state.popup_messages = []
if "popup_session_id" not in st.session_state:
    st.session_state.popup_session_id = str(uuid4())

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
            timeout=45,
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
    """Render the service-category tile grid with floating chatbot."""

    # Header
    st.markdown(
        """
        <div class="dashboard-header animate-in">
            <h1>🏛️ Citizen Services Assistant</h1>
            <p class="subtitle">Select a service to get started, or chat with our assistant below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render tiles in rows of 3 — unified clickable cards
    category_keys = list(CATEGORIES.keys())
    for row_start in range(0, len(category_keys), 3):
        row_keys = category_keys[row_start: row_start + 3]
        cols = st.columns([1, 1, 1])

        for idx, (col, cat_key) in enumerate(zip(cols, row_keys)):
            cat = CATEGORIES[cat_key]
            anim_idx = row_start + idx + 1
            anim_class = f"anim-d{min(anim_idx, 10)}"

            with col:
                st.markdown(
                    f"""<div class="tile-visual animate-in {anim_class}">
                            <span class="tile-icon">{cat['icon']}</span>
                            <div class="tile-name">{cat['name']}</div>
                            <div class="tile-desc">{cat['description']}</div>
                            <span class="tile-arrow">→</span>
                        </div>""",
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

    # ── Floating chatbot button (Functional) ──
    # We use an invisible marker to target the subsequent button container via CSS sibling selector
    st.markdown('<div id="floating-chat-marker" style="display:none;"></div>', unsafe_allow_html=True)
    btn_label = "✕" if st.session_state.show_popup else "💬"
    if st.button(btn_label, key="toggle_popup_float"):
        st.session_state.show_popup = not st.session_state.show_popup
        if st.session_state.show_popup and not st.session_state.popup_messages:
            _seed_popup_messages()
        st.rerun()

    # ── Chatbot popup window ──
    if st.session_state.show_popup:
        _render_popup_chat()


def _seed_popup_messages():
    """Add a welcome message to the popup chat with service listing."""
    cat_list_lines = []
    for i, (key, cat) in enumerate(CATEGORIES.items(), 1):
        cat_list_lines.append(f"**{i}. {cat['icon']} {cat['name']}** — {cat['description']}")

    greeting = (
        "👋 Hello! I'm your **Citizen Services Assistant**.\n\n"
        "I can help you navigate government services step by step. "
        "Here are the available categories:\n\n"
        + "\n".join(cat_list_lines)
        + "\n\n"
        "**Which service are you looking for?** Type the name or number, "
        "or describe what you need help with."
    )
    st.session_state.popup_messages = [{"role": "assistant", "content": greeting}]


def _render_popup_chat():
    """Render the popup chat UI at the bottom of the dashboard."""
    st.markdown("---")
    st.markdown(
        """<div class="animate-slide" style="margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem; padding: 0.8rem 1rem;
                 background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%);
                 border-radius: 12px 12px 0 0; color: white;">
                <span style="font-size: 1.4rem;">🤖</span>
                <div>
                    <div style="font-weight: 700; font-size: 1rem;">Citizen Services Assistant</div>
                    <div style="font-size: 0.78rem; opacity: 0.85;">Ask me anything about government services</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Render popup messages
    for msg in st.session_state.popup_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input for popup
    popup_input = st.chat_input("Type your question...", key="popup_chat_input")
    if popup_input:
        st.session_state.popup_messages.append({"role": "user", "content": popup_input})

        # Check if user typed a category number or name to redirect
        redirect_key = _match_category(popup_input)
        if redirect_key:
            cat = CATEGORIES[redirect_key]
            redirect_msg = (
                f"Great choice! Taking you to **{cat['icon']} {cat['name']}** now. "
                f"You'll be able to ask detailed questions about {cat['description']}."
            )
            st.session_state.popup_messages.append({"role": "assistant", "content": redirect_msg})
            st.session_state.screen = "chat"
            st.session_state.selected_category = redirect_key
            st.session_state.messages = []
            st.session_state.session_id = str(uuid4())
            st.session_state.show_popup = False
            st.rerun()
        else:
            # General question — send to backend without a category
            with st.chat_message("user"):
                st.markdown(popup_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = call_backend(
                        session_id=st.session_state.popup_session_id,
                        message=popup_input,
                        category="",
                    )
                st.markdown(reply)
            st.session_state.popup_messages.append({"role": "assistant", "content": reply})
            st.rerun()


def _match_category(user_input: str) -> str | None:
    """Try to match user input to a category by number or name."""
    text = user_input.strip().lower()

    # Match by number
    category_keys = list(CATEGORIES.keys())
    try:
        num = int(text)
        if 1 <= num <= len(category_keys):
            return category_keys[num - 1]
    except ValueError:
        pass

    # Match by name (fuzzy)
    for key, cat in CATEGORIES.items():
        if text in cat["name"].lower() or cat["name"].lower() in text or text in key:
            return key

    return None


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
    st.markdown('<div class="back-btn-area">', unsafe_allow_html=True)
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
        <div class="chat-header-bar animate-in">
            <span class="header-icon">{cat['icon']}</span>
            <div>
                <p class="header-title">{cat['name']}</p>
                <p class="header-hint">Ask me anything about {cat['description'].lower()}</p>
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
            "Here's what I can assist you with:\n"
            "- ✅ **Eligibility criteria** — check if you qualify\n"
            "- 📝 **How to apply** — step-by-step guidance\n"
            "- 📄 **Required documents** — what you need to prepare\n"
            "- 📍 **Office locations** — where to go\n\n"
            "**How can I assist you today?**"
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
