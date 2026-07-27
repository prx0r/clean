#!/usr/bin/env python3
"""Match top 2 artworks to each of 56 video titles using concept/tag overlap."""

import json

with open("/tmp/art_aggregated_complete.json") as f:
    artworks = json.load(f)

# Domain categories mapped to image metadata
DOMAINS = {
    "alchemical": {
        "concepts": ["Transformation", "Beauty", "Purification", "Sacred Matter", "Conjunction", "Energy", "Union of Opposites", "Stability"],
        "motifs": ["alchemical_scroll", "laboratory", "mercury", "caduceus", "seven_metals", "green_lion", "vessel", "distillation", "spagyric"],
        "entities": ["alchemist", "laboratory", "mercury_god", "green_lion", "alembic"],
        "moods": ["mystical", "contemplative"],
        "mood_boost": True,
    },
    "cosmic": {
        "concepts": ["Cosmology", "Celestial Spheres", "Macrocosm", "Microcosm", "Astrology", "Unity", "Correspondence", "Divine Order"],
        "motifs": ["cosmos", "macrocosm", "sun", "stars", "astrology", "planetary", "celestial", "mountain"],
        "entities": ["macrocosm", "microcosm", "astrologer", "zodiac", "planet", "sun_rays"],
        "moods": ["cosmic", "visionary", "mystical"],
    },
    "angelic": {
        "concepts": ["Angel", "Annunciation", "Revelation", "Theophany", "Active Imagination", "Mundus Imaginalis", "Perfect Nature", "Celestial Counterpart", "Guidance"],
        "motifs": ["angel", "light_ray", "light"],
        "entities": ["angel"],
        "moods": ["visionary", "illuminated", "sacred"],
    },
    "visionary": {
        "concepts": ["Imagination", "Imaginal World", "Perception", "Theophany", "Creative Imagination", "Vision", "Active Imagination", "Mundus Imaginalis"],
        "motifs": ["emblem", "symbol", "light", "light_ray"],
        "entities": ["allegorical_figure"],
        "moods": ["visionary", "symbolic", "illuminated", "illuminatory"],
    },
    "illumination": {
        "concepts": ["Ascent", "Liberation", "Radiant Body", "Theophany", "Light"],
        "motifs": ["light_ray", "light", "sun"],
        "entities": ["sun_rays", "light"],
        "moods": ["illuminated", "illuminatory", "visionary"],
    },
    "soul": {
        "concepts": ["Beauty", "Unity", "Divine Love", "Divine Power", "Divine Order", "Perception", "Stability"],
        "motifs": ["emblem", "symbol", "rose_cross", "rose"],
        "entities": ["allegorical_figure"],
        "moods": ["contemplative", "sacred", "mystical"],
    },
    "death": {
        "concepts": ["Transformation", "Purification", "Sacred Matter"],
        "motifs": ["darkness"],
        "moods": ["austere", "mystical", "contemplative"],
    },
    "oracle": {
        "concepts": ["Revelation", "Prophetic Vision", "Angel", "Annunciation", "Divine Power"],
        "motifs": ["angel", "light_ray"],
        "entities": ["angel"],
        "moods": ["visionary", "sacred", "mystical"],
    },
    "fire": {
        "concepts": ["Transformation", "Purification", "Sacred Matter", "Energy"],
        "motifs": ["sun", "light_ray", "light"],
        "entities": ["sun_rays"],
        "moods": ["illuminated", "visionary"],
    },
    "magic": {
        "concepts": ["Transformation", "Imagination", "Creative Imagination", "Artist Magician", "Himma"],
        "motifs": ["emblem", "symbol", "circle"],
        "entities": ["allegorical_figure"],
        "moods": ["mystical", "visionary"],
    },
    "dream": {
        "concepts": ["Imagination", "Imaginal World", "Perception", "Vision", "Active Imagination", "Mundus Imaginalis"],
        "motifs": ["emblem", "symbol"],
        "moods": ["visionary", "symbolic"],
    },
    "buddhist": {
        "concepts": ["Liberation", "Unity", "Perception"],
        "motifs": ["lotus", "buddha", "mandala"],
        "moods": ["contemplative", "sacred", "mystical"],
    },
    "nature": {
        "concepts": ["Sacred Matter", "Transformation", "Stability"],
        "motifs": ["earth", "mountain", "tree", "green_lion"],
        "entities": ["stone", "mountain", "philosophical_tree", "green_lion"],
        "moods": ["contemplative", "mystical", "austere"],
    },
    "self": {
        "concepts": ["Beauty", "Perception", "Unity", "Imagination", "Conjunction"],
        "motifs": ["emblem", "symbol", "rose_cross", "rose"],
        "entities": ["allegorical_figure"],
        "moods": ["contemplative", "mystical"],
    },
    "god": {
        "concepts": ["Divine Power", "Divine Love", "Divine Order", "Theophany", "Creation", "Cosmology"],
        "motifs": ["light_ray", "light", "sun"],
        "moods": ["sacred", "visionary", "contemplative"],
    },
}

