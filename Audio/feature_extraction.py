# feature_extraction.py
"""
Feature-extraction helpers converting raw 16-bit PCM audio to MFCC tensors.
"""

from __future__ import annotations

import numpy as np
import torch
import torchaudio
from torchaudio.transforms import MFCC


def _bytes_to_tensor(audio_bytes: bytes) -> torch.Tensor:
    """Convert raw 16-bit PCM bytes to a (1, samples) float32 tensor."""
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    if (peak := np.abs(audio_np).max()) > 0:
        audio_np /= peak
    return torch.from_numpy(audio_np).unsqueeze(0)  # (1, N)


def extract_mfcc(
    audio_bytes: bytes,
    sample_rate: int = 16_000,
    n_mfcc: int = 13,
    *,
    device: torch.device | str | None = None,
) -> torch.Tensor:
    """Return an ``(1, n_mfcc, time)`` MFCC tensor on the requested *device*."""
    waveform = _bytes_to_tensor(audio_bytes)
    mfcc = MFCC(
        sample_rate=sample_rate,
        n_mfcc=n_mfcc,
        melkwargs=dict(n_fft=400, hop_length=160, n_mels=40, center=False, power=2.0),
    )(waveform)
    return mfcc.to(device) if device else mfcc
