import json, os, random

CAPTION_FILE = "captions.json"

def get_caption():
    if not os.path.exists(CAPTION_FILE):
        return ""
    with open(CAPTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    captions = data.get("captions", [])
    return random.choice(captions) if captions else ""
