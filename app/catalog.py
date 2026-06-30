"""
Service Catalog: Categories, Schemes, Eligibility Rules, and Slot Questions
for the Citizen Services Assistant.
"""

CATEGORIES = {
    "agriculture": {
        "name": "Agriculture",
        "icon": "🌾",
        "description": "Farm support schemes including PM-KISAN, MGNREGA, and Crop Insurance.",
        "schemes": {
            "pm_kisan": {
                "name": "PM-KISAN",
                "required_slots": [
                    {"slot": "land_acres", "type": "float", "description": "Land owned in acres"},
                    {"slot": "category", "type": "str", "description": "Caste category (SC/ST/General)"},
                    {"slot": "state", "type": "str", "description": "State of residence"},
                ],
                "eligibility_rule": lambda slots: float(slots.get("land_acres", 999)) <= 5,
            },
            "mgnrega": {
                "name": "MGNREGA",
                "required_slots": [
                    {"slot": "rural_resident", "type": "bool", "description": "Whether you live in a rural area"},
                    {"slot": "has_job_card", "type": "bool", "description": "Whether you have a job card"},
                ],
                "eligibility_rule": lambda slots: bool(slots.get("rural_resident")) and bool(slots.get("has_job_card")),
            },
            "crop_insurance": {
                "name": "Crop Insurance (PMFBY)",
                "required_slots": [
                    {"slot": "is_farmer", "type": "bool", "description": "Whether you are a farmer"},
                    {"slot": "has_crop", "type": "bool", "description": "Whether you have a standing crop"},
                ],
                "eligibility_rule": lambda slots: bool(slots.get("is_farmer")) and bool(slots.get("has_crop")),
            },
        },
    },
    "health": {
        "name": "Health",
        "icon": "🏥",
        "description": "Healthcare schemes including Ayushman Bharat and Janani Suraksha Yojana.",
        "schemes": {
            "ayushman_bharat": {
                "name": "Ayushman Bharat (PMJAY)",
                "required_slots": [
                    {"slot": "annual_income", "type": "float", "description": "Annual household income in INR"},
                    {"slot": "family_size", "type": "int", "description": "Number of family members"},
                ],
                "eligibility_rule": lambda slots: float(slots.get("annual_income", 999999999)) < 300000,
            },
            "janani_suraksha": {
                "name": "Janani Suraksha Yojana",
                "required_slots": [
                    {"slot": "is_pregnant", "type": "bool", "description": "Whether you are pregnant"},
                    {"slot": "is_bpl", "type": "bool", "description": "Whether you are below poverty line"},
                ],
                "eligibility_rule": lambda slots: bool(slots.get("is_pregnant")) and bool(slots.get("is_bpl")),
            },
        },
    },
    "education": {
        "name": "Education",
        "icon": "📚",
        "description": "Education support including National Scholarship Portal, scholarships, and fellowships.",
        "schemes": {
            "nsp_scholarship": {
                "name": "National Scholarship Portal (NSP)",
                "required_slots": [
                    {"slot": "annual_income", "type": "float", "description": "Annual household income in INR"},
                    {"slot": "caste_category", "type": "str", "description": "Caste category (SC/ST/OBC/General)"},
                    {"slot": "percentage", "type": "float", "description": "Academic percentage scored"},
                ],
                "eligibility_rule": lambda slots: (
                    float(slots.get("annual_income", 999999999)) < 250000
                    and float(slots.get("percentage", 0)) >= 50
                ),
            },
        },
    },
    "housing": {
        "name": "Housing",
        "icon": "🏠",
        "description": "Housing schemes including Pradhan Mantri Awas Yojana (PMAY) for affordable housing.",
        "schemes": {
            "pmay": {
                "name": "Pradhan Mantri Awas Yojana (PMAY)",
                "required_slots": [
                    {"slot": "annual_income", "type": "float", "description": "Annual household income in INR"},
                    {"slot": "owns_house", "type": "bool", "description": "Whether you own a pucca house"},
                    {"slot": "category", "type": "str", "description": "Income category (EWS/LIG/MIG)"},
                ],
                "eligibility_rule": lambda slots: (
                    not bool(slots.get("owns_house"))
                    and float(slots.get("annual_income", 999999999)) < 1800000
                ),
            },
        },
    },
    "employment": {
        "name": "Employment",
        "icon": "💼",
        "description": "Skill development and employment schemes including PMKVY and job portals.",
        "schemes": {
            "pmkvy": {
                "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
                "required_slots": [
                    {"slot": "age", "type": "int", "description": "Your age in years"},
                    {"slot": "education_level", "type": "str", "description": "Highest education level (e.g. 10th/12th/Graduate)"},
                ],
                "eligibility_rule": lambda slots: 15 <= int(slots.get("age", 0)) <= 45,
            },
        },
    },
    "transport": {
        "name": "Transport",
        "icon": "🚗",
        "description": "Transport services including Driving Licence, vehicle registration, and permits.",
        "schemes": {
            "driving_licence": {
                "name": "Driving Licence",
                "required_slots": [
                    {"slot": "age", "type": "int", "description": "Your age in years"},
                    {"slot": "has_address_proof", "type": "bool", "description": "Whether you have address proof"},
                ],
                "eligibility_rule": lambda slots: (
                    int(slots.get("age", 0)) >= 18
                    and bool(slots.get("has_address_proof"))
                ),
            },
        },
    },
    "finance": {
        "name": "Finance",
        "icon": "💰",
        "description": "Financial inclusion schemes including PM Jan Dhan Yojana and Mudra Loan.",
        "schemes": {
            "pmjdy": {
                "name": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
                "required_slots": [
                    {"slot": "age", "type": "int", "description": "Your age in years"},
                    {"slot": "has_bank_account", "type": "bool", "description": "Whether you have a bank account"},
                ],
                "eligibility_rule": lambda slots: (
                    int(slots.get("age", 0)) >= 10
                    and not bool(slots.get("has_bank_account"))
                ),
            },
            "mudra_loan": {
                "name": "Mudra Loan (PMMY)",
                "required_slots": [
                    {"slot": "is_business_owner", "type": "bool", "description": "Whether you own or plan to start a business"},
                    {"slot": "loan_amount", "type": "float", "description": "Loan amount required in INR"},
                ],
                "eligibility_rule": lambda slots: (
                    bool(slots.get("is_business_owner"))
                    and float(slots.get("loan_amount", 999999999)) <= 1000000
                ),
            },
        },
    },
    "legal": {
        "name": "Legal & Identity",
        "icon": "⚖️",
        "description": "Identity and legal documents including Aadhaar, PAN Card, and Voter ID.",
        "schemes": {
            "aadhaar": {
                "name": "Aadhaar Card",
                "required_slots": [
                    {"slot": "is_resident", "type": "bool", "description": "Whether you are a resident of India"},
                ],
                "eligibility_rule": lambda slots: bool(slots.get("is_resident")),
            },
            "pan_card": {
                "name": "PAN Card",
                "required_slots": [
                    {"slot": "has_identity_proof", "type": "bool", "description": "Whether you have valid identity proof"},
                ],
                "eligibility_rule": lambda slots: bool(slots.get("has_identity_proof")),
            },
            "voter_id": {
                "name": "Voter ID (EPIC)",
                "required_slots": [
                    {"slot": "age", "type": "int", "description": "Your age in years"},
                    {"slot": "is_citizen", "type": "bool", "description": "Whether you are an Indian citizen"},
                ],
                "eligibility_rule": lambda slots: (
                    int(slots.get("age", 0)) >= 18
                    and bool(slots.get("is_citizen"))
                ),
            },
        },
    },
    "utilities": {
        "name": "Utilities",
        "icon": "🔌",
        "description": "Utility schemes including Ujjwala Yojana for LPG connections and electricity subsidy.",
        "schemes": {
            "ujjwala_yojana": {
                "name": "Pradhan Mantri Ujjwala Yojana",
                "required_slots": [
                    {"slot": "is_bpl", "type": "bool", "description": "Whether you are below poverty line"},
                    {"slot": "has_lpg_connection", "type": "bool", "description": "Whether you already have an LPG connection"},
                ],
                "eligibility_rule": lambda slots: (
                    bool(slots.get("is_bpl"))
                    and not bool(slots.get("has_lpg_connection"))
                ),
            },
        },
    },
    "social_welfare": {
        "name": "Social Welfare",
        "icon": "🤝",
        "description": "Social welfare schemes including NSAP Pension, widow pension, and disability support.",
        "schemes": {
            "nsap_pension": {
                "name": "National Social Assistance Programme (NSAP) Pension",
                "required_slots": [
                    {"slot": "age", "type": "int", "description": "Your age in years"},
                    {"slot": "is_bpl", "type": "bool", "description": "Whether you are below poverty line"},
                ],
                "eligibility_rule": lambda slots: (
                    int(slots.get("age", 0)) >= 60
                    and bool(slots.get("is_bpl"))
                ),
            },
        },
    },
}

