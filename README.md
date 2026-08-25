p# agentic-hatha-flow
Idea: Why not build an agent that suggests Pranayama routines based on the user's stress levels? It combines your two worlds!
"An autonomous AI Agent built to bridge traditional Indian Yoga wisdom with modern LLM capabilities. This agent uses Reasoning and Acting (ReAct) loops to curate personalized breathwork sessions."

## Agent Capabilities
Tool Use: Can search a local database of Hatha Yoga poses.

Reasoning: Uses LangChain to determine if a user needs calming or energizing Pranayama.

## Garmin tracking

The hourly tracker uses the `python-garminconnect` wrapper to read Garmin
Connect data and stores refreshed tokens in `~/.garminconnect`.

Set these environment variables in `.env`:

```env
GARMIN_PROVIDER=garminconnect
GARMIN_TOKENSTORE=~/.garminconnect
GARMIN_POLL_INTERVAL_SECONDS=3600
```

Run `python3 webapp.py`; click Connect Garmin and enter your Garmin credentials
in the local form. The wrapper supports MFA in the terminal when needed, caches
tokens, and fetches today's heart-rate
samples. The dashboard polls once immediately and then every hour. Heart rates
of 100 bpm or higher suggest calming Nadi Shodhana, readings below 60 bpm
suggest energizing Bellows Breath, and other readings suggest Bhramari.

The wrapper requires Python 3.12 or later. This repository includes a dedicated
`.venv-garmin` environment. Start the app with
`.venv-garmin/bin/python webapp.py`. Never commit `.env` or your Garmin
password into `.env`. The token store contains persistent account access and
should remain owner-only. Do not put your Garmin password into `.env`.

Copy `.env.example` to `.env` and restart the webapp. Never commit `.env`.
Since API keys were previously present in the
local `.env`, rotate those keys in their provider dashboards before continuing.
