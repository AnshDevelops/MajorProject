import base64, requests
from io import BytesIO
from PIL import Image
from .config import together_client
from .pipeline import scene_prompts, seed

def generate_images(story: str, style: str, quality: int, n: int):
    prompts = scene_prompts(story, n)
    out = []
    for p in prompts:
        full = f"{style} style, cinematic lighting, quality {quality}, {p}"
        try:
            resp = together_client.images.generate(
                model="black-forest-labs/FLUX.1-schnell-Free",
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
