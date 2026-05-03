# Family assistant — v1 (terminal)

Personal assistant for an elderly user. Answers questions about his own life
and family from a local SQLite database, and escalates unknown questions for
family follow-up.

This stage is local-only: terminal in, terminal out. WhatsApp comes later.

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Provide your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Seed the database with placeholder family data
uv run python seed.py

# 4. Start the chat
uv run python chat.py
```

## Files

- `db.py` — SQLite schema + connection helper
- `seed.py` — placeholder family data (replace with real data later)
- `tools.py` — tool implementations exposed to Claude
- `chat.py` — terminal chat loop with the agent
- `family.db` — SQLite file (gitignored, created on first run)

## Tools the agent has

- `search_personal_database(query)` — search across people, places, events, stories
- `add_pending_question(question)` — record an unknown for the family to answer
- `save_story(title, transcript)` — preserve a memory the user shares

## Try these test prompts

- `Who is Sarah?` → should look up Sarah Lim and answer warmly
- `Where did I grow up?` → should pull Penang from places
- `When did I marry Helen?` → should find the 1972 wedding event
- `Who is Aunt Beatrice?` → not in DB; should escalate with the "let me check" reply
- `I was thinking about the time my father took me fishing in the river behind our house...` → should call `save_story`
