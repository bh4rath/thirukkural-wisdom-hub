"""
Generates kid-friendly English translations for all 1330 Kurals.
Adds a new `translation_kids` field to each entry in kurals-kids.json.
The original `translation` field is never modified.

Usage:
    ANTHROPIC_API_KEY=sk-ant-... python3 generate_kids_translations.py

Resume-safe: already-translated kurals are skipped on re-run.
"""

import json
import os
import sys
import time

import anthropic

DATA_FILE = "kurals-kids.json"
BATCH_SIZE = 50          # kurals per API call
MODEL = "claude-haiku-4-5-20251001"   # fast + cheap for simple rewriting

SYSTEM_PROMPT = """You rewrite ancient Tamil Kural verses into plain English that a 10-year-old can easily understand.

Rules:
- Keep the core wisdom and meaning completely intact
- Use short, simple sentences (max 25 words total)
- No old-fashioned words (no: thee, thou, hath, whilst, inflicted, conjugal, eminent, aversion, etc.)
- Active voice whenever possible
- No parenthetical clarifications like (women) or (heroes)
- Sound natural, warm, and direct — like a wise older sibling explaining it
- Return ONLY the rewritten translation, nothing else"""

def make_prompt(kurals_batch):
    lines = []
    for k in kurals_batch:
        lines.append(f"KURAL_{k['number']}: {k['translation']}")
    lines.append("\nRewrite each one in the same KURAL_N: format. One per line.")
    return "\n".join(lines)

def parse_response(text, batch):
    results = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            continue
        prefix, _, content = line.partition(":")
        prefix = prefix.strip()
        if prefix.startswith("KURAL_"):
            try:
                num = int(prefix[6:])
                results[num] = content.strip()
            except ValueError:
                pass
    return results

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    with open(DATA_FILE) as f:
        data = json.load(f)

    # Find kurals that still need translation
    todo = [k for k in data if not k.get("translation_kids", "").strip()]
    done = len(data) - len(todo)
    print(f"Total: {len(data)} | Already done: {done} | To process: {len(todo)}")

    if not todo:
        print("All kurals already have kid-friendly translations. Nothing to do.")
        return

    # Build a lookup for fast updates
    index = {k["number"]: k for k in data}

    processed = 0
    errors = 0

    for i in range(0, len(todo), BATCH_SIZE):
        batch = todo[i : i + BATCH_SIZE]
        batch_nums = [k["number"] for k in batch]
        print(f"\nBatch {i//BATCH_SIZE + 1}: kurals {batch_nums[0]}–{batch_nums[-1]} ({len(batch)} kurals)...")

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": make_prompt(batch)}],
            )
            text = response.content[0].text
            results = parse_response(text, batch)

            # Apply results
            for k in batch:
                num = k["number"]
                if num in results and results[num].strip():
                    index[num]["translation_kids"] = results[num].strip()
                    processed += 1
                else:
                    print(f"  WARNING: no result for kural #{num}, keeping original")
                    index[num]["translation_kids"] = k["translation"]
                    errors += 1

            # Save after every batch so progress is never lost
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Saved. Progress: {done + processed}/{len(data)}")

            # Polite rate-limit pause between batches
            if i + BATCH_SIZE < len(todo):
                time.sleep(0.8)

        except Exception as e:
            print(f"  ERROR on batch: {e}")
            errors += 1
            time.sleep(3)
            continue

    print(f"\n=== Done ===")
    print(f"Translated: {processed} | Errors/fallbacks: {errors}")
    print(f"Output saved to {DATA_FILE}")

if __name__ == "__main__":
    main()
