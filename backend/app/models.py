import torch
from torchvision import models, transforms
from PIL import Image
import os

# Load pre-trained DenseNet model (can simulate CheXNet-like behavior)
model = models.densenet121(pretrained=True)
model.classifier = torch.nn.Linear(model.classifier.in_features, 2)  # Binary: normal vs pneumonia
model.eval()

# Simulated weights – in real scenario, you’d load custom weights
# model.load_state_dict(torch.load("chexnet.pth", map_location=torch.device("cpu")))

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def analyze_xray(file_path):
    try:
        image = Image.open(file_path).convert("RGB")
        image = transform(image).unsqueeze(0)  # Add batch dim
        with torch.no_grad():
            outputs = model(image)
            probs = torch.nn.functional.softmax(outputs[0], dim=0)
            label = "Pneumonia Likely" if probs[1] > 0.5 else "Normal"
            return f"{label} (Confidence: {probs[1].item():.2f})"
    except Exception as e:
        return f"Error analyzing image: {str(e)}"
