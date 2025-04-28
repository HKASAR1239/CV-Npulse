from pathlib import Path
import torch, torchaudio
from feature_extraction import extract_mfcc_from_tensor

LABELS = [l.strip() for l in open("commands.txt")] + ["wake", "garbage"]
label2idx = {lbl: i for i, lbl in enumerate(LABELS)}

class CommandDataset(torch.utils.data.Dataset):
    def __init__(self, split="train", precompute=True):
        self.precompute = precompute
        base = Path("data")
        txt  = base / "splits" / f"{split}.txt"
        self.items = [line.strip().split() for line in txt.read_text().splitlines()]
        self.root_raw = base / "raw"
        self.root_proc = base / "processed"
    def __len__(self): return len(self.items)
    def __getitem__(self, idx):
        rel_path, label = self.items[idx]
        if self.precompute:
            mfcc = torch.load(self.root_proc / Path(rel_path).with_suffix(".pt").name)
        else:
            wav, sr = torchaudio.load(self.root_raw / rel_path)
            wav = torchaudio.functional.resample(wav.mean(0, True), sr, 16_000)
            mfcc = extract_mfcc_from_tensor(wav)
        wake = torch.tensor([1 if label=="wake" else 0])
        cmd  = torch.tensor(label2idx.get(label, label2idx["garbage"]))
        return mfcc, wake, cmd
