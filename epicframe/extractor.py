import json
import re

from .config import get_settings
from .prompts import CHARACTER_RELATION_PROMPT, EVENT_EXTRACTION_PROMPT

settings = get_settings()


def extract_entities(text: str) -> dict:
    prompt = CHARACTER_RELATION_PROMPT % text
    resp = settings.together_client.chat.completions.create(
        model=settings.text_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    raw = resp.choices[0].message.content.strip()

    block = re.search(r"\{[\s\S]*\}", raw)
    if not block:
        raise RuntimeError("no-json")

    data = json.loads(block.group(0))

    data.setdefault("characters", [])
    data.setdefault("relations", [])
    data.setdefault("traits", {})

    missing = set(data["traits"].keys()) - set(data["characters"])
    if missing:
        data["characters"].extend(sorted(missing))

    return data


def extract_events(text: str) -> dict:
    prompt = EVENT_EXTRACTION_PROMPT % text
    resp = settings.together_client.chat.completions.create(
        model=settings.text_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    raw = resp.choices[0].message.content.strip()

    block = re.search(r"\{[\s\S]*\}", raw)
    if not block:
        raise RuntimeError("no-json")

    data = json.loads(block.group(0))

    data.setdefault("events", [])
    data.setdefault("subplots", [])

    return data
