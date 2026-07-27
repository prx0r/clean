#!/usr/bin/env python3
"""
Final polish: handle mid-line NEG patterns that earlier passes missed.
Looks for "[not X]. [Pronoun Y]" or "[not X]; [Pronoun Y]" within commentary text.
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
    "expansion-essay20.md", "expansion-essay18.md"
]

def fix_file(path):
    with open(path, 'r') as f:
        text = f.read()
    
    # Split into paragraphs (by double newlines or blockquote boundaries)
    # Process each paragraph as a unit
    paragraphs = text.split('\n\n')
    result = []
    
    for para in paragraphs:
        lines = para.split('\n')
        
        # Skip if any line is a blockquote
        if any(l.lstrip().startswith('>') for l in lines if l.strip()):
            result.append(para)
            continue
        
        # Join lines into a single block of commentary
        block = ' '.join(l.strip() for l in lines if l.strip())
        if not block:
            result.append(para)
            continue
        
        # Pattern: ". [Subject] [is|are|was|were|does|do] not [X]. {It|They|He|She} [Y]"
        # → ". [Subject] [Y]"
        # This needs to handle the pattern anywhere in the block
        
        # First, handle ". not X. It Y." patterns
        # This is chained replacements from end to beginning to avoid match shifting
        changed = True
        while changed:
            changed = False
            m = re.search(
                r'(\b(is|are|was|were|does|do)\s+not\s+[^.!?]+[.!?])\s+(It|They|He|She)\s+',
                block
            )
            if m:
                # Find the subject before "is/are/was/were/does/do not"
                prefix = block[:m.start()]
                # Extract the last noun phrase before the NEG verb
                neg_verb = m.group(2)
                subj_match = re.search(r'(\S[\s\S]*?)\s+' + re.escape(neg_verb) + r'\s+not\b', block[:m.end()])
                if subj_match:
                    subject = subj_match.group(1).strip()
                    # Get the positive assertion after "It/They/He/She"
                    after_pronoun = block[m.end():]
                    # Find where this assertion ends (period, exclamation, question, or end of block)
                    end_match = re.search(r'[.!?]', after_pronoun)
                    if end_match:
                        assertion = after_pronoun[:end_match.end()]
                    else:
                        assertion = after_pronoun
                    
                    # Build replacement: keep everything before the match, add subject + assertion
                    before = block[:m.start()]
                    # Find the start of the negated sentence
                    neg_start = subj_match.start()
                    replacement = block[:neg_start] + subject + ' ' + assertion
                    block = replacement + block[m.end() + len(assertion):]
                    changed = True
        
        # Handle "not X; It Y" patterns (semicolon)
        block = re.sub(
            r'\b(is|are|was|were|does|do)\s+not\s+([^;]+?);\s+(?:it|they|he|she)\s+\1\s+',
            r'\1 ', block, flags=re.IGNORECASE
        )
        
        # Handle "not X — It Y" patterns (em-dash)
        block = re.sub(
            r'\b(is|are|was|were|does|do)\s+not\s+([^—]+?)—\s*(?:it|they|he|she)\s+\1\s+',
            r'\1 ', block, flags=re.IGNORECASE
        )
        
        # Handle "not because X but because Y" → "because Y"
        block = re.sub(
            r'not because\s+[^,]+?,\s*but because\s+',
            'because ', block, flags=re.IGNORECASE
        )
        
        # Rebuild paragraph with original line structure (approximate)
        if len(lines) == 1:
            result.append(block)
        else:
            # Simple approach: put the whole block back
            result.append(block)
    
    with open(path, 'w') as f:
        f.write('\n\n'.join(result))

for fname in FILES:
    path = os.path.join(BASE, fname)
    print(f'Polishing {fname}...')
    fix_file(path)
print('Done')
