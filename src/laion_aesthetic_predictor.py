import os
import torch
from torchvision import transforms
from PIL import Image
import timm
import requests
from pathlib import Path

# A custom transform to resize and pad images to a square
class ResizeAndPad:
    def __init__(self, output_size, fill_color=(0, 0, 0)):
        self.output_size = output_size
        self.fill_color = fill_color

    def __call__(self, img):
        # Create a copy to avoid modifying the original image with thumbnail
        img = img.copy()
        # Resize the image so that its longest side is `output_size`
        img.thumbnail((self.output_size, self.output_size), Image.Resampling.LANCZOS)
        
        # Create a new square image with a black background
        new_img = Image.new("RGB", (self.output_size, self.output_size), self.fill_color)
        
        # Paste the resized image into the center of the black square
        paste_position = (
            (self.output_size - img.width) // 2,
            (self.output_size - img.height) // 2
        )
        new_img.paste(img, paste_position)
        
        return new_img

MODEL_NAME = "vit_base_patch16_224"
AESTHETIC_WEIGHTS_URL = "https://huggingface.co/trl-lib/ddpo-aesthetic-predictor/resolve/main/aesthetic-model.pth"
AESTHETIC_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "sa_0.4.pt")
FINETUNED_WEIGHTS_PATH = Path("models/aesthetic_model_finetuned.pth")


def download_weights(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)

class AestheticMLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = torch.nn.Sequential(
            torch.nn.Linear(768, 1024),
            torch.nn.ReLU(),
            torch.nn.Linear(1024, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 16),
            torch.nn.Linear(16, 1)
        )
    
    def forward(self, x):
        return self.layers(x)

class LAIONAestheticPredictor:
    def __init__(self, device=None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        
        # Create and load the MLP
        self.linear = AestheticMLP()

        # Check for a fine-tuned model first
        if FINETUNED_WEIGHTS_PATH.exists():
            print("Loading fine-tuned model weights.")
            # Load the state dict directly from the fine-tuned file
            self.linear.load_state_dict(torch.load(FINETUNED_WEIGHTS_PATH, map_location=self.device))
        else:
            print("No fine-tuned model found. Loading base model weights.")
            # Download and load the base aesthetic weights if needed
            download_weights(AESTHETIC_WEIGHTS_URL, AESTHETIC_WEIGHTS_PATH)
            base_weights = torch.load(AESTHETIC_WEIGHTS_PATH, map_location=self.device)
            
            # Map the keys from the base model to the MLP state dict format
            state_dict = {}
            for k, v in base_weights.items():
                new_key = k.replace('layers.', '') if 'layers.' in k else k
                state_dict[f'layers.{new_key}'] = v
            self.linear.load_state_dict(state_dict)

        self.linear.to(self.device)
        self.linear.eval()
        
        # Load the ViT model
        self.model = timm.create_model(MODEL_NAME, pretrained=True)
        self.model.eval()
        self.model.to(self.device)
        
        self.preprocess = transforms.Compose([
            ResizeAndPad(224), # Use the new custom transform
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.48145466, 0.4578275, 0.40821073],
                std=[0.26862954, 0.26130258, 0.27577711]
            )
        ])

    @torch.no_grad()
    def predict(self, pil_image):
        if not isinstance(pil_image, Image.Image):
            raise ValueError("Input must be a PIL.Image.Image")
        image = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        features = self.model.forward_features(image)
        features = features[:, 0, :]  # CLS token
        score = self.linear(features).item()
        # Clamp to [0, 10]
        return max(0, min(10, score)) 