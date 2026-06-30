"""
Slot Filler: Manages multi-turn slot collection for eligibility checks.
Tracks per-session state for which slots have been filled and which remain.
"""

from app.catalog import CATEGORIES, SLOT_QUESTIONS


class SlotFiller:
    """
    Manages conversational slot-filling sessions.
    Each session tracks the scheme being checked, which slots are filled,
    and which are still pending.
    """

    # Class-level session store: session_id -> session data dict
    _sessions: dict = {}

    @classmethod
    def start_filling(cls, session_id: str, scheme_id: str, category: str) -> None:
        """
        Initialize a slot-filling session for a given scheme.

        Args:
            session_id: Unique session identifier.
            scheme_id: The scheme to collect slots for.
            category: The category the scheme belongs to.
        """
        cat_data = CATEGORIES.get(category)
        if not cat_data:
            raise ValueError(f"Unknown category: {category}")

        scheme_data = cat_data["schemes"].get(scheme_id)
        if not scheme_data:
            raise ValueError(f"Unknown scheme '{scheme_id}' in category '{category}'")

        required_slots = scheme_data["required_slots"]
        pending = [slot_info.copy() for slot_info in required_slots]

        cls._sessions[session_id] = {
            "scheme_id": scheme_id,
            "category": category,
            "filled_slots": {},
            "pending_slots": pending,
        }

    @classmethod
    def process_answer(cls, session_id: str, answer: str) -> None:
        """
        Process the user's answer for the next pending slot.
        Parses the answer to the appropriate type (int, float, bool, str).

        Args:
            session_id: The session to process.
            answer: The user's raw text answer.
        """
        session = cls._sessions.get(session_id)
        if not session or not session["pending_slots"]:
            return

        next_slot = session["pending_slots"][0]
        slot_name = next_slot["slot"]
        slot_type = next_slot["type"]

        parsed_value = cls._parse_value(answer.strip(), slot_type)
        session["filled_slots"][slot_name] = parsed_value
        session["pending_slots"].pop(0)

    @classmethod
    def get_next_question(cls, session_id: str) -> str | None:
        """
        Get the next question to ask the user, or None if all slots are filled.

        Args:
            session_id: The session to query.

        Returns:
            A human-friendly question string, or None.
        """
        session = cls._sessions.get(session_id)
        if not session or not session["pending_slots"]:
            return None

        next_slot = session["pending_slots"][0]
        slot_name = next_slot["slot"]
        return SLOT_QUESTIONS.get(slot_name, f"Please provide your {slot_name}:")

    @classmethod
    def get_filled_slots(cls, session_id: str) -> dict:
        """
        Return the dict of slots filled so far.

        Args:
            session_id: The session to query.

        Returns:
            Dict mapping slot_name -> parsed value.
        """
        session = cls._sessions.get(session_id)
        if not session:
            return {}
        return dict(session["filled_slots"])

    @classmethod
    def is_complete(cls, session_id: str) -> bool:
        """
        Check if all required slots have been filled.

        Args:
            session_id: The session to query.

        Returns:
            True if no pending slots remain.
        """
        session = cls._sessions.get(session_id)
        if not session:
            return False
        return len(session["pending_slots"]) == 0

    @classmethod
    def get_session(cls, session_id: str) -> dict | None:
        """
        Retrieve the full session data.

        Args:
            session_id: The session to retrieve.

        Returns:
            Session dict or None.
        """
        return cls._sessions.get(session_id)

    @classmethod
    def clear_session(cls, session_id: str) -> None:
        """
        Remove all session data for the given session_id.

        Args:
            session_id: The session to clear.
        """
        cls._sessions.pop(session_id, None)

    @staticmethod
    def _parse_value(raw: str, slot_type: str):
        """
        Parse a raw string answer into the expected Python type.

        Args:
            raw: The raw text input from the user.
            slot_type: One of 'int', 'float', 'bool', 'str'.

        Returns:
            The parsed value.
        """
        lower = raw.lower().strip()

        if slot_type == "bool":
            truthy = {"yes", "y", "true", "1", "yeah", "yep", "haan", "ha"}
            falsy = {"no", "n", "false", "0", "nope", "nahi", "na"}
            if lower in truthy:
                return True
            if lower in falsy:
                return False
            # Default: try to interpret as truthy
            return bool(lower)

        if slot_type == "int":
            # Strip commas and try to parse
            cleaned = lower.replace(",", "").replace(" ", "")
            try:
                return int(float(cleaned))
            except (ValueError, TypeError):
                return 0

        if slot_type == "float":
            cleaned = lower.replace(",", "").replace(" ", "")
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0

        # Default: string type
        return raw.strip()
