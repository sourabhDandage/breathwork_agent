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