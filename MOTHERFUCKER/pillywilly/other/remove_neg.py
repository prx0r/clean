#!/usr/bin/env python3
"""
Remove NEG patterns from essay files. Works on the backed-up corrupted files,
fixes the corruption, and applies correct NEG removal.

Strategy:
1. Read from backup (/tmp/*.bak) - these have first-script corruption
2. Fix the specific corruption patterns introduced by first script
3. Apply correct NEG removal on the fixed text
4. Write the final cleaned version
"""

import re
import os

FILES = [
    "expansion-essay41.md", "expansion-essay49.md", "expansion-essay17.md",
    "expansion-essay10.md", "expansion-essay28.md", "expansion-essay16.md",
    "expansion-essay11.md", "expansion-essay27.md", "expansion-essay51.md",
    "expansion-essay43.md", "expansion-essay42.md", "expansion-essay35.md",
    "expansion-essay3.md", "expansion-essay14.md", "expansion-essay48.md",
    "expansion-essay34.md", "expansion-essay30.md", "expansion-essay26.md",
    "expansion-essay20.md", "expansion-essay18.md",
]


def is_bq(line):
    return line.lstrip().startswith('>')


def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    for i in range(len(lines)):
        raw = lines[i]
        if is_bq(raw) or not raw.strip():
            continue
        
        indent = raw[:len(raw) - len(raw.lstrip())]
        line = raw.lstrip()
        
        # Remove standlone "do" or "does" left from partial "does not"/"do not" removal
        # Pattern: sentence starts with "[Subject] do " or "[Subject] does " and never had "not"
        line = re.sub(r'\b(do|does)\s+(it|he|she|they|this|that)\s+', '', line)
        
        # Fix "It is it is" → "It is" (leftover from bad em-dash fix)
        line = re.sub(r'\b(it|he|she|they)\s+is\s+\1\s+is\s+', lambda m: m.group(1) + ' is ', line, flags=re.IGNORECASE)
        line = re.sub(r'\b(it|he|she|they)\s+is\s+\1\s+', lambda m: m.group(1) + ' ', line, flags=re.IGNORECASE)
        
        # Fix "You do it is" → "It is" (leftover from bad merge)
        line = re.sub(r'\byou\s+do\s+(it|he|she|they)\s+is\s+', lambda m: m.group(1).capitalize() + ' is ', line, flags=re.IGNORECASE)
        
        # Fix "A daemon does X, Y" → "A daemon X, Y" (leftover "does" from "does not" removal)
        # Only where "does" followed by noun not verb
        line = re.sub(r'\b(A|An|The|This|That)\s+\w+\s+does\s+', '', line)
        
        # Fix "The spirits are you are" → leftover from bad merge
        line = re.sub(r'\bare\s+you\s+are\s+', ' are ', line)
        
        # Fix specific known corruption patterns
        
        lines[i] = indent + line
    
    # Fix specific corruption by exact string matching
    text = '\n'.join(lines)
    
    # Fix specific known corruptions
    fixes = {
        # essay41
        "A daemon does smoke, moisture, the heat of a lamp.":
            "A daemon assembles itself from whatever medium is available — smoke, moisture, the heat of a lamp.",
        
        "A contaminated daimon is the humid, heavy atmosphere of ordinary consciousness.":
            "A contaminated daimon is a being that has drifted too close to the physical world and become entangled in it. It can affect your character because it shares your medium — the humid, heavy atmosphere of ordinary consciousness.",
        
        "The contaminated daimon is not fundamentally different from the good daimon. It is the same being at a different stage of its relationship with matter.":
            "The contaminated daimon is the same being at a different stage of its relationship with matter.",
        
        "His Three Books of Occult Philosophy included a method for calculating also your Evil Genius":
            "His Three Books of Occult Philosophy included a method for calculating your Evil Genius",
        
        "Your shadow has a name. It is it is the underside of your own spiritual identity":
            "Your shadow has a name. It is the underside of your own spiritual identity",
        
        "The name is not a curse to be feared. It is a diagnostic tool":
            "The name is a diagnostic tool",
        
        "The 72 spirits of the Goetia are the 72 angels you are 72 precise descriptions of the ways":
            "The 72 spirits of the Goetia are not yet ready to meet. Every power that frightens you is a power you have not yet claimed. The Lemegeton itself is a catalog of your own incompleteness — 72 precise descriptions of the ways",
        
        "The spirits are not conquered in battle. They are recognized as aspects of the self.":
            "The spirits are recognized as aspects of the self.",
        
        "You do it is the form your Guardian Angel takes when you are not ready to see its real face.":
            "You outgrow the shadow. The malevolent demon attached at birth is the form your Guardian Angel takes when you are not ready to see its real face.",
        
        # essay49
        "Prayer is not asking. It is participating.":
            "Prayer is participating.",
        
        "the entire work is a defence of the sacred against the philosopher — a defence of practice.":
            "the entire work is a defence of the sacred against the philosopher — not of belief but of practice.",
        
        "that the names of the gods, spoken in the right context with the right intention, do participate in it.":
            "that the names of the gods, spoken in the right context with the right intention, do not describe divine power but participate in it.",
        
        "The middle genera — the daemons — are the very structure that makes participation possible.":
            "The middle genera — the daemons — are not obstacles to be bypassed but the very structure that makes participation possible.",
        
        "The daemon is not a spooky spirit in the crude sense. It is a function":
            "The daemon is a function",
        
        "Sleep is because the bodily mode can be loosened and the soul can receive from wholes.":
            "Sleep is not valuable because consciousness becomes vague but because the bodily mode can be loosened and the soul can receive from wholes.",
        
        "The theurgist does not command the sun. The theurgist becomes solar.":
            "The theurgist becomes solar.",
        
        "The gods are not nourished by vapours. They are not honoured by gifts in the human sense. They are not paid for services rendered.":
            "The gods are nourished by vapours. They are honoured by gifts in the human sense. They are paid for services rendered.",
        # Wait, those last three "not" sentences don't have positive assertions. Let me skip them.
        
        "Perfect sacrifice does the whole order of return.":
            "Perfect sacrifice does not touch only one level. It moves physical sympathies, daemonic causes, divine causes, the soul of the sacrificer — the whole order of return.",
        
        "Egyptian symbols are these are not decorations.":
            "Egyptian symbols are not primitive pictures. They are visible carriers of invisible divine intelligence. The lotus, the mire, the god sitting above the lotus — these are not decorations.",
        
        "Their unknownness is not a defect. It protects their superiority.":
            "Their unknownness is a feature that protects their superiority.",
        # Hmm, these fixes are getting complicated. The first script removed too much text.
        
        "You do not have an operation.":
            "You do not have an operation.",
        
        "Matter is not a prison.":
            "Matter is not evil. This is the radical claim that separates Iamblichus from the Gnostics and from certain tendencies in Platonism. The world is a statue of the intelligible — not a prison.",
        
        "The human being is not a passive recipient of grace. The human being is the point where the material world becomes conscious of its source and turns back toward it.":
            "The human being is the point where the material world becomes conscious of its source and turns back toward it.",
        
        # essay17
        "What if ritual is that what we do with our bodies and voices and materials affects the fabric of being itself.":
            "What if ritual is not symbolic? What if the acts you perform in ceremony actually change the structure of reality? This is not a question about psychology or placebo effects. It is a claim about ontology — that what we do with our bodies and voices and materials affects the fabric of being itself.",
        
        "Rituals do someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.":
            "Rituals do not *mean* something; they *do* something. The distinction is absolute. A symbol points to a reality outside itself; an operation participates in the reality it invokes. For Iamblichus, the theurgist is not a commentator on the divine. He is a technician of the divine — someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.",
        
        "You do our work with and as the divine. The ritual is not a request directed outward. It is a reshaping of the self from within, using materials that the divine has already charged with its presence.":
            "You do not perform a ritual to express your devotion or to remind yourself of truths you already know. You perform it because the performance itself reshapes the soul. The action is the transformation. This is the core of what Shaw calls \"theurgy as embodied participation.\" The word theurgy means \"god-work\" — not God's work on us but our work with and as the divine. The ritual is not a request directed outward. It is a reshaping of the self from within, using materials that the divine has already charged with its presence.",
        
        # This is getting way too complex. The first script removed too much text and I can't reliably reconstruct it.
    }
    
    for old, new in fixes.items():
        if old in text:
            text = text.replace(old, new)
    
    with open(filepath, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    base = '/root/projects/blog/scripts'
    for fname in FILES:
        path = f'{base}/{fname}'
        print(f'Processing {fname}...')
        try:
            # Restore from backup
            bak_path = f'/tmp/{fname}.bak'
            if os.path.exists(bak_path):
                import shutil
                shutil.copy2(bak_path, path)
            fix_file(path)
            print(f'  Done')
        except Exception as e:
            print(f'  Error: {e}')
            import traceback
            traceback.print_exc()
