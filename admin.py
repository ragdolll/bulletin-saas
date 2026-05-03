"""Admin CLI for the family database. Add, list, delete rows; manage pending questions.

Examples:
  uv run python admin.py add-person --name "Aunt Mei" --relationship aunt --lives-in "Kuala Lumpur"
  uv run python admin.py add-place --place "Cameron Highlands" --years 1980-1990 --significance "family holidays"
  uv run python admin.py add-event --event "Sarah's graduation" --date 1995-05-20 --people-involved "Sarah, Helen"
  uv run python admin.py add-story --title "First car" --transcript "I bought a beat-up Morris Minor in 1968..."
  uv run python admin.py list people
  uv run python admin.py delete people 5
  uv run python admin.py pending
  uv run python admin.py answer 3 --answer "Aunt Beatrice was your mother's youngest sister."
"""

import argparse
import sys
from datetime import datetime, timezone

from db import connect, init_db


TABLES = {"people", "places", "events", "stories", "pending_questions"}


def _insert(table: str, fields: dict) -> int:
    cols = ", ".join(fields.keys())
    placeholders = ", ".join("?" for _ in fields)
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    with connect() as conn:
        cur = conn.execute(sql, tuple(fields.values()))
        conn.commit()
        return cur.lastrowid


def add_person(args) -> None:
    fields = {"name": args.name}
    for key in ("relationship", "spouse", "children", "lives_in", "notes"):
        val = getattr(args, key)
        if val is not None:
            fields[key] = val
    new_id = _insert("people", fields)
    print(f"added person id={new_id}: {args.name}")


def add_place(args) -> None:
    fields = {"place": args.place}
    for key in ("significance", "years", "notes"):
        val = getattr(args, key)
        if val is not None:
            fields[key] = val
    new_id = _insert("places", fields)
    print(f"added place id={new_id}: {args.place}")


def add_event(args) -> None:
    fields = {"event": args.event}
    for key in ("date", "people_involved", "description"):
        val = getattr(args, key)
        if val is not None:
            fields[key] = val
    new_id = _insert("events", fields)
    print(f"added event id={new_id}: {args.event}")


def add_story(args) -> None:
    fields = {
        "title": args.title,
        "transcript": args.transcript,
        "told_by": args.told_by or "self",
        "date_told": args.date_told or datetime.now(timezone.utc).date().isoformat(),
    }
    for key in ("summary", "topics"):
        val = getattr(args, key)
        if val is not None:
            fields[key] = val
    new_id = _insert("stories", fields)
    print(f"added story id={new_id}: {args.title}")


def list_table(args) -> None:
    if args.table not in TABLES:
        print(f"unknown table: {args.table}. choose from {sorted(TABLES)}", file=sys.stderr)
        sys.exit(2)
    with connect() as conn:
        rows = conn.execute(f"SELECT * FROM {args.table} ORDER BY id").fetchall()
    if not rows:
        print(f"(no rows in {args.table})")
        return
    for row in rows:
        parts = [f"{k}={row[k]!r}" for k in row.keys() if row[k] is not None]
        print(" | ".join(parts))


def delete_row(args) -> None:
    if args.table not in TABLES:
        print(f"unknown table: {args.table}. choose from {sorted(TABLES)}", file=sys.stderr)
        sys.exit(2)
    with connect() as conn:
        cur = conn.execute(f"DELETE FROM {args.table} WHERE id = ?", (args.id,))
        conn.commit()
    if cur.rowcount == 0:
        print(f"no row with id={args.id} in {args.table}")
    else:
        print(f"deleted id={args.id} from {args.table}")


def show_pending(args) -> None:
    with connect() as conn:
        sql = "SELECT * FROM pending_questions"
        if args.all:
            sql += " ORDER BY asked_at DESC"
            rows = conn.execute(sql).fetchall()
        else:
            sql += " WHERE status = 'open' ORDER BY asked_at DESC"
            rows = conn.execute(sql).fetchall()
    if not rows:
        print("(no pending questions)")
        return
    for row in rows:
        print(f"[{row['id']}] {row['status']}  {row['asked_at']}")
        print(f"    Q: {row['question']}")
        if row["answer"]:
            who = f" ({row['answered_by']})" if row["answered_by"] else ""
            print(f"    A{who}: {row['answer']}")


def answer_pending(args) -> None:
    with connect() as conn:
        cur = conn.execute(
            "UPDATE pending_questions SET answer = ?, answered_by = ?, status = 'answered' "
            "WHERE id = ?",
            (args.answer, args.answered_by, args.id),
        )
        conn.commit()
    if cur.rowcount == 0:
        print(f"no pending question with id={args.id}")
    else:
        print(f"answered id={args.id}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Admin CLI for the family database.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("add-person", help="Insert a row into people.")
    sp.add_argument("--name", required=True)
    sp.add_argument("--relationship")
    sp.add_argument("--spouse")
    sp.add_argument("--children")
    sp.add_argument("--lives-in", dest="lives_in")
    sp.add_argument("--notes")
    sp.set_defaults(func=add_person)

    sp = sub.add_parser("add-place", help="Insert a row into places.")
    sp.add_argument("--place", required=True)
    sp.add_argument("--significance")
    sp.add_argument("--years")
    sp.add_argument("--notes")
    sp.set_defaults(func=add_place)

    sp = sub.add_parser("add-event", help="Insert a row into events.")
    sp.add_argument("--event", required=True)
    sp.add_argument("--date", help="Free-form date string, e.g. 1972-06-15 or 'summer 1980'.")
    sp.add_argument("--people-involved", dest="people_involved")
    sp.add_argument("--description")
    sp.set_defaults(func=add_event)

    sp = sub.add_parser("add-story", help="Insert a row into stories.")
    sp.add_argument("--title", required=True)
    sp.add_argument("--transcript", required=True)
    sp.add_argument("--told-by", dest="told_by", help="Defaults to 'self'.")
    sp.add_argument("--date-told", dest="date_told", help="Defaults to today (UTC).")
    sp.add_argument("--summary")
    sp.add_argument("--topics")
    sp.set_defaults(func=add_story)

    sp = sub.add_parser("list", help="Print all rows of a table.")
    sp.add_argument("table", choices=sorted(TABLES))
    sp.set_defaults(func=list_table)

    sp = sub.add_parser("delete", help="Delete a row by id.")
    sp.add_argument("table", choices=sorted(TABLES))
    sp.add_argument("id", type=int)
    sp.set_defaults(func=delete_row)

    sp = sub.add_parser("pending", help="Show pending questions (open by default).")
    sp.add_argument("--all", action="store_true", help="Include answered ones too.")
    sp.set_defaults(func=show_pending)

    sp = sub.add_parser("answer", help="Answer a pending question and mark it answered.")
    sp.add_argument("id", type=int)
    sp.add_argument("--answer", required=True)
    sp.add_argument("--answered-by", dest="answered_by", default="family")
    sp.set_defaults(func=answer_pending)

    return p


def main() -> None:
    init_db()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
