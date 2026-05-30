"""
Jarvis agent — wraps Claude with tool use and conversation memory.

Tool-use turns use blocking Claude calls (executed in a thread pool).
The final answer is streamed via an async generator that yields SSE-ready dicts.
"""

import asyncio
import json
from typing import AsyncGenerator

import anthropic

from backend.config import settings
from backend.memory import memory
from backend.tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = """You are JARVIS, an AI assistant helping the user stay on course with their projects.

You have real-time access to:
- GitHub: repositories, issues, pull requests, commit history
- Google Analytics: traffic, sessions, page views, top pages, sources
- Task management: Notion databases, Linear issues, Trello boards
- Local files: project files and documentation

Your job:
1. Surface what matters — blockers, overdue tasks, stalled PRs, critical issues
2. Synthesize data across tools into a clear picture of project health
3. Help the user decide what to focus on next
4. Answer questions about projects with real data, not assumptions

Style:
- Lead with the most important information
- Be direct and concise — no filler
- Use bullet points for lists
- Highlight problems in plain language
- When an integration isn't configured, say so and move on
- Always pull fresh data with tools rather than guessing

If the user says "status", "update", or "how are things going" — give a full cross-tool summary."""


class JarvisAgent:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(
        self, session_id: str, user_message: str
    ) -> AsyncGenerator[dict, None]:
        """
        Yields SSE event dicts:
          {"type": "tool_start", "name": str}
          {"type": "tool_done",  "name": str, "result": str}
          {"type": "text",       "content": str}   ← streamed
          {"type": "done"}
          {"type": "error",      "message": str}
        """
        memory.append(session_id, "user", user_message)
        messages = memory.get_messages(session_id)
        # Drop the message we just appended so we pass a clean copy
        messages = messages[:-1]
        messages.append({"role": "user", "content": user_message})

        try:
            async for event in self._agent_loop(session_id, messages):
                yield event
        except Exception as exc:
            yield {"type": "error", "message": str(exc)}

    async def _agent_loop(
        self, session_id: str, messages: list[dict]
    ) -> AsyncGenerator[dict, None]:
        while True:
            # Non-streaming call to handle potential tool use
            response = await self.client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                # Collect tool calls from this response turn
                tool_results = []
                assistant_content = [b.model_dump() for b in response.content]
                messages.append({"role": "assistant", "content": assistant_content})

                for block in response.content:
                    if block.type == "tool_use":
                        yield {"type": "tool_start", "name": block.name}

                        result = await asyncio.to_thread(
                            execute_tool, block.name, block.input
                        )

                        yield {"type": "tool_done", "name": block.name, "result": result[:500]}

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({"role": "user", "content": tool_results})
                # Loop back to let Claude process tool results

            else:
                # Final response — stream the text
                final_text = ""
                async with self.client.messages.stream(
                    model="claude-opus-4-8",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                ) as stream:
                    async for chunk in stream.text_stream:
                        final_text += chunk
                        yield {"type": "text", "content": chunk}

                # Persist the completed exchange to memory
                memory.append(session_id, "assistant", final_text)
                yield {"type": "done"}
                break


agent = JarvisAgent()
