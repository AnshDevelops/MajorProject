import base64
import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image

from .config import get_settings
from .pipeline import scene_prompts, seed

load_dotenv()

settings = get_settings()


def generate_images(story: str, style: str, quality: int, n: int):
    prompts = scene_prompts(story, n)
    out = []
    for p in prompts:
        full = f"{style} style, cinematic lighting, quality {quality}, {p}"
        try:
            resp = settings.together_client.images.generate(
                model=settings.image_model,
                prompt=full,
                seed=seed(),
                width=768,
                height=512,
                steps=3,
            ).data[0]
            if hasattr(resp, "url"):
                img = Image.open(BytesIO(requests.get(resp.url, timeout=30).content))
            else:
                img = Image.open(BytesIO(base64.b64decode(resp.b64_json)))
            out.append(img)
        except Exception:
            continue
    return out