# Map each video to domains + specific keywords
VIDEOS = [
    (1, "The Engine of Consciousness", ["alchemical", "cosmic", "illumination"], ["consciousness", "vibration", "energy", "light", "shiva", "shakti", "spanda"]),
    (2, "Why You Feel Small", ["cosmic"], ["cosmos", "macrocosm", "vast", "stars", "universe", "sublime", "human", "microcosm", "celestial", "awe"]),
    (3, "Remember Enlightenment?", ["buddhist", "illumination", "visionary"], ["enlightenment", "buddha", "liberation", "awakening", "illumination", "light", "meditation", "awareness"]),
    (4, "The Path You Didn't Choose", ["alchemical", "visionary"], ["path", "journey", "threshold", "initiatory", "gate", "pilgrim", "way", "crossroads"]),
    (5, "Why Pain Is Actually Beautiful", ["alchemical", "death"], ["suffering", "transformation", "nigredo", "dark", "fire", "purification", "sacrifice", "beauty"]),
    (6, "Real as the Mirror", ["self", "visionary"], ["mirror", "reflection", "reality", "image", "truth", "vision", "face", "appearance", "maya"]),
    (7, "How Light Becomes You", ["illumination", "angelic", "god"], ["light", "embodiment", "incarnation", "radiance", "sun", "form", "descent", "glory", "theophany"]),
    (8, "Why Some People Wake Up Overnight", ["illumination", "visionary", "buddhist"], ["awakening", "sudden", "grace", "initiation", "transmission", "realization", "recognition"]),
    (9, "The Companion You've Had Since Birth", ["angelic", "oracle"], ["daimon", "guardian", "angel", "companion", "spirit", "guide", "soul", "birth", "destiny", "protector"]),
    (10, "The Death Everyone Forgets", ["death", "alchemical"], ["death", "afterlife", "passage", "soul", "rebirth", "transition", "underworld", "mortality"]),
    (11, "The Universe Is a Mirror", ["cosmic", "god"], ["cosmos", "mirror", "macrocosm", "reflection", "correspondence", "harmony", "divine", "creation"]),
    (12, "The World Between Worlds", ["visionary", "angelic", "dream"], ["imaginal", "intermediate", "visionary", "celestial", "mystical", "threshold", "realm", "dream", "symbolic"]),
    (13, "The Secret Life of Matter", ["alchemical", "nature"], ["matter", "element", "nature", "mineral", "stone", "earth", "transformation", "body", "substance", "alchemy"]),
    (14, "The God Who Needs You", ["god", "angelic"], ["god", "divine", "theurgy", "participation", "creation", "human", "relationship", "love", "partnership"]),
    (15, "The Light That Illuminates Itself", ["illumination", "self"], ["light", "self", "awareness", "consciousness", "luminous", "sun", "radiance", "knowledge", "gnosis"]),
    (16, "The Dream That You Are", ["dream", "visionary"], ["dream", "vision", "sleep", "consciousness", "reality", "illusion", "maya", "awakening", "imagination"]),
    (17, "When the Gods Speak", ["oracle", "angelic"], ["oracle", "prophecy", "voice", "god", "divine", "revelation", "inspiration", "muse", "message"]),
    (18, "The Body You Cannot See", ["illumination", "alchemical"], ["subtle", "energy", "chakra", "spirit", "aura", "etheric", "astral", "light", "invisible", "inner"]),
    (19, "The Battle You Are Fighting", ["alchemical", "self"], ["battle", "warrior", "struggle", "hero", "conflict", "dragon", "serpent", "combat", "victory"]),
    (20, "Everything Is Empty", ["buddhist", "cosmic"], ["emptiness", "shunyata", "void", "buddha", "nothingness", "form", "impermanence", "wisdom", "nondual"]),
    (21, "The Eight Limbs", ["buddhist", "alchemical"], ["yoga", "asana", "meditation", "eight", "limb", "path", "practice", "discipline", "body"]),
    (22, "The Mind of the Universe", ["cosmic", "god"], ["cosmic", "mind", "intelligence", "universal", "logos", "reason", "order", "creation", "wisdom", "nous"]),
    (23, "The Journey Everyone Must Take", ["death", "alchemical", "visionary"], ["journey", "pilgrim", "path", "death", "hero", "quest", "soul", "way", "transformation"]),
    (24, "The Fire You're Already Burning In", ["fire", "alchemical"], ["fire", "flame", "heat", "passion", "transformation", "alchemy", "burning", "light", "sacrifice"]),
    (25, "The Forgotten Oracles", ["oracle", "visionary"], ["oracle", "prophecy", "ancient", "sibyl", "temple", "mystery", "hidden", "knowledge", "wisdom", "forgotten"]),
    (26, "The Reality You Create Every Night", ["dream", "visionary"], ["dream", "sleep", "creation", "consciousness", "night", "vision", "reality", "mind"]),
    (27, "The Law That Explains Everything", ["cosmic", "god"], ["law", "order", "cosmic", "universal", "correspondence", "harmony", "principle", "truth"]),
    (28, "The Self You Cannot Find", ["self", "visionary"], ["self", "soul", "search", "quest", "introspection", "mirror", "face", "identity", "spirit"]),
    (29, "The Self You Become While Sleeping", ["dream", "self"], ["dream", "sleep", "astral", "soul", "journey", "night", "consciousness", "spirit", "travel"]),
    (30, "The Psyche Has No Walls", ["soul", "self"], ["psyche", "soul", "mind", "infinite", "boundless", "unconscious", "depth", "expansive", "spirit"]),
    (31, "The Two Mountains That See the Same Dawn", ["cosmic", "nature"], ["mountain", "twin", "nondual", "unity", "dawn", "sun", "ascent", "summit", "perspective"]),
    (32, "The Art and Science of Causing Change", ["magic", "alchemical"], ["magic", "will", "transformation", "power", "change", "art", "wisdom", "knowledge", "hermetic"]),
    (33, "The Sun That Knows Itself", ["illumination", "cosmic", "self"], ["sun", "light", "self", "consciousness", "radiance", "illumination", "knowledge", "star"]),
    (34, "The Evolution You Haven't Heard Of", ["cosmic", "soul"], ["evolution", "consciousness", "transformation", "development", "soul", "journey", "becoming", "emergence"]),
    (35, "The Prayers That Move the Cosmos", ["cosmic", "angelic", "god"], ["prayer", "cosmos", "invocation", "worship", "devotion", "angel", "divine", "celestial", "mystical"]),
    (36, "The Angel You Already Are", ["angelic", "soul"], ["angel", "daimon", "spirit", "soul", "divine", "messenger", "light", "wing", "celestial", "human"]),
    (37, "The Dream That Knows You", ["dream", "angelic"], ["dream", "consciousness", "daimon", "awareness", "vision", "soul", "night", "encounter"]),
    (38, "The Man Who Thought Himself Free", ["buddhist", "self"], ["freedom", "liberation", "illusion", "bondage", "awakening", "chains", "enlightenment", "truth"]),
    (39, "The Journey You're Already On", ["visionary", "alchemical"], ["journey", "path", "pilgrim", "quest", "soul", "way", "traveler", "discovery"]),
    (40, "Voices That Speak", ["oracle", "angelic"], ["voice", "daimon", "angel", "inspiration", "muse", "prophecy", "oracle", "spirit", "message"]),
    (41, "The Companion That Tests You", ["angelic", "death"], ["daimon", "trial", "test", "challenge", "guide", "guardian", "spirit", "companion", "initiation"]),
    (42, "The Voice That Only Says No", ["death", "self"], ["daimon", "negation", "shadow", "obstacle", "resistance", "dark", "limit", "boundary", "voice"]),
    (43, "The Body You Travel In", ["soul", "alchemical"], ["body", "vehicle", "astral", "soul", "spirit", "travel", "vessel", "incarnation", "light"]),
    (44, "The Operation", ["magic", "alchemical"], ["theurgy", "ritual", "operation", "magic", "ceremony", "sacred", "transformation", "invocation", "circle"]),
    (45, "The Daimon in the Spine", ["alchemical", "illumination"], ["kundalini", "serpent", "spine", "energy", "awakening", "chakra", "daimon", "ascent", "light"]),
    (46, "The Stones That Know", ["nature", "alchemical"], ["stone", "mineral", "alchemy", "earth", "ancient", "element", "crystal", "rock", "nature"]),
    (47, "The Being of Light Before You", ["angelic", "illumination", "god"], ["angel", "light", "being", "divine", "vision", "theophany", "presence", "radiance"]),
    (48, "The Bodies You Cannot See", ["illumination", "soul"], ["subtle", "energy", "spirit", "aura", "astral", "etheric", "invisible", "light", "soul"]),
    (49, "Why the Gods Need You", ["god", "angelic"], ["god", "divine", "theurgy", "human", "participation", "sacred", "partnership", "ritual", "need"]),
    (50, "The Stars Are in Your Blood", ["cosmic", "soul"], ["stars", "cosmos", "astrology", "celestial", "fate", "destiny", "constellation", "birth", "heaven"]),
    (51, "The Beauty That Does Not Fade", ["soul", "angelic", "god"], ["beauty", "eternal", "soul", "angel", "light", "transcendent", "divine", "love", "radiance"]),
    (52, "The God Who Longs to Be Known", ["god", "soul"], ["god", "love", "desire", "knowledge", "divine", "creation", "emanation", "theophany", "yearning"]),
    (53, "The Soul at the Center of Everything", ["soul", "cosmic"], ["soul", "center", "cosmos", "universe", "heart", "divine", "essence", "core", "world_soul"]),
    (54, "The Universe Has a Soul", ["cosmic", "soul"], ["world_soul", "cosmos", "soul", "nature", "living", "divine", "creation", "life", "organism"]),
    (55, "Before the Earth Was Earth", ["cosmic", "nature"], ["creation", "primordial", "beginning", "origin", "cosmos", "chaos", "elements", "formation", "ancient"]),
    (56, "The Choice Before You Were Born", ["soul", "cosmic"], ["choice", "soul", "destiny", "birth", "fate", "incarnation", "purpose", "plan", "eternity"]),
]


