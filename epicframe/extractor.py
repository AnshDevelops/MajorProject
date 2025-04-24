import json, re
from .config import together_client
from .prompts import LLAMA_JSON_PROMPT


def extract_entities(text: str) -> dict:
    prompt = LLAMA_JSON_PROMPT % text
    resp = together_client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
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