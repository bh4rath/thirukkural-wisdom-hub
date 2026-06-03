#!/usr/bin/env python3
"""
Generates kurals-kids.json directly — no API key needed.
Applies systematic language modernisation + child-friendly rewriting
to all 1330 Thirukkural translations and explanations.
"""

import json, re, urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/tk120404/thirukkural/master/thirukkural.json"
OUTPUT = "kurals-kids.json"

# ── Archaic word replacements (order matters — longest first) ──────────────────
WORD_MAP = [
    # pronouns / verb forms
    (r"\bthyself\b", "yourself"),
    (r"\bthineself\b", "yourself"),
    (r"\bthine\b", "your"),
    (r"\bthy\b", "your"),
    (r"\bthou\b", "you"),
    (r"\bthee\b", "you"),
    (r"\byour own self\b", "yourself"),
    (r"\bhimself\b", "himself"),   # keep — already modern
    (r"\bhath\b", "has"),
    (r"\bhast\b", "have"),
    (r"\bdoth\b", "does"),
    (r"\bdost\b", "do"),
    (r"\bwilt\b", "will"),
    (r"\bshalt\b", "shall"),
    (r"\bwouldst\b", "would"),
    (r"\bcouldst\b", "could"),
    (r"\bshouldst\b", "should"),
    (r"\bmightest\b", "might"),
    # -eth suffix verbs → -s (seeketh→seeks etc.)
    (r"\b(\w+)eth\b", lambda m: m.group(1) + "s" if not m.group(1).endswith("s") else m.group(1)),
    # prepositions / conjunctions
    (r"\bunto\b", "to"),
    (r"\bwhither\b", "where"),
    (r"\bwhence\b", "from where"),
    (r"\bthence\b", "from there"),
    (r"\bwherein\b", "in which"),
    (r"\bwhereby\b", "by which"),
    (r"\bwhereof\b", "of which"),
    (r"\bwherewith\b", "with which"),
    (r"\bherein\b", "here"),
    (r"\bhereof\b", "of this"),
    (r"\bhereto\b", "to this"),
    (r"\bhereunto\b", "to this"),
    (r"\bhereafter\b", "from now on"),
    (r"\btherein\b", "in it"),
    (r"\bthereof\b", "of it"),
    (r"\btherewith\b", "with it"),
    (r"\bthereby\b", "by that"),
    (r"\bwithout\b", "without"),   # keep
    (r"\bwithout\b", "without"),
    (r"\bere\b", "before"),
    (r"\bforth\b", "forward"),
    (r"\bnaught\b", "nothing"),
    (r"\bnought\b", "nothing"),
    (r"\boft\b", "often"),
    (r"\bperchance\b", "perhaps"),
    (r"\bforsooth\b", "truly"),
    (r"\bverily\b", "truly"),
    (r"\bbeseech\b", "beg"),
    (r"\bwhereas\b", "while"),
    (r"\bsave\b", "except"),       # "save" = except in old usage — context risky, skip
    (r"\bnay\b", "no"),
    (r"\byea\b", "yes"),
    (r"\balbe?it\b", "even though"),
    (r"\bforthwith\b", "right away"),
    (r"\bmanifold\b", "many"),
    # complex vocabulary → simple
    (r"\bvirtue(?:s)?\b", "goodness"),
    (r"\bvirtuous(?:ly)?\b", "good"),
    (r"\brighteousness\b", "doing what is right"),
    (r"\brighteous\b", "honest and good"),
    (r"\bcelestial\b", "heavenly"),
    (r"\btemporal\b", "earthly"),
    (r"\bimperishable\b", "lasting forever"),
    (r"\bperishable\b", "not lasting"),
    (r"\bprosperity\b", "success and happiness"),
    (r"\bprosperous(?:ly)?\b", "successful"),
    (r"\bprosper\b", "do well"),
    (r"\bbenevolence\b", "kindness"),
    (r"\bbenevolent(?:ly)?\b", "kind"),
    (r"\bmagnanimity\b", "generosity"),
    (r"\bmagnanimous(?:ly)?\b", "generous"),
    (r"\bequanimity\b", "calmness"),
    (r"\bforbearance\b", "patience"),
    (r"\bfortitude\b", "bravery"),
    (r"\bprudence\b", "good judgment"),
    (r"\bprudent(?:ly)?\b", "wise"),
    (r"\bdiscernment\b", "good understanding"),
    (r"\bdiscern\b", "understand"),
    (r"\bascetic(?:s)?\b", "holy person"),
    (r"\basceticism\b", "holy life"),
    (r"\bexalted\b", "great"),
    (r"\bvain(?:ly)?\b", "useless"),
    (r"\bfruitless(?:ly)?\b", "pointless"),
    (r"\bfruitful(?:ly)?\b", "useful"),
    (r"\bconducting oneself\b", "behaving"),
    (r"\bconducting\b", "doing"),
    (r"\babstain(?:ing|s)?\b", "stay away"),
    (r"\babstinence\b", "not doing something"),
    (r"\brancou?r\b", "deep anger"),
    (r"\btreachery\b", "betrayal"),
    (r"\btreacherous(?:ly)?\b", "dishonest"),
    (r"\btransgress(?:ion|ing|s)?\b", "wrongdoing"),
    (r"\bauxiliar(?:y|ies)\b", "helper"),
    (r"\benum(?:erate|eration)\b", "list"),
    (r"\bconducive\b", "helpful"),
    (r"\bdestitute of\b", "without"),
    (r"\bdestitute\b", "very poor"),
    (r"\brenounce\b", "give up"),
    (r"\brenunciation\b", "giving up"),
    (r"\bimpudent(?:ly)?\b", "rude"),
    (r"\biniquit(?:y|ous)\b", "wrongdoing"),
    (r"\bdiscord\b", "disagreement"),
    (r"\bdiligence\b", "hard work"),
    (r"\bdiligent(?:ly)?\b", "hardworking"),
    (r"\bslothful(?:ness)?\b", "laziness"),
    (r"\bsloth\b", "laziness"),
    (r"\bliberty\b", "freedom"),
    (r"\bhumility\b", "being humble"),
    (r"\bhumble\b", "humble"),        # keep
    (r"\bfrugalit(?:y|ies)\b", "living simply"),
    (r"\bfrugal(?:ly)?\b", "careful with money"),
    (r"\bsubservient\b", "obedient"),
    (r"\bsubjugate\b", "control"),
    (r"\bvanquish\b", "defeat"),
    (r"\bconquer\b", "defeat"),       # keep — kids know "defeat"
    (r"\bsuppliant(?:s)?\b", "beggar"),
    (r"\bsojourn\b", "stay"),
    (r"\bintellect\b", "mind"),
    (r"\bintellectual\b", "of the mind"),
    (r"\bimpart\b", "give"),
    (r"\bimparted\b", "given"),
    (r"\binferior(?:s)?\b", "lesser"),
    (r"\bsuperior(?:s)?\b", "greater"),
    (r"\bpossess(?:ion|ions)?\b", "have"),
    (r"\bpossesses\b", "has"),
    (r"\bacquire(?:s|d|ing)?\b", "get"),
    (r"\bacquisition\b", "getting"),
    (r"\bconceive(?:d|s|ing)?\b", "think of"),
    (r"\bconception\b", "idea"),
    (r"\bexecution\b", "doing it"),
    (r"\bexecute\b", "do it"),
    (r"\binstruction(?:s)?\b", "teaching"),
    (r"\binstruct(?:s|ed|ing)?\b", "teach"),
    (r"\bperceive\b", "see"),
    (r"\bperception\b", "understanding"),
    (r"\benlighten(?:ed|ment)?\b", "wise"),
    (r"\bconformity\b", "fitting in"),
    (r"\bconform(?:s|ed|ing)?\b", "fit in"),
    (r"\besteem(?:ed|s)?\b", "respect"),
    (r"\bdignity\b", "respect"),
    (r"\bdignified\b", "respected"),
    (r"\bmanifest(?:s|ed|ing)?\b", "show"),
    (r"\bmanifestation\b", "showing"),
    (r"\bcomprehend\b", "understand"),
    (r"\bcomprehension\b", "understanding"),
    (r"\bdetermination\b", "strong will"),
    (r"\bdetermined\b", "determined"),  # keep
    (r"\bperseverance\b", "never giving up"),
    (r"\bpersevere(?:s|d|ing)?\b", "keep going"),
    (r"\bassiduous(?:ly)?\b", "hardworking"),
    (r"\bassiduity\b", "hard work"),
    (r"\bungrateful(?:ness)?\b", "not thankful"),
    (r"\bgratitude\b", "being thankful"),
    (r"\bgrateful(?:ly)?\b", "thankful"),
    (r"\bindolence\b", "laziness"),
    (r"\bindolent(?:ly)?\b", "lazy"),
    (r"\buprightness\b", "honesty"),
    (r"\bupright(?:ly)?\b", "honest"),
    (r"\bsincerity\b", "being honest"),
    (r"\bsincere(?:ly)?\b", "honest"),
    (r"\bfraud(?:ulent)?\b", "cheating"),
    (r"\bdeceit(?:ful)?\b", "lying"),
    (r"\bdeceitfulness\b", "being dishonest"),
    (r"\bdecieve\b", "trick"),
    (r"\bmalice\b", "hate"),
    (r"\bmalicious(?:ly)?\b", "hateful"),
    (r"\bcourage(?:ous)?\b", "bravery"),
    (r"\bcourageous(?:ly)?\b", "brave"),
    (r"\bgallantry\b", "bravery"),
    (r"\bgallant(?:ly)?\b", "brave"),
    (r"\bintelligence\b", "smartness"),
    (r"\bintelligent(?:ly)?\b", "smart"),
    (r"\bcontempt\b", "disrespect"),
    (r"\bcontemptuous(?:ly)?\b", "disrespectful"),
    (r"\bdespise(?:s|d)?\b", "look down on"),
    (r"\bdespised\b", "looked down on"),
    (r"\bglorify\b", "praise"),
    (r"\bglorious(?:ly)?\b", "wonderful"),
    (r"\bglory\b", "greatness"),
    (r"\bhonour(?:able|ably)?\b", "honor"),
    (r"\bdishonour(?:able|ably)?\b", "dishonor"),
    (r"\bwealth(?:y)?\b", "wealth"),  # keep — kids know wealth
    (r"\bstrife\b", "fighting"),
    (r"\benmity\b", "hatred"),
    (r"\benmit(?:y|ies)\b", "enemies"),
    (r"\bfoe(?:s)?\b", "enemy"),
    (r"\bhostility\b", "being enemies"),
    (r"\bhostile\b", "unfriendly"),
    (r"\bkinsman\b", "relative"),
    (r"\bkinsfolk\b", "relatives"),
    (r"\bkinsmen\b", "relatives"),
    (r"\bkinswoman\b", "relative"),
    (r"\bcounsel(?:s|ed|or)?\b", "advice"),
    (r"\bminister(?:s)?\b", "advisor"),
    (r"\bambassador(?:s)?\b", "messenger"),
    (r"\bspy\b", "spy"),  # keep
    (r"\bspies\b", "spies"),  # keep
    (r"\bfortification(?:s)?\b", "fort"),
    (r"\bfortress(?:es)?\b", "fort"),
    (r"\bweal\b", "good"),
    (r"\bwoe\b", "sadness"),
    (r"\bwoes\b", "troubles"),
    (r"\bjoy(?:ous|fully)?\b", "joy"),  # keep
    (r"\banguish\b", "pain"),
    (r"\bgrief\b", "sadness"),
    (r"\bgrieve(?:s|d|ing)?\b", "be sad"),
    (r"\blamentation\b", "crying in sadness"),
    (r"\blament(?:s|ed|ing)?\b", "be sad about"),
    (r"\bsolace\b", "comfort"),
    (r"\blanguid(?:ly)?\b", "tired and weak"),
    (r"\blanguish(?:es|ed|ing)?\b", "grow weak"),
    (r"\bpallid\b", "pale"),
    (r"\bseparation\b", "being apart"),
    (r"\bemb?race(?:s|d)?\b", "hug"),
    (r"\blonging\b", "missing someone"),
    (r"\bvexed\b", "upset"),
    (r"\bvexation\b", "being upset"),
    (r"\bdistemper\b", "illness"),
    (r"\binfirmity\b", "weakness"),
    (r"\binfirm\b", "weak"),
    (r"\binfluence\b", "effect"),
    (r"\bprofound(?:ly)?\b", "deep"),
    (r"\bprolific\b", "producing a lot"),
    (r"\bprimordial\b", "very first"),
    (r"\bprimal\b", "first"),
    (r"\boriginated\b", "started"),
    (r"\boriginate\b", "start"),
    (r"\bconstitute(?:s|d)?\b", "make up"),
    (r"\bconstitution\b", "make-up"),
    (r"\bpossession\b", "having"),
    (r"\bpossessing\b", "having"),
    (r"\bprosperity\b", "success"),
    (r"\baffluence\b", "wealth"),
    (r"\bquagmire\b", "mud swamp"),
    (r"\bquell\b", "stop"),
    (r"\bquench\b", "put out"),
    (r"\brule(?:rs?|d|ing)?\b", "rule"),  # keep
    (r"\bgover(?:n|nance|nor)\b", "govern"),  # keep
    (r"\bkingdom\b", "kingdom"),  # keep
    (r"\bsubject(?:s)?\b", "people"),
    (r"\bmonarch\b", "king"),
    (r"\bsovereign\b", "ruler"),
    (r"\bsupremacy\b", "power"),
]

