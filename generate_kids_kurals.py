#!/usr/bin/env python3
"""
Generate kid-friendly English translations and explanations for all 1330 Thirukkural.

Usage:
    pip install anthropic
    ANTHROPIC_API_KEY=sk-ant-... python3 generate_kids_kurals.py

Produces kurals-kids.json — commit it alongside index.html.
"""

import json
import os
import time
import urllib.request
import anthropic

BATCH_SIZE = 10
SOURCE_URL = "https://raw.githubusercontent.com/tk120404/thirukkural/master/thirukkural.json"
OUTPUT_FILE = "kurals-kids.json"
RESUME_FILE = "kurals-kids-progress.json"

SYSTEM = """You simplify English explanations of Thirukkural (ancient Tamil wisdom couplets) so a 10-year-old child can easily read and understand them.

Rules:
- Use simple everyday words a child knows. No "thee/thou", "virtue", "righteousness", "conducive", "temporal", "celestial", "prosperity", "discourse", "hath", "doth" etc.
- Tone: warm, friendly, like an older sibling explaining something cool.
- "translation": one clear sentence (max 20 words) capturing what the couplet says.
- "meaning_english": 2–3 short sentences explaining the deeper idea. Relate it to everyday life — school, family, friends, sports, food. Make the child think "oh yeah, that makes sense!"
- Never start meaning_english with "This Kural..." or "Thiruvalluvar says...".
- Return ONLY a valid JSON array — no markdown fences, no extra text."""

def fetch_original():
    print("Fetching original data from GitHub...")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        data = json.loads(r.read())
    raw = data.get("kural", data)
    kurals = []
    for i, k in enumerate(raw):
        num = i + 1
        kurals.append({
            "number": num,
            "line1": k.get("Line1", ""),
            "line2": k.get("Line2", ""),
            "transliteration1": k.get("transliteration1", ""),
            "transliteration2": k.get("transliteration2", ""),
            "translation": k.get("translation") or k.get("Translation", ""),
            "meaning_tamil": (k.get("mk") or {}).get("mkural", ""),
            "meaning_english": k.get("explanation", ""),
        })
    print(f"  Loaded {len(kurals)} Kurals.")
    return kurals


def simplify_batch(client, batch):
    items = [
        {"num": k["number"], "translation": k["translation"], "meaning_english": k["meaning_english"]}
        for k in batch
    ]
    prompt = (
        "Simplify these Thirukkural explanations for a 10-year-old. "
        "Return a JSON array: [{\"num\": <number>, \"translation\": \"<simplified>\", \"meaning_english\": \"<simplified>\"}]\n\n"
        + json.dumps(items, ensure_ascii=False)
    )
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2500,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    # Strip accidental markdown fences
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def load_progress():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(simplified):
    with open(RESUME_FILE, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: set ANTHROPIC_API_KEY environment variable and re-run.")
        return

    kurals = fetch_original()
    client = anthropic.Anthropic(api_key=api_key)

    # Load any previous progress so we can resume if interrupted
    simplified = load_progress()
    already_done = len(simplified)
    if already_done:
        print(f"Resuming — {already_done} Kurals already simplified.")

    total_batches = (len(kurals) + BATCH_SIZE - 1) // BATCH_SIZE
    errors = 0

    for i in range(0, len(kurals), BATCH_SIZE):
        batch = kurals[i : i + BATCH_SIZE]
        # Skip batches already processed
        if all(str(k["number"]) in simplified for k in batch):
            continue

        batch_num = i // BATCH_SIZE + 1
        nums = f"{batch[0]['number']}–{batch[-1]['number']}"
        print(f"  Batch {batch_num}/{total_batches}  (Kurals {nums})...", end=" ", flush=True)

        for attempt in range(3):
            try:
                results = simplify_batch(client, batch)
                for r in results:
                    simplified[str(r["num"])] = {
                        "translation": r["translation"],
                        "meaning_english": r["meaning_english"],
                    }
                save_progress(simplified)
                print("done")
                break
            except Exception as e:
                wait = 2 ** attempt
                print(f"retry {attempt+1} ({e}) waiting {wait}s...", end=" ", flush=True)
                time.sleep(wait)
        else:
            print("FAILED — keeping originals for this batch")
            errors += 1
            for k in batch:
                simplified[str(k["number"])] = {
                    "translation": k["translation"],
                    "meaning_english": k["meaning_english"],
                }
            save_progress(simplified)

        # Brief pause to stay within rate limits
        time.sleep(0.4)

    # Merge simplified text back into the full kural records
    for k in kurals:
        s = simplified.get(str(k["number"]))
        if s:
            k["translation"] = s["translation"]
            k["meaning_english"] = s["meaning_english"]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(kurals, f, ensure_ascii=False, indent=2)

    # Clean up progress file on success
    if os.path.exists(RESUME_FILE):
        os.remove(RESUME_FILE)

    print(f"\nDone! {len(kurals)} Kurals written to {OUTPUT_FILE}.")
    if errors:
        print(f"  {errors} batches used original text (check output above).")
    print("\nNext steps:")
    print("  git add kurals-kids.json index.html")
    print("  git commit -m 'Add kid-friendly Kural explanations'")
    print("  git push origin main")


if __name__ == "__main__":
    main()
