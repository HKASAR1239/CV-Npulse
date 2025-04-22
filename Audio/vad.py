# vad.py
"""
Light-weight wrapper around WebRTC Voice Activity Detection.
"""

from __future__ import annotations

import webrtcvad


class VoiceActivityDetector:
    """Return *True* when speech is detected in a raw PCM byte string."""

    def __init__(self, aggressiveness: int = 1, sample_rate: int = 16_000):
        if aggressiveness not in range(4):
            raise ValueError("aggressiveness must be 0-3.")
        self._vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self._frame_len = int(sample_rate * 0.02) * 2  # 20 ms

    # ------------------------------------------------------------------ #
    def __call__(self, audio_bytes: bytes) -> bool:
        return any(
            self._vad.is_speech(frame, self.sample_rate)
            for frame in self._frames(audio_bytes)
        )

    # ------------------------------------------------------------------ #
    def _frames(self, audio: bytes):
        for off in range(0, len(audio) - self._frame_len + 1, self._frame_len):
            yield audio[off : off + self._frame_len]