SENTENCE_FIXES = [
    # Remove double spaces
    (r"  +", " "),
    # Fix "? " becoming statement
    (r"\?$", "."),
]


def apply_map(text: str, rules: list) -> str:
    for pat, repl in rules:
        if callable(repl):
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    for pat, repl in SENTENCE_FIXES:
        text = re.sub(pat, repl, text)
    # Capitalise first letter
    if text:
        text = text[0].upper() + text[1:]
    return text.strip()


def simplify_translation(original_translation: str, explanation: str) -> str:
    """
    Use the explanation (more literal) as the base for a plain one-sentence translation.
    If the explanation is already short and clear, use it directly (simplified).
    Otherwise, take the first sentence of the explanation.
    """
    exp = apply_map(explanation, WORD_MAP)
    # If explanation is already one sentence and under ~25 words, use as-is
    sentences = re.split(r'(?<=[.!?])\s+', exp.strip())
    first = sentences[0].strip()
    words = first.split()
    if len(words) <= 25 and len(words) >= 5:
        return first if first.endswith('.') else first + '.'
    # Otherwise truncate or use original translation simplified
    if len(words) > 25:
        # Truncate at 20 words
        first = ' '.join(words[:20]) + '.'
        return first
    # Fallback: simplify the original translation
    return apply_map(original_translation, WORD_MAP)


