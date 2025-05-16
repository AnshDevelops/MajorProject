CHARACTER_RELATION_PROMPT = """
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

EVENT_EXTRACTION_PROMPT = """
Extract chronological events from the text.
Keep event descriptions brief and clear.

Return JSON in this schema:
{
  "plots": [
    {
      "id": "p1",
      "event": "Major story event",  # Keep under 6 words
      "time": "start",
      "sequence": 1
    }
  ],
  "subplots": [
    {
      "from": "p1",
      "to": "p2",
      "type": "leads_to",
      "event": "Brief connecting event",  # Keep under 6 words
      "sequence": 2
    }
  ]
}

Rules:
- Use 3-6 words per event description
- Start with action verbs
- Use IDs like p1, p2, etc.
- Mark first/last with time: "start"/"end"
- Number events sequentially

Examples:
✓ "Hero finds ancient sword"
✓ "Castle falls to invaders"
✓ "Princess escapes through portal"

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
