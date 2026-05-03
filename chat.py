"""Terminal chat loop for the family assistant agent."""

import os
import sys

import anthropic

from db import init_db
from tools import TOOL_DISPATCH, TOOL_SCHEMAS


MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
MAX_TURNS = 10  # Safety cap per user message; tool loops shouldn't need this many.

SYSTEM_PROMPT = """\
You are a personal family assistant for an elderly user. Your job is to answer his \
questions about his own life, family, and memories using the personal database \
available through the search_personal_database tool.

How to behave:
- Tone is warm, brief, conversational. Treat him as a capable adult, not a patient.
- Keep replies short. Two or three sentences is usually right. Avoid long lists.
- Never invent facts about his life, his family, or his history. If something is \
  not in the database, you do not know it.
- Never quiz him, never test his memory, never reference forgetting. Do not say \
  things like "do you remember" or "as we discussed".
- Do not be overly formal or clinical. Skip phrases like "I have retrieved" or \
  "according to my records".

How to use tools:
- For any question about his life or family, call search_personal_database first. \
  Use the most useful keyword from his question (a name, place, year, or topic).
- If the search returns relevant information, answer directly from it in your own \
  natural words.
- If the search returns nothing useful, call add_pending_question with his \
  original question, then reply exactly: "Let me check with the family and get \
  back to you."
- If he spontaneously shares a memory, story, or piece of family history worth \
  keeping, call save_story to preserve it, then respond warmly to what he shared. \
  Do not save_story for casual chit-chat or for things he is asking about \
  (those are questions, not stories).
- For pure small talk ("how are you", "good morning"), reply briefly without \
  calling any tool.

Privacy: everything in the database is his own life. You can share it freely \
with him.
"""


def run_agent(client: anthropic.Anthropic, user_message: str) -> str:
    """Send a user message through Claude with tool use until a final reply."""
    messages = [{"role": "user", "content": user_message}]

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return _extract_text(response.content)

        if response.stop_reason != "tool_use":
            # Unexpected stop (refusal, max_tokens, etc.) — return whatever text we got.
            return _extract_text(response.content) or "(no reply)"

        # Append the assistant turn (with tool_use blocks) to history.
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            handler = TOOL_DISPATCH.get(block.name)
            if handler is None:
                result = f"unknown tool: {block.name}"
                is_error = True
            else:
                try:
                    result = handler(block.input or {})
                    is_error = False
                except Exception as exc:  # surface errors back to the model
                    result = f"tool error: {exc!r}"
                    is_error = True
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return "(agent stopped: too many tool-use turns)"


def _extract_text(blocks) -> str:
    return "".join(b.text for b in blocks if getattr(b, "type", None) == "text").strip()


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in your environment first.", file=sys.stderr)
        sys.exit(1)

    init_db()
    client = anthropic.Anthropic()

    print("Family assistant ready. Type a message, or 'quit' to exit.\n")
    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_message:
            continue
        if user_message.lower() in {"quit", "exit"}:
            break

        reply = run_agent(client, user_message)
        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()
