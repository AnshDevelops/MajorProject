import os
from dotenv import load_dotenv
from together import Together
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
TOGETHER_TOKEN = os.getenv("TOGETHER_API_KEY", "")

together_client = Together(api_key=TOGETHER_TOKEN)
image_client = InferenceClient(token=HF_TOKEN)

__all__ = ["together_client", "image_client"]
