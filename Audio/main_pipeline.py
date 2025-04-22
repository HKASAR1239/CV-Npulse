# main_pipeline.py
import time
import torch
from audio_capture import start_audio_stream, stop_audio_stream, audio_buffer
from vad import is_speech
from feature_extraction import extract_mfcc_from_bytes
from unified_model import UnifiedDSCNN

# Set up device: use MPS if available (macOS with Apple Silicon)
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using MPS device.")
else:
    device = torch.device("cpu")
    print("Using CPU.")

# Instantiate the unified model (adjust num_commands as needed)
num_commands = 3
model = UnifiedDSCNN(num_commands=num_commands)
try:
    model.load_state_dict(torch.load("unified_model.pth", map_location=device))
    print("Loaded pre-trained model weights.")
except Exception as e:
    print("No pre-trained model found; using untrained model. Error:", e)
model.to(device)
model.eval()

# Label maps (customize these as needed)
wake_label_map = {0: "no wake", 1: "wake"}
cmd_label_map = {0: "command_one", 1: "command_two", 2: "command_three"}

def process_audio_chunk(audio_chunk):
    # Step 1: Use VAD to filter non-speech segments.
    if not is_speech(audio_chunk):
        return
    
    # Step 2: Extract MFCC features from the live audio chunk.
    mfcc_tensor = extract_mfcc_from_bytes(audio_chunk)  # shape: (1, n_mfcc, time)
    # Ensure proper shape: (batch, channel, n_mfcc, time)
    mfcc_tensor = mfcc_tensor.unsqueeze(0)  # add batch dimension (now: (1, 1, n_mfcc, time))
    mfcc_tensor = mfcc_tensor.to(device)
    
    # Step 3: Run the unified model.
    with torch.no_grad():
        wake_logits, cmd_logits = model(mfcc_tensor)
    
    # Step 4: Interpret the outputs.
    wake_pred = torch.argmax(wake_logits, dim=1).item()  # 0 or 1
    if wake_pred == 1:
        print("Wake word detected!")
        cmd_pred = torch.argmax(cmd_logits, dim=1).item()
        print("Recognized command:", cmd_label_map.get(cmd_pred, "unknown"))
    else:
        print("No wake word detected in this chunk.")

def main():
    # Start audio capture
    stream, audio_interface = start_audio_stream()
    try:
        while True:
            if not audio_buffer.empty():
                audio_chunk = audio_buffer.get()
                process_audio_chunk(audio_chunk)
            time.sleep(0.01)  # Small delay to yield control
    except KeyboardInterrupt:
        print("Terminating pipeline...")
    finally:
        stop_audio_stream(stream, audio_interface)

if __name__ == "__main__":
    main()
