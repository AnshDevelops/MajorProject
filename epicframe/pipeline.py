import random
import re

from .config import get_settings
from .prompts import SUBPLOT_EXTRACTION_PROMPT, SCENE_DESCRIPTION_PROMPT

settings = get_settings()


def _subplots(story: str, k: int):
    p = SUBPLOT_EXTRACTION_PROMPT % story
    resp = settings.together_client.chat.completions.create(
        model=settings.text_model,
        messages=[{"role": "user", "content": p}],
        max_tokens=512,
    )
    numbered = [l.split('.', 1)[1].strip()
                for l in resp.choices[0].message.content.splitlines()
                if re.match(r"^\d+\.", l)]
    return numbered[:k]


def scene_prompts(story: str, k: int):
    events = _subplots(story, k)
    block = "\n".join(f"{i + 1}. {e}" for i, e in enumerate(events))
    p = SCENE_DESCRIPTION_PROMPT % (len(events), block)
    resp = settings.together_client.chat.completions.create(
        model=settings.text_model,
        messages=[{"role": "user", "content": p}],
        max_tokens=300 + 100 * len(events),
    )
    return [l.lstrip('- ').strip() for l in resp.choices[0].message.content.splitlines() if l.strip()][:k]


def seed():
    return random.randint(1, 10_000_000)
