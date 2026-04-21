import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain_groq import ChatGroq
import langchain_community.llms
from breath_tools import get_pranayama_technique
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
    agent="zero-shot-react-description", # Better for modern LLMs
    verbose=True,
    handle_parsing_errors=True # Helps if the LLM makes a formatting mistake
)

# 5. The Test
print("🧘‍♂️ Breathwork Agent is thinking...")
response = agent.run("I am in Munich and feeling quite tired before my first yoga class. What technique should I use?")
print(f"\n✨ FINAL ADVICE: {response}")