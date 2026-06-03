#!/usr/bin/env python3
"""
Step 2 of 2.
Reads response_01.txt … response_07.txt (Claude's JSON output from claude.ai),
merges them with the original Kural data, and writes kurals-kids.json.
"""

import glob
import json
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/tk120404/thirukkural/master/thirukkural.json"
OUTPUT_FILE = "kurals-kids.json"

def fetch_raw():
    print("Downloading original Kural data...")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        data = json.loads(r.read())
    return data.get("kural", data)

def load_responses():
    simplified = {}
    files = sorted(glob.glob("response_*.txt"))
    if not files:
        print("ERROR: No response_*.txt files found.")
        print("  Save Claude's JSON responses as response_01.txt, response_02.txt, etc.")
        return None

    for fname in files:
        with open(fname, encoding="utf-8") as f:
            text = f.read().strip()

        # Strip accidental markdown fences if Claude added them
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        try:
            batch = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  ERROR parsing {fname}: {e}")
            print(f"  Fix the JSON in {fname} and re-run.")
            return None

        for item in batch:
            simplified[item["num"]] = {
                "translation": item["translation"],
                "meaning_english": item["meaning_english"],
            }
        print(f"  Loaded {len(batch)} Kurals from {fname}")

    return simplified

def main():
    raw = fetch_raw()
    simplified = load_responses()
    if simplified is None:
        return

    missing = [i + 1 for i in range(1330) if (i + 1) not in simplified]
    if missing:
        print(f"\nWARNING: {len(missing)} Kurals not found in responses: {missing[:10]}{'...' if len(missing) > 10 else ''}")
        print("  These will use the original text.")

    CHAPTERS = [
        ("கடவுள் வாழ்த்து","The Praise of God","aram"),("வான் சிறப்பு","The Excellence of Rain","aram"),
        ("நீத்தார் பெருமை","The Greatness of Ascetics","aram"),("அறன்வலியுறுத்தல்","Assertion of the Strength of Virtue","aram"),
        ("இல்வாழ்க்கை","Domestic Life","aram"),("வாழ்க்கைத் துணைநலம்","The Goodness of the Help to Domestic Life","aram"),
        ("புதல்வரைப் பெறுதல்","The Obtaining of Sons","aram"),("அன்புடைமை","The Possession of Love","aram"),
        ("விருந்தோம்பல்","Cherishing Guests","aram"),("இனியவைகூறல்","The Utterance of Pleasant Words","aram"),
        ("செய்ந்நன்றியறிதல்","Gratitude","aram"),("நடுவுநிலைமை","Impartiality","aram"),
        ("அடக்கமுடைமை","The Possession of Self-restraint","aram"),("ஒழுக்கமுடைமை","The Possession of Decorum","aram"),
        ("பிறனில் விழையாமை","Not coveting another's wife","aram"),("பொறையுடைமை","The Possession of Patience","aram"),
        ("அழுக்காறாமை","Not Envying","aram"),("வெஃகாமை","Not Coveting","aram"),
        ("புறங்கூறாமை","Not Backbiting","aram"),("பயனில சொல்லாமை","Not speaking unprofitable words","aram"),
        ("தீவினையச்சம்","Dread of Evil Deeds","aram"),("ஒப்புரவறிதல்","Conforming to the World","aram"),
        ("ஈகை","Charity","aram"),("புகழ்","Fame","aram"),
        ("அருளுடைமை","Compassion","aram"),("புலான்மறுத்தல்","Abstaining from Flesh","aram"),
        ("தவம்","Penance","aram"),("கூடாவொழுக்கம்","Imposture","aram"),
        ("கள்ளாமை","Not stealing","aram"),("வாய்மை","Veracity","aram"),
        ("வெகுளாமை","Not being Angry","aram"),("இன்னாசெய்யாமை","Not doing Evil","aram"),
        ("கொல்லாமை","Not killing","aram"),("நிலையாமை","Instability","aram"),
        ("துறவு","Renunciation","aram"),("மெய்யுணர்தல்","Knowledge of the True","aram"),
        ("அவாவறுத்தல்","The Extirpation of Desire","aram"),("ஊழ்","Fate","aram"),
        ("இறைமாட்சி","The Greatness of a King","porul"),("கல்வி","Learning","porul"),
        ("கல்லாமை","Ignorance","porul"),("கேள்வி","Hearing","porul"),
        ("அறிவுடைமை","The Possession of Knowledge","porul"),("குற்றங்கடிதல்","Correction of Faults","porul"),
        ("பெரியாரைத் துணைக்கோடல்","Seeking the Aid of Great Men","porul"),("சிற்றினஞ்சேராமை","Avoiding Mean Associations","porul"),
        ("தெரிந்துசெயல்வகை","Acting after due Deliberation","porul"),("வலியறிதல்","Knowing one's Strength","porul"),
        ("காலமறிதல்","Knowing the fitting Time","porul"),("இடனறிதல்","Knowing the fitting Place","porul"),
        ("தெரிந்துதெளிதல்","Selection and Confidence","porul"),("தெரிந்துவினையாடல்","Selection and Employment","porul"),
        ("சுற்றந்தழால்","Cherishing Kinsmen","porul"),("பொச்சாவாமை","Not forgetting Benefits","porul"),
        ("யாதெனினும் யாரெனினும்","Not regarding Caste or Creed","porul"),("தூது","Ambassadors","porul"),
        ("மன்னரைச் சேர்ந்தொழுகல்","Conduct in the Presence of the King","porul"),("குறிப்பறிதல்","Knowing the King's Intention","porul"),
        ("அவையறிதல்","Knowing the Assembly","porul"),("அவையஞ்சாமை","Not fearing the Assembly","porul"),
        ("நாடு","The Land","porul"),("அரண்","The Fortification","porul"),
        ("பொருள்செயல்வகை","Ways of making Money","porul"),("படைமாட்சி","The Excellence of the Army","porul"),
        ("படைச்செருக்கு","Military Spirit","porul"),("நட்பு","Friendship","porul"),
        ("நட்பாராய்தல்","Trying Friendships","porul"),("பழைமை","Old Friendship","porul"),
        ("தீ நட்பு","Evil Friendship","porul"),("கூடா நட்பு","Unreal Friendship","porul"),
        ("பேதைமை","Folly","porul"),("புல்லறிவாண்மை","Ignorant Men","porul"),
        ("இகல்","Hostility","porul"),("பகைமாட்சி","The Excellence of Hatred","porul"),
        ("பகைத்திறந்தெரிதல்","Knowing the Quality of Hate","porul"),("உட்பகை","Internal Enemies","porul"),
        ("கண்ணோட்டம்","Benevolence","porul"),("வலிமடங்கல்","Timidity","porul"),
        ("மடி இன்மை","Not being Slothful","porul"),("ஆள்வினையுடைமை","The Possession of Manly Effort","porul"),
        ("இடுக்கணழியாமை","Not being Disheartened by Trouble","porul"),("அமைச்சு","The Prime Minister","porul"),
        ("சொல்வன்மை","Power of Speech","porul"),("வினைத்தூய்மை","Purity in Action","porul"),
        ("வினைத்திட்பம்","Firmness in Action","porul"),("வினை செயல்வகை","The Mode of Action","porul"),
        ("தூய்தாண்மை","Purity","porul"),("ஒற்றாடல்","Spies","porul"),
        ("ஊக்கமுடைமை","Energy","porul"),("மடியின்மை","Not being Slothful","porul"),
        ("ஆட்சியில் ஊக்கம்","Ruling with Energy","porul"),("குடிமை","Nobility","porul"),
        ("மானம்","Honour","porul"),("பெருமை","Greatness","porul"),
        ("சான்றாண்மை","Perfectness","porul"),("பண்புடைமை","Courtesy","porul"),
        ("நன்றியில் செல்வம்","Wealth without Beneficence","porul"),("நாணுடைமை","Modesty","porul"),
        ("குடிசெயல்வகை","How to conduct one's Family","porul"),("உழவு","Agriculture","porul"),
        ("நல்குரவு","Poverty","porul"),("இரவு","Begging","porul"),
        ("இரவச்சம்","The Dread of Begging","porul"),("கயமை","Meanness","porul"),
        ("தகையணங்குறுத்தல்","The pre-eminence of the strength of Beauty","inbam"),("குறிப்பறிதல்","Recognition of the Signs of Love","inbam"),
        ("புணர்ச்சி மகிழ்தல்","The Rejoicing at the Embrace","inbam"),("நலம்புனைந்துரைத்தல்","The Praise of her Beauty","inbam"),
        ("காதற்சிறப்புரைத்தல்","Declaration of Love's special Excellence","inbam"),("நாணுத்துறவுரைத்தல்","Renunciation of Reserve","inbam"),
        ("அலரறிவுறுத்தல்","The Announcement of the Rumour","inbam"),("பிரிவாற்றாமை","Intolerance of Separation","inbam"),
        ("படர்மெலிந்திரங்கல்","The Languishing under Desire","inbam"),("கண்விதுப்பழிதல்","The Blame of the Eye","inbam"),
        ("பசப்புறுபருவரல்","The Pallid Hue and the Anguish","inbam"),("தனிப்படர்மிகுதி","The Increased Loneliness of the Separated","inbam"),
        ("நினைந்தவர்புலம்பல்","The Grief of the Separated one thinking of his Love","inbam"),("கனவுநிலையுரைத்தல்","The Solace of the Dream","inbam"),
        ("பொழுதுகண்டிரங்கல்","Bemoaning one's Lot at Nightfall","inbam"),("உறுப்புநலனழிதல்","The Fading of Beauty","inbam"),
        ("நெஞ்சொடுகிளத்தல்","Talking to one's own Heart","inbam"),("நிறையழிதல்","Broken Chastity","inbam"),
        ("அவர்வயின்விதும்பல்","Longing for the Beloved","inbam"),("குறிப்பினைக் கூட்டம்","The Meeting by Stealth","inbam"),
        ("புலவி","Sulking","inbam"),("புலவி நுணுக்கம்","The Subtlety of Sulking","inbam"),
        ("ஊடலுவகை","The Pleasures of temporary Variance","inbam"),
    ]

    kurals_out = []
    for i, k in enumerate(raw):
        num = i + 1
        ch_num = (num - 1) // 10
        ch = CHAPTERS[ch_num] if ch_num < len(CHAPTERS) else ("", "", "aram")
        s = simplified.get(num, {})
        kurals_out.append({
            "number": num,
            "line1": k.get("Line1", ""),
            "line2": k.get("Line2", ""),
            "transliteration1": k.get("transliteration1", ""),
            "transliteration2": k.get("transliteration2", ""),
            "translation": s.get("translation") or k.get("Translation", ""),
            "meaning_tamil": k.get("mk", "") if isinstance(k.get("mk"), str) else "",
            "meaning_english": s.get("meaning_english") or k.get("explanation", ""),
            "chapter_number": ch_num + 1,
            "chapter_tamil": ch[0],
            "chapter_english": ch[1],
            "book": ch[2],
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(kurals_out, f, ensure_ascii=False, indent=2)

    simplified_count = sum(1 for k in kurals_out if k["number"] in simplified)
    print(f"\nWrote {len(kurals_out)} Kurals to {OUTPUT_FILE}")
    print(f"  {simplified_count} have kid-friendly text, {len(missing)} use original text.")
    print("\nNext steps:")
    print("  git add kurals-kids.json")
    print("  git commit -m 'Add kid-friendly English for all 1330 Kurals'")
    print("  git push origin main")

if __name__ == "__main__":
    main()
