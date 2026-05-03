"""One-shot wrapper around run_agent so a single message can be sent via CLI."""

import sys

import anthropic

from chat import run_agent
from db import init_db


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: ask.py <message>", file=sys.stderr)
        sys.exit(2)

    init_db()
    client = anthropic.Anthropic()
    message = sys.argv[1]
    print(run_agent(client, message))


if __name__ == "__main__":
    main()
