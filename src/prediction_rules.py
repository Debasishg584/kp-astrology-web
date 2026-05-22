# src/prediction_rules.py

"""
ULTRA-ADVANCED KP PREDICTION DATABASE
Matches 'pppp.xlsx' structure and 'Divya Drishti' Design Colors.
"""

# Spiritual Color Palette (Matches Previous Design)
HOUSE_COLORS = {
    1: "#E3F2FD", # 🟦 Blue
    2: "#FFE0B2", # 🟧 Orange
    3: "#FFF9C4", # 🟨 Yellow
    4: "#C8E6C9", # 🟩 Green
    5: "#BBDEFB", # 🟦 Blue
    6: "#FFCDD2", # 🟥 Red
    7: "#D7CCC8", # 🟫 Brown
    8: "#E1BEE7", # 🟪 Purple
    9: "#D7CCC8", # 🟫 Brown
    10: "#BBDEFB", # 🟦 Blue
    11: "#FFE0B2", # 🟧 Orange
    12: "#FFF9C4"  # 🟨 Yellow
}

# Data from your Excel Sheet
HOUSE_DATA = {
    1: {
        "Title": "🟦 1st House (Lagna) – Self House",
        "Significations": [
            "Self, physical body", "General health, immunity", 
            "Personality, appearance", "Vitality, strength", 
            "Head, brain", "Character & behavior", "Mindset, confidence"
        ],
        "Events": {
            "Longevity (Life Span)": ([1, 3, 8], [2, 7]),
            "Starting New Ventures": ([1, 11], [12]),
            "Success in Missions": ([1, 11], [12])
        },
        "Quantities": ["Number of new phases", "Body weight changes"]
    },
    2: {
        "Title": "🟧 2nd House – Wealth & Family House",
        "Significations": [
            "Wealth, earnings", "Bank balance, assets", 
            "Family, speech", "Food, face, mouth", "Family expansion"
        ],
        "Events": {
            "Money Gain": ([2, 6, 11], [12]),
            "Family Disputes": ([2, 8, 12], [11]),
            "Marriage (Family Addn)": ([2, 7, 11], [1, 6, 10]),
            "Second Marriage": ([2, 7, 11], [6])
        },
        "Quantities": ["Amount of money", "Number of bank accounts", "Number of children"]
    },
    3: {
        "Title": "🟨 3rd House – Courage, Brothers",
        "Significations": [
            "Younger siblings", "Courage, initiative", 
            "Communication, media", "Short travels", "Hobbies, skills"
        ],
        "Events": {
            "Job Joining (Effort)": ([3, 10], [12]),
            "Promotion (Self-made)": ([3, 10, 11], [12]),
            "Interview Success": ([3, 9], [8])
        },
        "Quantities": ["Number of siblings", "Attempts made", "Jobs changed"]
    },
    4: {
        "Title": "🟩 4th House – Comforts, Mother",
        "Significations": [
            "Mother", "Home, property, land", "Vehicles", 
            "Basic Education", "Mental peace", "Fixed assets"
        ],
        "Events": {
            "Buying Property": ([4, 11, 12], [3]),
            "Vehicle Purchase": ([4, 11, 12], [3]),
            "Education Success": ([4, 11], [3, 8]),
            "Immigration Support": ([4, 12], [3])
        },
        "Quantities": ["Number of properties", "Number of vehicles", "Number of relocations"]
    },
    5: {
        "Title": "🟦 5th House – Love, Children",
        "Significations": [
            "Children", "Love affairs", "Higher Education", 
            "Creativity", "Speculation (Lottery)"
        ],
        "Events": {
            "Love Marriage": ([5, 7, 11], [6, 12]),
            "Child Birth": ([2, 5, 11], [1, 4, 10]),
            "Lottery Win": ([2, 5, 8, 11], [12]),
            "Creative Success": ([5, 10, 11], [12])
        },
        "Quantities": ["Number of children", "Love affairs", "Educational degrees"]
    },
    6: {
        "Title": "🟥 6th House – Job, Disease, Enemy",
        "Significations": [
            "Job, service", "Loans, debts", "Diseases", 
            "Court cases", "Competition"
        ],
        "Events": {
            "Job Joining": ([6, 10], [5]),
            "Job Problems": ([6, 8], [5, 11]),
            "Divorce (Separation)": ([6, 10, 12], [7]),
            "Court Case": ([6, 8], [12]),
            "Loan Approval": ([6, 2, 11], [12])
        },
        "Quantities": ["Number of diseases", "Jobs held", "Court cases"]
    },
    7: {
        "Title": "🟫 7th House – Marriage & Partner",
        "Significations": [
            "Spouse", "Marriage", "Business partnership", 
            "Public dealings", "Marital harmony"
        ],
        "Events": {
            "Marriage": ([2, 7, 11], [1, 6, 10]),
            "Divorce/Separation": ([6, 10, 12], [7]),
            "Partnership Business": ([7, 10, 11], [6])
        },
        "Quantities": ["Number of marriages", "Relationships", "Partners"]
    },
    8: {
        "Title": "🟪 8th House – Death, Secrets",
        "Significations": [
            "Longevity", "Accidents, surgery", "Inheritance", 
            "Sudden events", "Occult"
        ],
        "Events": {
            "Accident": ([8, 12], [11]),
            "Surgery": ([8, 12], [11]),
            "Occult Rise": ([8, 9, 11], [2]),
            "Inheritance Gain": ([2, 8, 11], [5])
        },
        "Quantities": ["Intensity of danger", "Surgeries", "Sudden events"]
    },
    9: {
        "Title": "🟫 9th House – Luck, Father",
        "Significations": [
            "Luck, fortune", "Father", "Spirituality", 
            "Long travels", "Higher knowledge"
        ],
        "Events": {
            "Foreign Settlement": ([3, 9, 12], [2, 4]),
            "Religious Growth": ([9, 5], [8]),
            "Higher Education (PhD)": ([4, 9, 11], [3, 8])
        },
        "Quantities": ["Number of travels", "Mentors/Gurus"]
    },
    10: {
        "Title": "🟦 10th House – Career, Status",
        "Significations": [
            "Career, profession", "Fame, recognition", 
            "Promotions", "Government interactions"
        ],
        "Events": {
            "Job Joining": ([6, 10], [5]),
            "Promotion": ([10, 11], [5, 9]),
            "Business Success": ([7, 10, 11], [5]),
            "Public Reputation": ([1, 10], [12])
        },
        "Quantities": ["Promotions", "Professions", "Public recognitions"]
    },
    11: {
        "Title": "🟧 11th House – Gains, Fulfillment",
        "Significations": [
            "Gains", "Desires fulfilled", "Friend circle", 
            "Awards", "Income"
        ],
        "Events": {
            "Financial Success": ([2, 6, 11], [12]),
            "Social Rise": ([1, 11], [12]),
            "Wish Fulfillment": ([11], [12])
        },
        "Quantities": ["Amount of gains", "Friend circle size", "Awards"]
    },
    12: {
        "Title": "🟨 12th House – Loss, Foreign",
        "Significations": [
            "Loss, expenses", "Foreign residence", "Moksha", 
            "Hospital, Jail", "Isolation"
        ],
        "Events": {
            "Immigration": ([3, 9, 12], [2, 4]),
            "Foreign Settlement": ([3, 9, 12], [2, 4]),
            "Hospitalization": ([6, 8, 12], [1, 5, 11]),
            "Imprisonment": ([12, 8], [2, 4])
        },
        "Quantities": ["Separations", "Losses", "Foreign travels"]
    }
}