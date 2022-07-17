from __future__ import annotations

import random
from collections import deque
from datetime import timedelta
from types import TracebackType
from typing import Deque, TypeVar

from .timer import Timer

PipelineT = TypeVar("PipelineT", bound="PipelineBase")


class StatsClientBase:
    """A Base class for various statsd clients."""

    _prefix: str | None

    def close(self) -> None:
        """Used to close and clean up any underlying resources."""
        raise NotImplementedError()

    def _send(self, data: str | None) -> None:
        raise NotImplementedError()

    def pipeline(self) -> PipelineBase:
        raise NotImplementedError()

    def timer(self, stat: str, rate: float = 1) -> Timer:
        return Timer(self, stat, rate)

    def timing(self, stat: str, delta: float | timedelta, rate: float = 1) -> None:
        """
        Send new timing information.

        `delta` can be either a number of milliseconds or a timedelta.
        """
        if isinstance(delta, timedelta):
            # Convert timedelta to number of milliseconds.
            delta = delta.total_seconds() * 1000.0
        self._send_stat(stat, "%0.6f|ms" % delta, rate)

    def incr(self, stat: str, count: int = 1, rate: float = 1) -> None:
        """Increment a stat by `count`."""
        self._send_stat(stat, "%s|c" % count, rate)

    def decr(self, stat: str, count: int = 1, rate: float = 1) -> None:
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(
        self, stat: str, value: float, rate: float = 1, delta: bool = False
    ) -> None:
        """Set a gauge value."""
        if value < 0 and not delta:
            if rate < 1:
                if random.random() > rate:
                    return
            with self.pipeline() as pipe:
                pipe._send_stat(stat, "0|g", 1)
                pipe._send_stat(stat, "%s|g" % value, 1)
        else:
            prefix = "+" if delta and value >= 0 else ""
            self._send_stat(stat, f"{prefix}{value}|g", rate)

    def set(self, stat: str, value: float | str, rate: float = 1) -> None:
        """Set a set value."""
        self._send_stat(stat, "%s|s" % value, rate)

    def _send_stat(self, stat: str, value: float | str, rate: float) -> None:
        self._after(self._prepare(stat, value, rate))

    def _prepare(self, stat: str, value: float | str, rate: float) -> str | None:
        if rate < 1:
            if random.random() > rate:
                return None
            value = f"{value}|@{rate}"

        if self._prefix:
            stat = f"{self._prefix}.{stat}"

        return f"{stat}:{value}"

    def _after(self, data: str | None) -> None:
        if data:
            self._send(data)


class PipelineBase(StatsClientBase):
    def __init__(self, client: StatsClientBase):
        self._client = client
        self._prefix = client._prefix
        self._stats: Deque[str] = deque()

    def _send(self, data: str | None = None) -> None:
        super()._send(data)

    def _after(self, data: str | None) -> None:
        if data is not None:
            self._stats.append(data)

    def __enter__(self) -> PipelineBase:
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.send()

    def send(self) -> None:
        if not self._stats:
            return
        self._send()

    def pipeline(self: PipelineT) -> PipelineT:
        return self.__class__(self)
