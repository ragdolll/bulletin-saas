# Family assistant — session notes

Personal assistant for an elderly user. Local-only terminal v1.
Branch: `claude/whatsapp-family-assistant-yzOM5`. WhatsApp comes later.

## Project layout

- `db.py` — SQLite schema (people, places, events, stories, pending_questions)
- `seed.py` — wipes the four content tables and reloads placeholder family data; preserves `pending_questions`
- `tools.py` — tool implementations + JSON schemas exposed to Claude (`search_personal_database`, `add_pending_question`, `save_story`)
- `chat.py` — readline loop. `MODEL = "claude-sonnet-4-6"`. Manual agentic loop in `run_agent`. Each call starts a fresh `messages` list — no cross-turn history.
- `ask.py` — one-shot wrapper around `run_agent`. Used to relay single messages from the Claude Code chat into the agent (`uv run python ask.py "<message>"`).
- `admin.py` — CLI for adding/listing/deleting rows and managing pending questions. Subcommands: `add-person`, `add-place`, `add-event`, `add-story`, `list <table>`, `delete <table> <id>`, `pending`, `answer <id> --answer "..."`.
- `family.db` — SQLite file, gitignored
- `.claude/settings.local.json` — gitignored, holds `ANTHROPIC_API_KEY` in `env`

## Running

```bash
uv run python seed.py
uv run python chat.py        # interactive
uv run python ask.py "hi"    # one-shot
```

## Resume checklist (next session)

1. **Set the API key.** User is still figuring out the secure path. Options, in order of preference:
   - A "Secrets" panel in the hosted Claude Code UI (user originally referenced one but hasn't located it).
   - `.claude/settings.local.json` `env.ANTHROPIC_API_KEY` (file already exists with a placeholder if their last edit isn't persisted; gitignored).
   - `export ANTHROPIC_API_KEY=...` in the terminal that launches Claude Code.
2. Run `uv run python seed.py` (idempotent re-seed) and then either `chat.py` for direct terminal use or `ask.py` per message for relay.
3. Test conversation logic: try the prompts in `README.md` (warm DB hit, escalation, story save).

## Security note

During the previous session the user pasted real-looking API keys directly into the chat twice (against their own stated preference). Both should be considered burned and revoked at https://console.anthropic.com/settings/keys. If the user pastes another key in the new session, remind them once, then proceed only if they explicitly authorize (do not run `export` with literal keys silently).

## Known design quirks

- `run_agent` does not preserve conversation history across user turns — each message is a fresh standalone conversation. Worth fixing later if multi-turn coherence matters.
- The agent's system prompt does not forbid answering general-knowledge questions outside the personal database. It currently fills in (e.g. "what road connects Ngee Ann Poly to NUS?" got answered from model knowledge). Tighten the prompt if pure-personal scope is desired.
- `seed.py` wipes and reloads — safe for placeholder data but destructive once real entries exist via `admin.py`. Consider gating it behind a confirm flag before real-data use.
