
"""
CNN Pothole Model — stub module.

If you have a trained ResNet-18 checkpoint (pothole_weights.pth),
place it in the models/ folder and the ai_detection_service will
automatically load it.

This file shows the exact architecture you need to match.
"""

import os

try:
    import torch
    import torch.nn as nn
    from torchvision import models

    class PotholeCNN(nn.Module):
        """
        Binary classifier built on top of ResNet-18.
          Output index 0 → no pothole
          Output index 1 → pothole
        """

        def __init__(self, pretrained: bool = False):
            super().__init__()
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            backbone = models.resnet18(weights=weights)
            in_features = backbone.fc.in_features
            backbone.fc = nn.Identity()
            self.backbone = backbone
            self.head = nn.Sequential(
                nn.Linear(in_features, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 2),
                nn.Softmax(dim=1),
            )

        def forward(self, x):
            features = self.backbone(x)
            return self.head(features)

    def load_model(weights_path: str | None = None) -> "PotholeCNN":
        model = PotholeCNN(pretrained=False)
        if weights_path and os.path.exists(weights_path):
            state = torch.load(weights_path, map_location="cpu")
            model.load_state_dict(state)
        model.eval()
        return model

except (ImportError, RuntimeError, Exception) as e:
    # PyTorch not installed or incompatible — provide a no-op placeholder
    class PotholeCNN:  # type: ignore
        """Placeholder when PyTorch is not installed."""
        pass

    def load_model(weights_path=None):  # type: ignore
        return None
