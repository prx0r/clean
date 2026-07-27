#!/usr/bin/env python3
"""
Final NEG removal pass for all 20 essay files.
Only removes NEGs that follow the pattern:
1. "[negation sentence]. [positive assertion sentence]" (cross-sentence)
2. "not X but Y" (intra-sentence)
3. "[verb] not X; [pronoun verb] Y" (semicolon pivot)
4. "[verb] not X — [pronoun verb] Y" (em-dash pivot)

Does NOT modify blockquotes.
"""

import re, os

BASE = '/root/projects/blog/scripts'
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

def fix_cross_sentence(lines):
    """Handle cross-sentence NEG patterns."""
    result = []
    skip_next = False
    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue
        
        raw = lines[i]
        s = raw.rstrip('\n')
        if is_bq(raw) or not s:
            result.append(raw)
            continue
        
        if i + 1 >= len(lines):
            result.append(raw)
            continue
        
        next_raw = lines[i + 1]
        if is_bq(next_raw) or not next_raw.strip():
            result.append(raw)
            continue
        
        s2 = next_raw.strip()
        
        # Pattern: "[Subject] (is|are|was|were|does|do) not [X]. {It|They|He|She|You} [positive]"
        m = re.search(
            r'\b(is|are|was|were|does|do)\s+not\s+(.+?)\.\s*$',
            s, re.IGNORECASE
        )
        if not m:
            result.append(raw)
            continue
        
        verb = m.group(1)
        # Get subject
        idx = s.lower().index(verb + ' not')
        subject = s[:idx].strip()
        
        # Check second sentence
        m2 = re.match(r'(It|They|He|She|You)\s+(.+)', s2, re.IGNORECASE)
        if not m2:
            result.append(raw)
            continue
        
        pronoun = m2.group(1)
        rest = m2.group(2)
        
        # Build merged sentence
        if pronoun.lower() in ('it', 'he', 'she', 'they'):
            merged = subject + ' ' + rest
        else:
            merged = 'You ' + rest
        
        # Capitalize
        if s[0].isupper():
            merged = merged[0].upper() + merged[1:]
        
        indent = raw[:len(raw) - len(s)]
        result.append(indent + merged + '\n')
        skip_next = True
    
    return result


def fix_intra_line(text):
    """Handle intra-line NEG patterns (not X but Y, semicolon/em-dash pivots)."""
    
    # "not X but Y" → "Y" (be careful with "not only... but also")
    text = re.sub(
        r'\bnot\s+((?!only)\w+(?:\s+\w+){0,5}?)\s+but\s+',
        '', text
    )
    
    # Semicolon pivot: "[verb] not [X]; [pronoun] [verb] [Y]" → "[verb] [Y]"
    # Already handled by cross-sentence for separate sentences.
    # For same-line semicolon: "The incense is not a symbol of divinity; it is divinity in the form of smoke."
    text = re.sub(
        r'\b(is|are|was|were|does|do)\s+not\s+([^;]+?);\s+(?:it|he|she|they)\s+\1\s+',
        r'\1 ',
        text, flags=re.IGNORECASE
    )
    
    # Em-dash pivot: same pattern with em-dash
    text = re.sub(
        r'\b(is|are|was|were|does|do)\s+not\s+([^—]+?)—\s*(?:it|he|she|they)\s+\1\s+',
        r'\1 ',
        text, flags=re.IGNORECASE
    )
    
    # "not because X, but because Y" → "because Y"
    text = re.sub(
        r'not because\s+(.+?),\s*but because\s+',
        'because ', text, flags=re.IGNORECASE
    )
    
    return text


def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Pass 1: Fix intra-line patterns (non-blockquote lines)
    for i in range(len(lines)):
        raw = lines[i]
        if is_bq(raw) or not raw.strip():
            continue
        lines[i] = fix_intra_line(raw)
    
    # Pass 2: Fix cross-sentence patterns
    lines = fix_cross_sentence(lines)
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    for fname in FILES:
        path = os.path.join(BASE, fname)
        print(f'Processing {fname}...')
        fix_file(path)
        print(f'  Done')
