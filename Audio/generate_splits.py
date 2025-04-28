# generate_splits.py
from pathlib import Path, PurePath
import random, csv

root = Path("data/raw")
splits = {"train": .8, "valid": .1, "test": .1}
pairs  = [(p, p.parent.name) for p in root.rglob("*.wav")]

random.shuffle(pairs)
N = len(pairs)
cursor = 0
for split, ratio in splits.items():
    out = Path("data/splits") / f"{split}.txt"
    out.parent.mkdir(exist_ok=True)
    with out.open("w") as f:
        for p, lbl in pairs[cursor:int(cursor+ratio*N)]:
            f.write(f"{p.relative_to(root).as_posix()} {lbl}\n")
    cursor += int(ratio*N)
