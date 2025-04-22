# unified_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        super(DepthwiseSeparableConv, self).__init__()
        # Depthwise convolution: one filter per input channel (groups = in_channels)
        self.depthwise = nn.Conv2d(
            in_channels, 
            in_channels, 
            kernel_size=kernel_size,
            stride=stride, 
            padding=padding, 
            groups=in_channels, 
            bias=False
        )
        # Pointwise convolution: 1x1 convolution to mix channels
        self.pointwise = nn.Conv2d(
            in_channels, 
            out_channels, 
            kernel_size=1,
            stride=1,
            bias=False
        )
        self.bn = nn.BatchNorm2d(out_channels)
        
    def forward(self, x):
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.bn(x)
        return F.relu(x)

class UnifiedDSCNN(nn.Module):
    def __init__(self, num_commands=3):
        """
        num_commands: number of command classes for recognition.
        The wake word head outputs 2 classes: 0 (no wake) and 1 (wake).
        """
        super(UnifiedDSCNN, self).__init__()
        # Initial convolution to expand from 1 channel to 64 channels.
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        # DS-CNN blocks
        self.dsconv1 = DepthwiseSeparableConv(64, 64, kernel_size=3, stride=1, padding=1)
        self.dsconv2 = DepthwiseSeparableConv(64, 64, kernel_size=3, stride=1, padding=1)
        self.dsconv3 = DepthwiseSeparableConv(64, 128, kernel_size=3, stride=2, padding=1)
        self.dsconv4 = DepthwiseSeparableConv(128, 128, kernel_size=3, stride=1, padding=1)
        self.dsconv5 = DepthwiseSeparableConv(128, 256, kernel_size=3, stride=2, padding=1)
        self.dsconv6 = DepthwiseSeparableConv(256, 256, kernel_size=3, stride=1, padding=1)
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        # Two heads:
        self.fc_wake = nn.Linear(256, 2)         # Wake word detection (binary)
        self.fc_cmd = nn.Linear(256, num_commands) # Command recognition (multi-class)
        
    def forward(self, x):
        # Input x shape: (batch, 1, n_mfcc, time)
        x = self.conv1(x)
        x = self.dsconv1(x)
        x = self.dsconv2(x)
        x = self.dsconv3(x)
        x = self.dsconv4(x)
        x = self.dsconv5(x)
        x = self.dsconv6(x)
        x = self.global_pool(x)  # shape: (batch, 256, 1, 1)
        x = x.view(x.size(0), -1)  # flatten to (batch, 256)
        wake_logits = self.fc_wake(x)
        cmd_logits = self.fc_cmd(x)
        return wake_logits, cmd_logits

# For testing purposes:
if __name__ == "__main__":
    dummy_input = torch.randn(1, 1, 13, 20)  # Example: 1 sample, 1 channel, 13 MFCC, 20 time frames
    model = UnifiedDSCNN(num_commands=3)
    wake_out, cmd_out = model(dummy_input)
    print("Wake logits:", wake_out)
    print("Command logits:", cmd_out)