def compute_domain_score(art, domains):
    score = 0.0
    for domain_name in domains:
        domain = DOMAINS.get(domain_name)
        if not domain:
            continue
        # Check concepts
        for concept_field in ["concepts", "visual_motifs", "mood", "entities_depicted"]:
            domain_tags = domain.get(concept_field, [])
            if not domain_tags:
                continue
            art_tags = [t.strip().lower() for t in art.get(concept_field, []) if t and t.strip()]
            for dt in domain_tags:
                dtl = dt.lower()
                for at in art_tags:
                    if dtl == at:
                        score += 5
                    elif dtl in at or at in dtl:
                        score += 3
        # Mood bonus
        if domain.get("mood_boost"):
            if any(m.strip().lower() in [x.strip().lower() for x in art.get("mood", [])] for m in ["mystical", "contemplative"]):
                score += 1
    return score


def score_image(art, domains, keywords):
    score = compute_domain_score(art, domains)

    text_bodies = []
    fields = ["concepts", "visual_motifs", "style", "mood", "entities_depicted"]
    for field in fields:
        for item in art.get(field, []):
            item = item.strip()
            if item:
                text_bodies.append(item.lower())
    palette = art.get("color_palette", [])
    if isinstance(palette, list):
        for p in palette:
            if p and p.strip():
                text_bodies.append(p.lower())
    elif palette:
        text_bodies.append(str(palette).lower())
    if art.get("title"):
        text_bodies.append(art["title"].lower())
    if art.get("notes"):
        text_bodies.append(art["notes"].lower())
    if art.get("composition"):
        text_bodies.append(art["composition"].lower())

    combined = " ".join(text_bodies)
    for kw in keywords:
        kw_lower = kw.lower()
        count = combined.count(kw_lower)
        if count > 0:
            score += count * 2
        if kw_lower in combined:
            score += 1

    return round(score, 1)


