"""Tool implementations the agent can call."""

import json
from datetime import datetime, timezone

from db import connect


SEARCHABLE_COLUMNS = {
    "people": ["name", "relationship", "spouse", "children", "lives_in", "notes"],
    "places": ["place", "significance", "years", "notes"],
    "events": ["event", "date", "people_involved", "description"],
    "stories": ["title", "told_by", "transcript", "summary", "topics"],
}


def search_personal_database(query: str) -> str:
    """Search across people, places, events, and stories for the query string.

    Returns a JSON string with hits per table. Empty result lists mean no match
    in that table.
    """
    query = (query or "").strip()
    if not query:
        return json.dumps({"error": "empty query"})

    like = f"%{query}%"
    results: dict[str, list[dict]] = {}

    with connect() as conn:
        for table, cols in SEARCHABLE_COLUMNS.items():
            where = " OR ".join(f"{col} LIKE ?" for col in cols)
            sql = f"SELECT * FROM {table} WHERE {where}"
            rows = conn.execute(sql, [like] * len(cols)).fetchall()
            results[table] = [dict(r) for r in rows]

    total = sum(len(v) for v in results.values())
    return json.dumps({"query": query, "total_hits": total, "results": results})


def add_pending_question(question: str) -> str:
    """Record a question the agent could not answer from the personal database."""
    question = (question or "").strip()
    if not question:
        return json.dumps({"error": "empty question"})

    asked_at = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO pending_questions (question, asked_at, status) "
            "VALUES (?, ?, 'open')",
            (question, asked_at),
        )
        conn.commit()
        return json.dumps({"id": cur.lastrowid, "asked_at": asked_at, "status": "open"})


def save_story(title: str, transcript: str) -> str:
    """Save a story told by the user to the stories table."""
    title = (title or "").strip()
    transcript = (transcript or "").strip()
    if not title or not transcript:
        return json.dumps({"error": "title and transcript are required"})

    date_told = datetime.now(timezone.utc).date().isoformat()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO stories (title, date_told, told_by, transcript) "
            "VALUES (?, ?, 'self', ?)",
            (title, date_told, transcript),
        )
        conn.commit()
        return json.dumps({"id": cur.lastrowid, "title": title, "date_told": date_told})


# Tool schemas exposed to Claude.
TOOL_SCHEMAS = [
    {
        "name": "search_personal_database",
        "description": (
            "Search the user's personal family database across people, places, "
            "events, and stories. Use this for any question about the user's own "
            "life, family, or memories. The query can be a name, place, year, or "
            "topic; partial matches work."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (name, place, topic, year, etc.).",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "add_pending_question",
        "description": (
            "Record a question that cannot be answered from the personal database. "
            "Call this whenever search_personal_database returns no useful result "
            "for a personal question. After calling this, reply that you'll check "
            "with the family."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's original question, recorded verbatim.",
                }
            },
            "required": ["question"],
        },
    },
    {
        "name": "save_story",
        "description": (
            "Save a story or memory the user just shared. Use this when the user "
            "spontaneously tells a memory, anecdote, or piece of family history "
            "worth preserving."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A short, descriptive title for the story.",
                },
                "transcript": {
                    "type": "string",
                    "description": "The story text, captured as faithfully as possible.",
                },
            },
            "required": ["title", "transcript"],
        },
    },
]


TOOL_DISPATCH = {
    "search_personal_database": lambda inp: search_personal_database(inp.get("query", "")),
    "add_pending_question": lambda inp: add_pending_question(inp.get("question", "")),
    "save_story": lambda inp: save_story(inp.get("title", ""), inp.get("transcript", "")),
}
