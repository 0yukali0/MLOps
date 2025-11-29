# Core

import flytekit as fl
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


def add_class(row):
    row["class"] = row["path"].rsplit("/", 3)[-2]
    return row


def download_model(model_id: str) -> bool:
    CLIPProcessor.from_pretrained(model_id)
    CLIPModel.from_pretrained(model_id)
    return True


class EmbedImages(object):
    def __init__(self, model_id: str):
        d = fl.FlyteDirectory.from_source(model_id)
        local_path = d.download()
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
        local_path = local_path + "/snapshots/link"
        self.processor = CLIPProcessor.from_pretrained(
            local_path, local_files_only=True
        )
        self.model = CLIPModel.from_pretrained(local_path, local_files_only=True)
        self.model.to(device)
        self.device = device

    def __call__(self, row):
        img = Image.fromarray(np.uint8(row["image"])).convert("RGB")
        inputs = self.processor(images=[img], return_tensors="pt").to(self.device)
        with torch.inference_mode():
            row["embedding"] = self.model.get_image_features(**inputs).cpu().numpy()[0]
        return row
