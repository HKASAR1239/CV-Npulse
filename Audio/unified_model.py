# unified_model.py
"""
Depth-wise separable CNN with dual heads:
* Wake-word detection (2 classes)
* Command recognition (N classes)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class DWSeparableConv(nn.Module):
    def __init__(
        self,
        in_ch: int,
        out_ch: int,
        *,
        k: int | tuple[int, int] = 3,
        s: int = 1,
        p: int = 1,
    ):
        super().__init__()
        self.dw = nn.Conv2d(
            in_ch, in_ch, kernel_size=k, stride=s, padding=p, groups=in_ch, bias=False
        )
        self.pw = nn.Conv2d(in_ch, out_ch, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # noqa: D401
        x = self.dw(x)
        x = self.pw(x)
        return F.relu(self.bn(x))


class UnifiedDSCNN(nn.Module):
    def __init__(self, num_commands: int = 3):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )
        self.blocks = nn.Sequential(
            DWSeparableConv(64, 64),
            DWSeparableConv(64, 64),
            DWSeparableConv(64, 128, s=2),
            DWSeparableConv(128, 128),
            DWSeparableConv(128, 256, s=2),
            DWSeparableConv(256, 256),
        )
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc_wake = nn.Linear(256, 2)
        self.fc_cmd = nn.Linear(256, num_commands)

    def forward(self, x: torch.Tensor):
        x = self.stem(x)
        x = self.blocks(x)
        x = self.pool(x).flatten(1)
        return self.fc_wake(x), self.fc_cmd(x)
