import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain_groq import ChatGroq
import langchain_community.llms
from breath_tools import get_pranayama_technique
from breath_tools import get_pranayama_for_heart_rate
from garmin_client import GarminError, fetch_heart_rate, login_with_garmin
from langchain_community.llms import Ollama
import os
from pathlib import Path
from dotenv import load_dotenv


# 1. Load the key
load_dotenv()

# 2. Define the Tool (the "Hands")
tools = [
    Tool(
        name="PranayamaSelector",
        func=get_pranayama_technique,
        # We add explicit instructions here so the LLM knows what to send
        description="""Use this tool to get a breathing technique. 
        The input should be a single word representing the mood, 
        specifically: 'stressed', 'tired', or 'anxious'."""
    )
]

# 3. Setup the Brain (the "Mind")
# We use temperature 0 because we want the agent to be precise, not "creative" with instructions



llm = langchain_community.llms.Ollama(model="llama3")

# 4. Initialize the Agent (the "Reasoning")
from langchain.agents import AgentType

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
)


def suggest_from_garmin() -> None:
    """Fetch heart rate and print one hourly recommendation."""
    try:
        reading = fetch_heart_rate()
    except GarminError as error:
        print(f"Garmin tracking error: {error}")
        return

    advice = get_pranayama_for_heart_rate(reading.bpm)
    stamp = f" at {reading.timestamp}" if reading.timestamp else ""
    print(f"Heart rate: {reading.bpm} bpm{stamp}")
    print(f"Hourly pranayama suggestion: {advice}")


def run_hourly_tracking() -> None:
    """Poll Garmin once per hour until the process is stopped."""
    interval = int(os.getenv("GARMIN_POLL_INTERVAL_SECONDS", "3600"))
    if interval < 60:
        raise ValueError("GARMIN_POLL_INTERVAL_SECONDS must be at least 60")
    while True:
        suggest_from_garmin()
        time.sleep(interval)


if __name__ == "__main__":
    if os.getenv("GARMIN_LOGIN", "false").lower() == "true":
        login_with_garmin()
    elif os.getenv("GARMIN_TRACKING_ENABLED", "false").lower() == "true":
        run_hourly_tracking()
    else:
        print("Breathwork Agent is thinking...")
        response = agent.run(
            "I am in Munich and feeling quite tired before my first yoga class. "
            "What technique should I use?"
        )
        print(f"\nFINAL ADVICE: {response}")