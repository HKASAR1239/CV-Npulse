# audio_capture.py
"""
Non-blocking audio capture utility based on PyAudio.

This module provides an :class:`AudioStream` that continuously pushes raw
16-bit PCM audio frames into a thread-safe :pymod:`queue.Queue`.  The class is
meant to be used as a context-manager:

    >>> from audio_capture import AudioStream
    >>> with AudioStream() as stream:
    ...     if (chunk := stream.read_nonblocking()) is not None:
    ...         process(chunk)
"""

from __future__ import annotations

import queue
from dataclasses import dataclass
from typing import Optional

import pyaudio


@dataclass(slots=True)
class AudioConfig:
    """Configuration parameters for :class:`AudioStream`."""
    rate: int = 16_000
    channels: int = 1
    chunk: int = 1024
    format: int = pyaudio.paInt16


class AudioStream:
    """High-level wrapper around PyAudio that captures microphone input."""

    def __init__(self, config: Optional[AudioConfig] = None) -> None:
        self.config = config or AudioConfig()
        self._buffer: queue.Queue[bytes] = queue.Queue()
        self._pa = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    @property
    def buffer(self) -> "queue.Queue[bytes]":
        return self._buffer

    def read_nonblocking(self) -> Optional[bytes]:
        try:
            return self._buffer.get_nowait()
        except queue.Empty:
            return None

    # ------------------------------------------------------------------ #
    # Context-manager helpers
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "AudioStream":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _callback(self, in_data, frame_count, time_info, status):
        self._buffer.put(in_data)
        return (None, pyaudio.paContinue)

    def start(self) -> None:
        if self._stream is not None:  # already started
            return
        self._stream = self._pa.open(
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.rate,
            input=True,
            frames_per_buffer=self.config.chunk,
            stream_callback=self._callback,
        )
        self._stream.start_stream()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        self._pa.terminate()