def simplify_meaning(explanation: str) -> str:
    """
    Simplify the explanation to 2-3 friendly sentences.
    """
    text = apply_map(explanation, WORD_MAP)
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    # Keep max 3 sentences
    sentences = sentences[:3]
    if not sentences:
        return text
    result = ' '.join(sentences)
    if not result.endswith(('.', '!', '?')):
        result += '.'
    return result


CHAPTERS = [
    ("கடவுள் வாழ்த்து","The Praise of God","aram"),
    ("வான் சிறப்பு","The Excellence of Rain","aram"),
    ("நீத்தார் பெருமை","The Greatness of Ascetics","aram"),
    ("அறன்வலியுறுத்தல்","Assertion of the Strength of Virtue","aram"),
    ("இல்வாழ்க்கை","Domestic Life","aram"),
    ("வாழ்க்கைத் துணைநலம்","The Goodness of the Help to Domestic Life","aram"),
    ("புதல்வரைப் பெறுதல்","The Obtaining of Sons","aram"),
    ("அன்புடைமை","The Possession of Love","aram"),
    ("விருந்தோம்பல்","Cherishing Guests","aram"),
    ("இனியவைகூறல்","The Utterance of Pleasant Words","aram"),
    ("செய்ந்நன்றியறிதல்","Gratitude","aram"),
    ("நடுவுநிலைமை","Impartiality","aram"),
    ("அடக்கமுடைமை","The Possession of Self-restraint","aram"),
    ("ஒழுக்கமுடைமை","The Possession of Decorum","aram"),
    ("பிறனில் விழையாமை","Not coveting another's wife","aram"),
    ("பொறையுடைமை","The Possession of Patience","aram"),
    ("அழுக்காறாமை","Not Envying","aram"),
    ("வெஃகாமை","Not Coveting","aram"),
    ("புறங்கூறாமை","Not Backbiting","aram"),
    ("பயனில சொல்லாமை","Not speaking unprofitable words","aram"),
    ("தீவினையச்சம்","Dread of Evil Deeds","aram"),
    ("ஒப்புரவறிதல்","Conforming to the World","aram"),
    ("ஈகை","Charity","aram"),
    ("புகழ்","Fame","aram"),
    ("அருளுடைமை","Compassion","aram"),
    ("புலான்மறுத்தல்","Abstaining from Flesh","aram"),
    ("தவம்","Penance","aram"),
    ("கூடாவொழுக்கம்","Imposture","aram"),
    ("கள்ளாமை","Not stealing","aram"),
    ("வாய்மை","Veracity","aram"),
    ("வெகுளாமை","Not being Angry","aram"),
    ("இன்னாசெய்யாமை","Not doing Evil","aram"),
    ("கொல்லாமை","Not killing","aram"),
    ("நிலையாமை","Instability","aram"),
    ("துறவு","Renunciation","aram"),
    ("மெய்யுணர்தல்","Knowledge of the True","aram"),
    ("அவாவறுத்தல்","The Extirpation of Desire","aram"),
    ("ஊழ்","Fate","aram"),
    ("இறைமாட்சி","The Greatness of a King","porul"),
    ("கல்வி","Learning","porul"),
    ("கல்லாமை","Ignorance","porul"),
    ("கேள்வி","Hearing","porul"),
    ("அறிவுடைமை","The Possession of Knowledge","porul"),
    ("குற்றங்கடிதல்","Correction of Faults","porul"),
    ("பெரியாரைத் துணைக்கோடல்","Seeking the Aid of Great Men","porul"),
    ("சிற்றினஞ்சேராமை","Avoiding Mean Associations","porul"),
    ("தெரிந்துசெயல்வகை","Acting after due Deliberation","porul"),
    ("வலியறிதல்","Knowing one's Strength","porul"),
    ("காலமறிதல்","Knowing the fitting Time","porul"),
    ("இடனறிதல்","Knowing the fitting Place","porul"),
    ("தெரிந்துதெளிதல்","Selection and Confidence","porul"),
    ("தெரிந்துவினையாடல்","Selection and Employment","porul"),
    ("சுற்றந்தழால்","Cherishing Kinsmen","porul"),
    ("பொச்சாவாமை","Not forgetting Benefits","porul"),
    ("யாதெனினும் யாரெனினும்","Not regarding Caste or Creed","porul"),
    ("தூது","Ambassadors","porul"),
    ("மன்னரைச் சேர்ந்தொழுகல்","Conduct in the Presence of the King","porul"),
    ("குறிப்பறிதல்","Knowing the King's Intention","porul"),
    ("அவையறிதல்","Knowing the Assembly","porul"),
    ("அவையஞ்சாமை","Not fearing the Assembly","porul"),
    ("நாடு","The Land","porul"),
    ("அரண்","The Fortification","porul"),
    ("பொருள்செயல்வகை","Ways of making Money","porul"),
    ("படைமாட்சி","The Excellence of the Army","porul"),
    ("படைச்செருக்கு","Military Spirit","porul"),
    ("நட்பு","Friendship","porul"),
    ("நட்பாராய்தல்","Trying Friendships","porul"),
    ("பழைமை","Old Friendship","porul"),
    ("தீ நட்பு","Evil Friendship","porul"),
    ("கூடா நட்பு","Unreal Friendship","porul"),
    ("பேதைமை","Folly","porul"),
    ("புல்லறிவாண்மை","Ignorant Men","porul"),
    ("இகல்","Hostility","porul"),
    ("பகைமாட்சி","The Excellence of Hatred","porul"),
    ("பகைத்திறந்தெரிதல்","Knowing the Quality of Hate","porul"),
    ("உட்பகை","Internal Enemies","porul"),
    ("கண்ணோட்டம்","Benevolence","porul"),
    ("வலிமடங்கல்","Timidity","porul"),
    ("மடி இன்மை","Not being Slothful","porul"),
    ("ஆள்வினையுடைமை","The Possession of Manly Effort","porul"),
    ("இடுக்கணழியாமை","Not being Disheartened by Trouble","porul"),
    ("அமைச்சு","The Prime Minister","porul"),
    ("சொல்வன்மை","Power of Speech","porul"),
    ("வினைத்தூய்மை","Purity in Action","porul"),
    ("வினைத்திட்பம்","Firmness in Action","porul"),
    ("வினை செயல்வகை","The Mode of Action","porul"),
    ("தூய்தாண்மை","Purity","porul"),
    ("ஒற்றாடல்","Spies","porul"),
    ("ஊக்கமுடைமை","Energy","porul"),
    ("மடியின்மை","Not being Slothful","porul"),
    ("ஆட்சியில் ஊக்கம்","Ruling with Energy","porul"),
    ("குடிமை","Nobility","porul"),
    ("மானம்","Honour","porul"),
    ("பெருமை","Greatness","porul"),
    ("சான்றாண்மை","Perfectness","porul"),
    ("பண்புடைமை","Courtesy","porul"),
    ("நன்றியில் செல்வம்","Wealth without Beneficence","porul"),
    ("நாணுடைமை","Modesty","porul"),
    ("குடிசெயல்வகை","How to conduct one's Family","porul"),
    ("உழவு","Agriculture","porul"),
    ("நல்குரவு","Poverty","porul"),
    ("இரவு","Begging","porul"),
    ("இரவச்சம்","The Dread of Begging","porul"),
    ("கயமை","Meanness","porul"),
    ("தகையணங்குறுத்தல்","The power of Beauty","inbam"),
    ("குறிப்பறிதல்","Recognition of the Signs of Love","inbam"),
    ("புணர்ச்சி மகிழ்தல்","The Joy of Union","inbam"),
    ("நலம்புனைந்துரைத்தல்","Praise of her Beauty","inbam"),
    ("காதற்சிறப்புரைத்தல்","The Excellence of Love","inbam"),
    ("நாணுத்துறவுரைத்தல்","Leaving Shyness Behind","inbam"),
    ("அலரறிவுறுத்தல்","Rumours about Love","inbam"),
    ("பிரிவாற்றாமை","Missing Someone","inbam"),
    ("படர்மெலிந்திரங்கல்","Sadness from Longing","inbam"),
    ("கண்விதுப்பழிதல்","Blaming the Eyes","inbam"),
    ("பசப்புறுபருவரல்","Turning Pale from Longing","inbam"),
    ("தனிப்படர்மிகுதி","Loneliness when Separated","inbam"),
    ("நினைந்தவர்புலம்பல்","Thinking of the Loved One","inbam"),
    ("கனவுநிலையுரைத்தல்","The Comfort of Dreams","inbam"),
    ("பொழுதுகண்டிரங்கல்","Sadness at Nightfall","inbam"),
    ("உறுப்புநலனழிதல்","Losing Beauty from Sadness","inbam"),
    ("நெஞ்சொடுகிளத்தல்","Talking to One's Heart","inbam"),
    ("நிறையழிதல்","Losing Self-control","inbam"),
    ("அவர்வயின்விதும்பல்","Longing for the Loved One","inbam"),
    ("குறிப்பினைக் கூட்டம்","A Secret Meeting","inbam"),
    ("புலவி","Sulking","inbam"),
    ("புலவி நுணுக்கம்","The Subtlety of Sulking","inbam"),
    ("ஊடலுவகை","The Joy of Making Up","inbam"),
]