SLOT_QUESTIONS = {
    "land_acres": "How many acres of land do you own?",
    "category": "What is your caste category? (SC/ST/General)",
    "state": "Which state do you reside in?",
    "rural_resident": "Do you live in a rural area? (yes/no)",
    "has_job_card": "Do you have a job card? (yes/no)",
    "is_farmer": "Are you a farmer? (yes/no)",
    "has_crop": "Do you have a standing crop? (yes/no)",
    "annual_income": "What is your annual household income in INR?",
    "family_size": "How many members are there in your family?",
    "is_pregnant": "Are you pregnant? (yes/no)",
    "is_bpl": "Are you below the poverty line (BPL)? (yes/no)",
    "caste_category": "What is your caste category? (SC/ST/OBC/General)",
    "percentage": "What is your academic percentage?",
    "owns_house": "Do you own a pucca house? (yes/no)",
    "age": "What is your age in years?",
    "education_level": "What is your highest education level? (e.g. 10th/12th/Graduate)",
    "has_address_proof": "Do you have a valid address proof? (yes/no)",
    "has_bank_account": "Do you already have a bank account? (yes/no)",
    "is_business_owner": "Do you own or plan to start a business? (yes/no)",
    "loan_amount": "What loan amount do you require (in INR)?",
    "is_resident": "Are you a resident of India? (yes/no)",
    "has_identity_proof": "Do you have valid identity proof? (yes/no)",
    "is_citizen": "Are you an Indian citizen? (yes/no)",
    "has_lpg_connection": "Do you already have an LPG connection? (yes/no)",
}