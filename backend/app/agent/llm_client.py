"""Unified LLM client — supports Anthropic (Claude) and OpenAI (GPT) with tool use."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Timeout for LLM API calls (connect, read, write, pool)
LLM_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)
# Max retries for transient errors (rate limit, overloaded)
MAX_RETRIES = 2
RETRY_BASE_DELAY = 5.0  # seconds


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    done: bool = False  # True when model wants to stop (no more tool calls)


def _anthropic_tools(tools: list[dict]) -> list[dict]:
    """Anthropic tool format — already native."""
    return tools


def _openai_tools(tools: list[dict]) -> list[dict]:
    """Convert Anthropic-style tool defs to OpenAI function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


async def chat_with_tools(
    system: str,
    messages: list[dict],
    tools: list[dict],
) -> tuple[LLMResponse, list[dict]]:
    """Send a message with tools and return (response, updated_messages).

    The caller manages the tool-use loop — this function handles one round.
    Returns the LLMResponse and the messages list with the assistant turn appended.
    """
    provider = settings.llm_provider

    if provider == "openai":
        return await _openai_round(system, messages, tools)
    else:
        return await _anthropic_round(system, messages, tools)


async def _anthropic_round(
    system: str,
    messages: list[dict],
    tools: list[dict],
) -> tuple[LLMResponse, list[dict]]:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=LLM_TIMEOUT)


    for attempt in range(MAX_RETRIES + 1):
        try:
            response = await client.messages.create(
                model=settings.anthropic_model,
                max_tokens=8192,
                system=system,
                tools=_anthropic_tools(tools),
                messages=messages,
            )
            break
        except anthropic.RateLimitError as e:

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning("Anthropic rate limited (attempt %d/%d), retrying in %.0fs", attempt + 1, MAX_RETRIES + 1, delay)
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(f"Anthropic rate limit exceeded after {MAX_RETRIES + 1} attempts") from e
        except anthropic.APITimeoutError as e:

            if attempt < MAX_RETRIES:
                logger.warning("Anthropic timeout (attempt %d/%d), retrying", attempt + 1, MAX_RETRIES + 1)
                await asyncio.sleep(RETRY_BASE_DELAY)
            else:
                raise RuntimeError(f"Anthropic API timed out after {MAX_RETRIES + 1} attempts") from e
        except anthropic.APIConnectionError as e:
            raise RuntimeError(f"Cannot connect to Anthropic API: {e}") from e
        except anthropic.AuthenticationError as e:
            raise RuntimeError(f"Anthropic API key invalid: {e}") from e
        except anthropic.BadRequestError as e:
            raise RuntimeError(f"Anthropic bad request (prompt too large?): {e}") from e
        except anthropic.APIStatusError as e:
            if e.status_code == 529:  # Overloaded
    
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning("Anthropic overloaded (attempt %d/%d), retrying in %.0fs", attempt + 1, MAX_RETRIES + 1, delay)
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(f"Anthropic API overloaded after {MAX_RETRIES + 1} attempts") from e
            else:
                raise RuntimeError(f"Anthropic API error ({e.status_code}): {e.message}") from e

    assistant_content = response.content
    messages.append({"role": "assistant", "content": assistant_content})

    result = LLMResponse()

    for block in assistant_content:
        if hasattr(block, "text"):
            result.text = block.text
        if block.type == "tool_use":
            result.tool_calls.append(ToolCall(
                id=block.id,
                name=block.name,
                input=block.input,
            ))

    if response.stop_reason == "max_tokens":
        logger.warning("Anthropic response truncated (hit max_tokens) — tool calls may be incomplete")
    result.done = response.stop_reason == "end_turn"
    return result, messages


def _build_tool_results_anthropic(tool_calls: list[ToolCall], results: dict[str, str]) -> dict:
    """Build Anthropic-format tool results message."""
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": results[tc.id],
            }
            for tc in tool_calls
            if tc.id in results
        ],
    }


