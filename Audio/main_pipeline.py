# main_pipeline.py
"""
Streaming pipeline for real-time wake-word + command recognition.
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import Optional

import torch

from audio_capture import AudioStream
from feature_extraction import extract_mfcc
from unified_model import UnifiedDSCNN
from vad import VoiceActivityDetector

LOG = logging.getLogger("pipeline")


def resolve_device(pref: Optional[str] = None) -> torch.device:
    if pref and getattr(torch.backends, pref).is_available():
        return torch.device(pref)
    for b in ("cuda", "mps"):
        if getattr(torch.backends, b).is_available():
            return torch.device(b)
    return torch.device("cpu")


def load_model(ckpt: Optional[Path], n_cmd: int, dev: torch.device) -> UnifiedDSCNN:
    model = UnifiedDSCNN(num_commands=n_cmd).to(dev)
    if ckpt and ckpt.is_file():
        model.load_state_dict(torch.load(ckpt, map_location=dev))
        LOG.info("Loaded checkpoint %s", ckpt)
    else:
        LOG.warning("Running with random weights.")
    model.eval()
    return model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("Realtime keyword-spotting demo")
    p.add_argument("--checkpoint", type=Path, help="*.pth model weights")
    p.add_argument(
        "--commands",
        nargs="+",
        default=["command_one", "command_two", "command_three"],
        help="List of command labels",
    )
    p.add_argument("--device", choices=("cpu", "cuda", "mps"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )

    device = resolve_device(args.device)
    model = load_model(args.checkpoint, len(args.commands), device)
    vad = VoiceActivityDetector()
    idx2label = {i: lbl for i, lbl in enumerate(args.commands)}

    LOG.info("Device: %s – press Ctrl-C to quit.", device)

    with AudioStream() as stream:
        try:
            while True:
                if (chunk := stream.read_nonblocking()) is None:
                    time.sleep(0.01)
                    continue
                if not vad(chunk):  # skip non-speech
                    continue
                mfcc = extract_mfcc(chunk, device=device).unsqueeze(0)  # (1,1,n,time)
                with torch.no_grad():
                    wake, cmd = model(mfcc)
                if wake.argmax().item() == 1:
                    LOG.info("Wake word detected – command: %s", idx2label[cmd.argmax()])
        except KeyboardInterrupt:
            LOG.info("Bye !")
            return


if __name__ == "__main__":
    main()
