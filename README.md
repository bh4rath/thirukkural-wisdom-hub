# Thirukkural: 2,000 Years of Wisdom

A clean, fast, fully offline-capable reading experience for the **Thirukkural** — a 2,000-year-old Tamil classic composed by Thiruvalluvar. All 1,330 couplets across 133 chapters and 3 books, in Tamil with transliteration, English translation, and plain-language explanations.

Live: **https://bh4rath.github.io/thirukkural-wisdom-hub/**

---

## What it does

| Feature | Detail |
|---|---|
| Browse all 1,330 Kurals | Organized into 3 books → 133 chapters → 10 Kurals each |
| Tamil + transliteration | Every couplet shown in Tamil script with Roman transliteration |
| Plain-English explanations | Kid-friendly translations generated with Claude AI |
| Search | Live search across Tamil text, English translations, and chapter names |
| Dark / Light theme | Auto-detects system preference; manually toggleable |
| Font size controls | Three-step A− / A / A+ control for accessibility |
| Reading progress | Tracks which Kurals you've read via localStorage |
| Vivid book-color system | Aram (green), Porul (orange), Inbam (pink) — consistent across every card, badge, and filter |
| Browser history navigation | Back/forward buttons work exactly as expected |

Everything runs in a **single `index.html` file** — no framework, no build step, no server required.

---

## Who it's for

- Tamil culture enthusiasts who want a clean reading interface
- Students studying the Thirukkural in school or at home
- Parents and educators looking for accessible English explanations
- Anyone curious about ancient Tamil philosophy

---

## Run it locally

```bash
# Clone
git clone https://github.com/bh4rath/thirukkural-wisdom-hub.git
cd thirukkural-wisdom-hub

# Serve (any static server works)
python3 -m http.server 8080
# then open http://localhost:8080
```

No dependencies to install. The Kural data is bundled in `kurals-kids.json` — the site works fully offline once the page has loaded.

If `kurals-kids.json` is missing, the site automatically falls back to fetching data from the open-source [tk120404/thirukkural](https://github.com/tk120404/thirukkural) repository.

---

## Project structure

```
index.html              # The entire app — HTML, CSS, and JS in one file
kurals-kids.json        # Pre-generated Kural data with plain-English explanations
generate_kids_kurals.py # Script that produced kurals-kids.json using Claude API
prepare_batches.py      # Helper: chunks Kural data into prompt batches
merge_responses.py      # Helper: merges batch responses into kurals-kids.json
simplify_rules.py       # Helper: post-processes explanations
batch_0*.txt            # Saved prompt batches (reference)
```

### Regenerating `kurals-kids.json`

The plain-English explanations were written by Claude. To regenerate:

```bash
pip install anthropic
ANTHROPIC_API_KEY=sk-ant-... python3 generate_kids_kurals.py
```

Or use the manual batch workflow: run `prepare_batches.py`, paste each `batch_0N.txt` into claude.ai, save responses as `response_0N.txt`, then run `merge_responses.py`.

---

## What's coming next

- **Audio** — Pronunciation recordings for each Tamil couplet
- **Mobile app** — PWA manifest + service worker for true offline/installable experience  
- **Commentary mode** — Classical commentaries by Parimelazhakar side-by-side with modern translations
- **Daily Kural** — A featured Kural on the home screen that rotates each day
- **Share card** — One-tap image card for sharing a Kural to social media
- **Verse-level bookmarks** — Pin favourite Kurals and export your reading list

---

## Data & credits

- Kural text: [tk120404/thirukkural](https://github.com/tk120404/thirukkural) (open source)
- Plain-English explanations: generated with [Claude](https://claude.ai) (Anthropic)
- Built by **Bharath S** · She Vibes AI Cohort 2026
- No trackers · No ads · No cookies (only localStorage for your preferences)
