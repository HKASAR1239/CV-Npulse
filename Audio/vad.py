# vad.py
import webrtcvad

# Initialize WebRTC VAD (aggressiveness level: 0-3)
vad = webrtcvad.Vad(1)

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Yield audio frames of fixed duration."""
    bytes_per_frame = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + bytes_per_frame <= len(audio):
        yield audio[offset:offset + bytes_per_frame]
        offset += bytes_per_frame

def is_speech(audio_data, sample_rate=16000, frame_duration_ms=20):
    """
    Returns True if any frame of the audio_data is detected as speech.
    """
    frames = list(frame_generator(frame_duration_ms, audio_data, sample_rate))
    return any(vad.is_speech(frame, sample_rate) for frame in frames)
