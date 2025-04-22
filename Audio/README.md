# Real‑Time Wake‑Word & Command Recognition

> **Offline voice interface built on PyAudio, WebRTC VAD, Torchaudio and a lightweight depth‑wise separable CNN.**

---

## Features
* **Low‑latency** streaming (1024‑frame chunks)  
* **Unified model** – one network, two heads: wake‑word *and* command classification  
* **Automatic device selection** – CUDA, Apple Silicon (MPS) or CPU  
* **WebRTC VAD** – silence filtering to save compute

## Installation

```bash
# 1 – create & activate a virtual‑env
python -m venv .venv && source .venv/bin/activate

# 2 – system deps (Linux example)
sudo apt install python3-dev portaudio19-dev ffmpeg

# 3 – Python deps
pip install torch torchaudio pyaudio webrtcvad
# choose the correct torch wheel for your GPU / MPS / CPU
```

## Running the demo

```bash
python main_pipeline.py --checkpoint path/to/unified_model.pth \
                        --commands yes no maybe
```

If *--checkpoint* is omitted the pipeline still runs, but with random weights.

### Keyboard shortcuts
* **`Ctrl‑C`** – exit gracefully

## File overview
```
audio_capture.py      # microphone → queue
feature_extraction.py # bytes → MFCC
unified_model.py      # DS‑CNN two‑head network
vad.py                # WebRTC VAD helper
main_pipeline.py      # end‑to‑end pipeline
```

## Training
Training scripts are out of scope, but you can follow any DS‑CNN recipe on
Google Speech Commands and export weights with

```python
torch.save(model.state_dict(), "unified_model.pth")
```

## License
MIT

## Authors
Darius Giannoli and Gabriel Taïeb