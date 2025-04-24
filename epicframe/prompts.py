LLAMA_JSON_PROMPT = """
Extract every character, all explicit relationships **and** any descriptive traits
(age, role, personality, skills, etc.) that the text gives about each character.
Return pure JSON ONLY in this schema:
{
  "characters": ["Alice", "Bob"],
  "traits": {
     "Alice": {"age": "25", "occupation": "botanist"},
     "Bob":   {"mood": "grumpy"}
  },
  "relations": [
     {"from":"Alice","to":"Bob","type":"friend"}
  ]
}
TEXT:
%s
"""

SUBPLOT_EXTRACTION_PROMPT = """
You are a literary analyst. Given the following story, perform these steps:
1. Identify and list the key events or subplots in the narrative.
2. Provide each event or subplot as a numbered list.
Story:
%s
"""

SCENE_DESCRIPTION_PROMPT = """
You have the following list of %d key events or subplots from a story:
%s
For each event:
- Craft one vivid, detailed scene description suitable for image generation.
- Include setting, mood, characters involved, and visual cues.
- Ensure each description is dramatically different but remains connected to the overall narrative.
Return the descriptions as an unnumbered list, one per line, each prefixed with a dash (-).
"""
