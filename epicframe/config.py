import os

from dotenv import load_dotenv
from together import Together

load_dotenv()


class Settings:
    together_client: Together = Together(api_key=os.getenv("TOGETHER_API_KEY"))
    image_model: str = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell-Free")
    text_model: str = os.getenv("TEXT_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")


def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings"]
