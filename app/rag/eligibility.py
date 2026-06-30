"""
Eligibility checker for the Citizen Services Assistant.
Evaluates eligibility rules defined in the service catalog.
"""

from app.catalog import CATEGORIES


def check_eligibility(category: str, scheme_id: str, slots: dict) -> dict:
    """
    Check whether a user is eligible for a given scheme based on their slot values.

    Args:
        category: The service category (e.g. 'agriculture').
        scheme_id: The scheme identifier (e.g. 'pm_kisan').
        slots: Dict of slot_name -> value, collected from the user.

    Returns:
        Dict with:
            - eligible (bool): Whether the user meets the eligibility criteria.
            - message (str): A human-friendly explanation of the result.
    """
    cat_data = CATEGORIES.get(category)
    if not cat_data:
        return {
            "eligible": False,
            "message": f"Sorry, I could not find the category '{category}'. "
                       "Please check and try again.",
        }

    scheme_data = cat_data["schemes"].get(scheme_id)
    if not scheme_data:
        return {
            "eligible": False,
            "message": f"Sorry, I could not find the scheme '{scheme_id}' "
                       f"under the '{cat_data['name']}' category.",
        }

    scheme_name = scheme_data["name"]
    rule = scheme_data["eligibility_rule"]

    try:
        is_eligible = rule(slots)
    except Exception as e:
        return {
            "eligible": False,
            "message": f"An error occurred while checking eligibility for "
                       f"{scheme_name}: {str(e)}. Please verify your inputs.",
        }

    if is_eligible:
        # Build a summary of the user's provided details
        details_lines = []
        for slot_info in scheme_data["required_slots"]:
            slot_name = slot_info["slot"]
            value = slots.get(slot_name, "N/A")
            if isinstance(value, bool):
                value = "Yes" if value else "No"
            details_lines.append(f"  • {slot_info['description']}: {value}")
        details_str = "\n".join(details_lines)

        return {
            "eligible": True,
            "message": (
                f"✅ Great news! Based on the information you provided, "
                f"you appear to be **eligible** for **{scheme_name}**.\n\n"
                f"Your details:\n{details_str}\n\n"
                f"You can proceed with the application process."
            ),
        }
    else:
        # Provide a helpful not-eligible message
        details_lines = []
        for slot_info in scheme_data["required_slots"]:
            slot_name = slot_info["slot"]
            value = slots.get(slot_name, "N/A")
            if isinstance(value, bool):
                value = "Yes" if value else "No"
            details_lines.append(f"  • {slot_info['description']}: {value}")
        details_str = "\n".join(details_lines)

        return {
            "eligible": False,
            "message": (
                f"❌ Based on the information you provided, "
                f"you **do not appear to be eligible** for **{scheme_name}** "
                f"at this time.\n\n"
                f"Your details:\n{details_str}\n\n"
                f"Please verify your details or explore other schemes that "
                f"may be suitable for you."
            ),
        }
