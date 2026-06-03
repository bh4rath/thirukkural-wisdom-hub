#!/usr/bin/env python3
"""
Step 1 of 2.
Downloads the original Kural data and creates 7 ready-to-paste prompt files
(batch_01.txt … batch_07.txt). Paste each into claude.ai and save the response
as response_01.txt … response_07.txt, then run merge_responses.py.
"""

import json
import math
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/tk120404/thirukkural/master/thirukkural.json"
BATCH_SIZE = 190  # ~7 batches total; comfortably fits in claude.ai output

PROMPT_HEADER = """\
You are simplifying Thirukkural explanations so a 10-year-old child can easily read and understand them.

For EVERY kural in the list below, rewrite TWO fields:
1. "translation" — one clear sentence (max 20 words) in everyday English, capturing what the couplet says.
2. "meaning_english" — 2-3 short sentences in simple, friendly language. Relate it to everyday life a child knows (school, family, friends, sports, food). No formal or old-fashioned words like "virtue", "righteousness", "thee", "thou", "conducive", "celestial", "temporal", "hath".

Return ONLY a valid JSON array — no markdown, no code fences, no extra text:
[{"num": <number>, "translation": "...", "meaning_english": "..."}, ...]

Kurals to simplify:
"""

def fetch_raw():
    print("Downloading original Kural data...")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        data = json.loads(r.read())
    raw = data.get("kural", data)
    print(f"  Got {len(raw)} Kurals.")
    return raw

def main():
    raw = fetch_raw()

    kurals_input = []
    for i, k in enumerate(raw):
        kurals_input.append({
            "num": i + 1,
            "translation": k.get("Translation", ""),
            "meaning_english": k.get("explanation", ""),
        })

    total_batches = math.ceil(len(kurals_input) / BATCH_SIZE)
    for b in range(total_batches):
        start = b * BATCH_SIZE
        batch = kurals_input[start: start + BATCH_SIZE]
        filename = f"batch_{b+1:02d}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(PROMPT_HEADER)
            f.write(json.dumps(batch, ensure_ascii=False, indent=2))
        nums = f"{batch[0]['num']}–{batch[-1]['num']}"
        print(f"  Created {filename}  ({len(batch)} Kurals, #{nums})")

    print(f"\nDone! {total_batches} prompt files created.")
    print("\nNext steps:")
    print("  1. Open batch_01.txt, copy ALL the text.")
    print("  2. Paste into claude.ai and send.")
    print("  3. When Claude replies, copy the ENTIRE JSON response.")
    print("  4. Save it as response_01.txt (in this same folder).")
    print("  5. Repeat for batch_02.txt → response_02.txt ... through batch_07.txt.")
    print("  6. Run:  python3 merge_responses.py")

if __name__ == "__main__":
    main()