def main():
    print("Downloading original data...")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        data = json.loads(r.read())
    raw = data.get("kural", data)
    print(f"  Loaded {len(raw)} Kurals.")

    kurals_out = []
    for i, k in enumerate(raw):
        num = i + 1
        ch_idx = (num - 1) // 10
        ch = CHAPTERS[ch_idx] if ch_idx < len(CHAPTERS) else ("", "", "aram")

        original_trans = k.get("Translation", "") or ""
        original_exp   = k.get("explanation", "") or ""
        mk_tamil       = k.get("mk", "") if isinstance(k.get("mk"), str) else ""

        new_trans = simplify_translation(original_trans, original_exp)
        new_exp   = simplify_meaning(original_exp)

        kurals_out.append({
            "number": num,
            "line1": k.get("Line1", ""),
            "line2": k.get("Line2", ""),
            "transliteration1": k.get("transliteration1", ""),
            "transliteration2": k.get("transliteration2", ""),
            "translation": new_trans,
            "meaning_tamil": mk_tamil,
            "meaning_english": new_exp,
            "chapter_number": ch_idx + 1,
            "chapter_tamil": ch[0],
            "chapter_english": ch[1],
            "book": ch[2],
        })

        if num % 100 == 0:
            print(f"  Processed {num}/1330...")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(kurals_out, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Wrote {len(kurals_out)} Kurals to {OUTPUT}")
    print("\nSample check (Kurals 1, 100, 500, 1000):")
    for k in kurals_out:
        if k["number"] in (1, 100, 500, 1000):
            print(f"\n  #{k['number']}")
            print(f"  T: {k['translation']}")
            print(f"  E: {k['meaning_english']}")


if __name__ == "__main__":
    main()
