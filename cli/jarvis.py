#!/usr/bin/env python3
"""
JARVIS CLI — interact with your Jarvis assistant from the terminal.

Usage:
  python -m cli.jarvis                  # interactive REPL
  python -m cli.jarvis "status update"  # one-shot query
  python -m cli.jarvis --session abc123 "what's blocked?"
"""

import json
import sys
from typing import Optional

import click
import httpx

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


BASE_URL = "http://localhost:8000"
console = Console() if HAS_RICH else None


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_msg(role: str, content: str) -> None:
    if HAS_RICH:
        if role == "user":
            console.print(Panel(content, title="[bold cyan]You[/]", border_style="dim blue"))
        else:
            console.print(Panel(Markdown(content), title="[bold green]JARVIS[/]", border_style="green"))
    else:
        prefix = "You> " if role == "user" else "JARVIS> "
        print(f"\n{prefix}{content}\n")


def print_tool_event(event: dict) -> None:
    name = event.get("name", "")
    labels = {
        "get_github_overview": "GitHub overview",
        "get_github_issues": "GitHub issues",
        "get_github_commits": "GitHub commits",
        "get_analytics_summary": "Analytics",
        "get_notion_tasks": "Notion",
        "get_linear_issues": "Linear",
        "get_trello_cards": "Trello",
        "read_file": "reading file",
        "list_directory": "listing directory",
    }
    label = labels.get(name, name)
    if event["type"] == "tool_start":
        if HAS_RICH:
            console.print(f"  [dim purple]⟳  Querying {label}…[/]")
        else:
            print(f"  [querying {label}...]", end="", flush=True)
    elif event["type"] == "tool_done":
        if HAS_RICH:
            console.print(f"  [dim green]✓  {label}[/]")
        else:
            print(f" done")


def new_session(client: httpx.Client) -> str:
    resp = client.post(f"{BASE_URL}/api/sessions")
    resp.raise_for_status()
    return resp.json()["session_id"]


def stream_chat(client: httpx.Client, session_id: str, message: str) -> str:
    full_text = ""
    in_stream = False

    with client.stream(
        "POST",
        f"{BASE_URL}/api/chat",
        json={"session_id": session_id, "message": message},
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        buffer = ""

        if not HAS_RICH:
            print("\nJARVIS> ", end="", flush=True)

        for chunk in resp.iter_text():
            buffer += chunk
            parts = buffer.split("\n\n")
            buffer = parts.pop()

            for part in parts:
                if not part.startswith("data: "):
                    continue
                raw = part[6:].strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                if event["type"] in ("tool_start", "tool_done"):
                    print_tool_event(event)

                elif event["type"] == "text":
                    content = event["content"]
                    full_text += content
                    if not HAS_RICH:
                        print(content, end="", flush=True)

                elif event["type"] == "done":
                    if not HAS_RICH:
                        print()  # newline after streaming

                elif event["type"] == "error":
                    msg = event.get("message", "unknown error")
                    if HAS_RICH:
                        console.print(f"[bold red]Error:[/] {msg}")
                    else:
                        print(f"\nError: {msg}")

    return full_text


# ── CLI ───────────────────────────────────────────────────────────────────────

@click.command()
@click.argument("query", nargs=-1)
@click.option("--session", "-s", default=None, help="Reuse an existing session ID.")
@click.option("--url", default=BASE_URL, show_default=True, help="Jarvis server URL.")
@click.option("--no-color", is_flag=True, help="Disable rich output.")
def main(query: tuple, session: Optional[str], url: str, no_color: bool) -> None:
    """JARVIS — AI project intelligence assistant."""
    global BASE_URL, console

    BASE_URL = url.rstrip("/")

    if no_color and HAS_RICH:
        import io
        global console
        console = Console(file=io.StringIO())  # suppress rich

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        # Check server reachability
        try:
            status = client.get(f"{BASE_URL}/api/status")
            status.raise_for_status()
        except Exception as exc:
            click.echo(
                f"Cannot reach Jarvis at {BASE_URL}.\n"
                f"Start the server with: uvicorn backend.main:app --reload\n"
                f"Error: {exc}",
                err=True,
            )
            sys.exit(1)

        sid = session or new_session(client)

        if query:
            # One-shot mode
            text = " ".join(query)
            print_msg("user", text)
            response = stream_chat(client, sid, text)
            if HAS_RICH and response:
                print_msg("assistant", response)
        else:
            # Interactive REPL
            if HAS_RICH:
                console.print(Panel(
                    "[bold cyan]JARVIS[/] — Project Intelligence\n"
                    "[dim]Type your question. [bold]exit[/] or Ctrl-C to quit.[/]",
                    border_style="cyan",
                ))
            else:
                print("JARVIS — Project Intelligence")
                print("Type 'exit' to quit.\n")

            while True:
                try:
                    if HAS_RICH:
                        user_input = console.input("[bold cyan]You>[/] ").strip()
                    else:
                        user_input = input("You> ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nGoodbye.")
                    break

                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "bye"):
                    print("Goodbye.")
                    break

                response = stream_chat(client, sid, user_input)
                if HAS_RICH and response:
                    print_msg("assistant", response)


if __name__ == "__main__":
    main()
