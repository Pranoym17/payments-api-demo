import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

T = TypeVar("T")


class RetryPolicy:
    def __init__(self, max_attempts: int = 3, backoff_seconds: float = 0.2) -> None:
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:
        last_error: httpx.HTTPError | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await operation()
            except httpx.TimeoutException as exc:
                last_error = exc
            except httpx.TransportError as exc:
                last_error = exc

            if attempt < self.max_attempts:
                await asyncio.sleep(self.backoff_seconds * attempt)

        if last_error:
            raise last_error

        raise RuntimeError("retry policy exhausted without result")