async def _openai_round(
    system: str,
    messages: list[dict],
    tools: list[dict],
) -> tuple[LLMResponse, list[dict]]:
    import openai

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key, timeout=LLM_TIMEOUT)

    # Convert messages to OpenAI format
    oai_messages = _to_openai_messages(system, messages)

    # Validate messages are JSON-serializable before sending
    try:
        import json as _json
        _json.dumps(oai_messages)
    except (TypeError, ValueError) as e:
        logger.error("Messages contain non-serializable data: %s", e)
        # Find the problematic message
        for i, msg_item in enumerate(oai_messages):
            try:
                _json.dumps(msg_item)
            except (TypeError, ValueError):
                logger.error("Problematic message at index %d: %s", i, repr(msg_item)[:500])
                break


    for attempt in range(MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                max_completion_tokens=8192,
                messages=oai_messages,
                tools=_openai_tools(tools),
            )
            break
        except openai.RateLimitError as e:

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning("OpenAI rate limited (attempt %d/%d), retrying in %.0fs", attempt + 1, MAX_RETRIES + 1, delay)
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(f"OpenAI rate limit exceeded after {MAX_RETRIES + 1} attempts") from e
        except openai.APITimeoutError as e:

            if attempt < MAX_RETRIES:
                logger.warning("OpenAI timeout (attempt %d/%d), retrying", attempt + 1, MAX_RETRIES + 1)
                await asyncio.sleep(RETRY_BASE_DELAY)
            else:
                raise RuntimeError(f"OpenAI API timed out after {MAX_RETRIES + 1} attempts") from e
        except openai.APIConnectionError as e:
            raise RuntimeError(f"Cannot connect to OpenAI API: {e}") from e
        except openai.AuthenticationError as e:
            raise RuntimeError(f"OpenAI API key invalid: {e}") from e
        except openai.BadRequestError as e:
            raise RuntimeError(f"OpenAI bad request: {e}") from e

    choice = response.choices[0]
    msg = choice.message

    # Build assistant message in our internal format for history
    assistant_entry = _openai_msg_to_internal(msg)
    messages.append(assistant_entry)

    result = LLMResponse()
    result.text = msg.content

    if msg.tool_calls:
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}
            result.tool_calls.append(ToolCall(
                id=tc.id,
                name=tc.function.name,
                input=args,
            ))

    if choice.finish_reason == "length":
        logger.warning("OpenAI response truncated (hit max_completion_tokens) — tool calls may be incomplete")
    result.done = choice.finish_reason == "stop"
    return result, messages


def append_tool_results(
    messages: list[dict],
    tool_calls: list[ToolCall],
    results: dict[str, str],
) -> list[dict]:
    """Append tool results to messages in the correct format for the active provider."""
    provider = settings.llm_provider

    if provider == "openai":
        for tc in tool_calls:
            if tc.id in results:
                messages.append({
                    "role": "tool",
                    "_provider": "openai",
                    "tool_call_id": tc.id,
                    "content": results[tc.id],
                })
    else:
        messages.append(_build_tool_results_anthropic(tool_calls, results))

    return messages


def _to_openai_messages(system: str, messages: list[dict]) -> list[dict]:
    """Convert our internal message format to OpenAI's format."""
    oai = [{"role": "system", "content": system}]

    for msg in messages:
        if msg.get("_provider") == "openai":
            # Already in OpenAI format (tool results)
            oai.append({
                "role": msg["role"],
                "tool_call_id": msg.get("tool_call_id"),
                "content": msg["content"],
            })
        elif msg.get("_provider") == "openai_assistant":
            # OpenAI assistant message with tool calls
            entry: dict = {"role": "assistant", "content": msg.get("content") or ""}
            if msg.get("tool_calls"):
                entry["tool_calls"] = msg["tool_calls"]
            oai.append(entry)
        elif msg["role"] == "user":
            content = msg["content"]
            if isinstance(content, str):
                oai.append({"role": "user", "content": content})
            elif isinstance(content, list):
                # Could be Anthropic tool_result blocks — convert
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        # These should have been handled by _provider tags
                        text_parts.append(f"[Tool result: {block.get('content', '')}]")
                    elif isinstance(block, dict):
                        text_parts.append(str(block.get("text", block.get("content", ""))))
                    else:
                        text_parts.append(str(block))
                oai.append({"role": "user", "content": "\n".join(text_parts)})
        elif msg["role"] == "assistant":
            content = msg["content"]
            if isinstance(content, str):
                oai.append({"role": "assistant", "content": content})
            elif isinstance(content, list):
                # Anthropic content blocks — extract text
                texts = []
                for block in content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                oai.append({"role": "assistant", "content": "\n".join(texts) or ""})

    return oai


def _openai_msg_to_internal(msg) -> dict:
    """Convert OpenAI response message to our internal format."""
    entry: dict = {
        "role": "assistant",
        "_provider": "openai_assistant",
        "content": msg.content,
    }
    if msg.tool_calls:
        entry["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
    return entry


async def simple_completion(system: str, user_message: str) -> str:
    """Simple completion without tools — used by topology learning etc."""
    provider = settings.llm_provider

    if provider == "openai":
        import openai
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key, timeout=LLM_TIMEOUT)
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                max_completion_tokens=2048,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content or ""
        except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError) as e:
            logger.error("OpenAI simple_completion failed: %s", e)
            raise RuntimeError(f"OpenAI API error: {e}") from e
    else:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=LLM_TIMEOUT)
        try:
            response = await client.messages.create(
                model=settings.anthropic_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": user_message}],
                system=system,
            )
            return response.content[0].text
        except (anthropic.RateLimitError, anthropic.APITimeoutError, anthropic.APIConnectionError) as e:
            logger.error("Anthropic simple_completion failed: %s", e)
            raise RuntimeError(f"Anthropic API error: {e}") from e
