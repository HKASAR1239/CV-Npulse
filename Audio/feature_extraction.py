# feature_extraction.py
import torch
import torchaudio
import numpy as np

def extract_mfcc_from_bytes(audio_bytes, sample_rate=16000, n_mfcc=13):
    """
    Convert raw 16-bit PCM audio bytes to MFCC features.
    Returns a tensor of shape (1, n_mfcc, time).
    """
    # Convert raw bytes to a NumPy array (float32) and normalize to [-1,1]
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    if np.max(np.abs(audio_np)) != 0:
        audio_np = audio_np / np.max(np.abs(audio_np))
    # Convert to a Torch tensor and add channel dimension: (1, num_samples)
    waveform = torch.from_numpy(audio_np).unsqueeze(0)
    
    # Define the MFCC transform (adjust parameters as needed)
    mfcc_transform = torchaudio.transforms.MFCC(
        sample_rate=sample_rate,
        n_mfcc=n_mfcc,
        melkwargs={
            "n_fft": 400,
            "hop_length": 160,
            "n_mels": 40,
            "center": False,
            "power": 2.0,
        }
    )
    mfcc = mfcc_transform(waveform)  # shape: (1, n_mfcc, time)
    return mfcc
