"""Simple retry utility with exponential backoff for data pipeline fetches."""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    coro_factory: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    label: str = "",
) -> T:
    """Retry an async callable with exponential backoff.

    Args:
        coro_factory: Zero-arg callable returning an awaitable (called fresh each attempt).
        max_attempts: Total attempts before giving up.
        base_delay: Initial delay in seconds (doubles each retry).
        label: Human-readable label for log messages.
    """
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return await coro_factory()
        except Exception as e:
            last_exc = e
            if attempt == max_attempts - 1:
                logger.error("%s failed after %d attempts: %s", label, max_attempts, e)
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "%s attempt %d/%d failed, retrying in %.1fs: %s",
                label, attempt + 1, max_attempts, delay, e,
            )
            await asyncio.sleep(delay)
    raise last_exc  # unreachable, but satisfies type checker
