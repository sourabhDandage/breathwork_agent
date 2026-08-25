def get_pranayama_technique(user_input: str):
    # Convert input to lowercase to be safe
    text = user_input.lower()
    
    database = {
        "stressed": "Nadi Shodhana (Alternate Nostril Breathing). It balances the nervous system.",
        "tired": "Bhastrika (Bellows Breath). It increases vital energy (Prana).",
        "anxious": "Bhramari (Humming Bee Breath). It calms the mind instantly."
    }
    
    # Check if any of our keywords are IN the text sent by the AI
    for mood in database:
        if mood in text:
            return database[mood]
            
    return "Deep Belly Breathing for general awareness."


def get_pranayama_for_heart_rate(bpm: int) -> str:
    """Choose a conservative practice from the latest heart-rate reading."""
    if bpm >= 100:
        mood = "stressed"
    elif bpm < 60:
        mood = "tired"
    else:
        mood = "anxious"
    return get_pranayama_technique(mood)


PRACTICES = {
    "nadi_shodhana": {
        "name": "Nadi Shodhana",
        "description": "Alternate nostril breathing to balance the nervous system.",
        "phases": [("Inhale", 4), ("Exhale", 6)],
    },
    "bhastrika": {
        "name": "Bhastrika",
        "description": "A gently energizing bellows breath. Stop if you feel dizzy or unwell.",
        "phases": [("Inhale", 2), ("Exhale", 2)],
    },
    "bhramari": {
        "name": "Bhramari",
        "description": "A settling humming breath with a longer, softer exhale.",
        "phases": [("Inhale", 4), ("Hum out", 6)],
    },
    "box_breathing": {
        "name": "Box Breathing",
        "description": "An even four-part rhythm: inhale, hold, exhale, hold.",
        "phases": [("Inhale", 4), ("Hold", 4), ("Exhale", 4), ("Hold", 4)],
    },
}


def get_practice_for_heart_rate(bpm: int):
    """Return a structured practice suitable for the current heart rate."""
    if bpm >= 100:
        return PRACTICES["nadi_shodhana"]
    if bpm < 60:
        return PRACTICES["bhastrika"]
    if bpm < 80:
        return PRACTICES["box_breathing"]
    return PRACTICES["bhramari"]