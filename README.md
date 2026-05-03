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
- `admin.py` — CLI for adding/listing/deleting rows and managing pending questions
- `ask.py` — one-shot wrapper that runs the agent on a single message
- `family.db` — SQLite file (gitignored, created on first run)

## Tools the agent has

- `search_personal_database(query)` — search across people, places, events, stories
- `add_pending_question(question)` — record an unknown for the family to answer
- `save_story(title, transcript)` — preserve a memory the user shares

## Adding data with `admin.py`

```bash
uv run python admin.py add-person --name "Aunt Mei" --relationship aunt --lives-in "Kuala Lumpur"
uv run python admin.py add-place --place "Cameron Highlands" --years 1980-1990 --significance "family holidays"
uv run python admin.py add-event --event "Sarah's graduation" --date 1995-05-20 --people-involved "Sarah, Helen"
uv run python admin.py add-story --title "First car" --transcript "I bought a beat-up Morris Minor in 1968..."

uv run python admin.py list people            # show all rows
uv run python admin.py delete people 5        # delete by id
uv run python admin.py pending                # show open pending questions
uv run python admin.py answer 3 --answer "Aunt Beatrice was your mother's youngest sister."
```

## Try these test prompts

- `Who is Sarah?` → should look up Sarah Lim and answer warmly
- `Where did I grow up?` → should pull Penang from places
- `When did I marry Helen?` → should find the 1972 wedding event
- `Who is Aunt Beatrice?` → not in DB; should escalate with the "let me check" reply
- `I was thinking about the time my father took me fishing in the river behind our house...` → should call `save_story`
