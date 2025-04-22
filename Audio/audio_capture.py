# audio_capture.py
import pyaudio
import queue

# Audio configuration parameters
CHUNK = 1024              # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono audio
RATE = 16000              # Sampling rate in Hz

# Create a thread-safe queue for audio chunks
audio_buffer = queue.Queue()

def audio_callback(in_data, frame_count, time_info, status):
    """Callback to store incoming audio data."""
    audio_buffer.put(in_data)
    return (None, pyaudio.paContinue)

def start_audio_stream():
    """Initialize and start the PyAudio stream."""
    audio_interface = pyaudio.PyAudio()
    stream = audio_interface.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=audio_callback
    )
    stream.start_stream()
    print("Audio stream started. Listening...")
    return stream, audio_interface

def stop_audio_stream(stream, audio_interface):
    """Stop the audio stream and clean up resources."""
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    print("Audio stream terminated.")