def describe_image(art):
    parts = []
    c = [x for x in art.get("concepts", []) if x.strip()]
    if c:
        parts.append(f"concepts: {', '.join(c[:4])}")
    m = [x for x in art.get("visual_motifs", []) if x.strip()]
    if m:
        parts.append(f"motifs: {', '.join(m[:3])}")
    d = [x for x in art.get("mood", []) if x.strip()]
    if d:
        parts.append(f"mood: {', '.join(d[:3])}")
    return " | ".join(parts) if parts else "(no structured metadata)"


print("Matching 56 videos against 348 artworks...\n")

for num, title, domains, keywords in VIDEOS:
    scored = [(score_image(art, domains, keywords), art) for art in artworks]
    scored.sort(key=lambda x: -x[0])
    top = scored[:2]

    print(f"\n{'='*65}")
    print(f"  {num:2d}. {title}")
    print(f"  Domains: {', '.join(domains)}")
    print(f"{'='*65}")
    for i, (score, art) in enumerate(top):
        path = art.get("_resolved_path", "?")
        desc = describe_image(art)
        print(f"\n  #{i+1} (score: {score})")
        print(f"  {art['id']}")
        print(f"  \"{art['title'][:80]}\"")
        print(f"  {desc}")
        print(f"  Path: {path}")
    if top and top[0][0] < 3:
        print(f"  ⚠ Low scores ({top[0][0]}) — consider curated picks")

print("\nDone.")
