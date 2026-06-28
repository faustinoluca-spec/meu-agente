# WhatsApp News Agent 🤖

AI agent that automatically sends daily political, economic, electoral and cultural news briefings via WhatsApp.

## What it does

Runs daily at 8pm and sends curated news analysis to a list of WhatsApp contacts across 4 categories:
- 🏛️ Politics
- 💰 Economy  
- 🗳️ Elections
- 🎭 Culture & Entertainment

Each briefing includes key facts, context, multiple perspectives and forward-looking analysis — sourced from G1, UOL and CNN Brasil.

## Tech Stack

- **LLM:** Groq (llama-3.3-70b-versatile)
- **Search:** Serper API (Google News)
- **Messaging:** Twilio WhatsApp API
- **Scheduling:** Railway cron job

## Environment Variables

```env
GROQ_KEY=
SERPER_KEY=
TWILIO_SID=
TWILIO_TOKEN=
WHATSAPP_NUMEROS=whatsapp:+55...,whatsapp:+55...
```

## Author

Luca Faustino — AI Engineer
