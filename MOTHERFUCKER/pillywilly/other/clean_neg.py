#!/usr/bin/env python3
"""
Clean NEG patterns from essay files.
- Restores from backup (corrupted by previous attempt)
- Applies correct NEG removal using specific text replacements
- Never modifies blockquotes (>)
"""

import re, os, shutil

BASE = '/root/projects/blog/scripts'
BKP  = '/tmp'

FILES = [
    "expansion-essay41.md", "expansion-essay49.md", "expansion-essay17.md",
    "expansion-essay10.md", "expansion-essay28.md", "expansion-essay16.md",
    "expansion-essay11.md", "expansion-essay27.md", "expansion-essay51.md",
    "expansion-essay43.md", "expansion-essay42.md", "expansion-essay35.md",
    "expansion-essay3.md", "expansion-essay14.md", "expansion-essay48.md",
    "expansion-essay34.md", "expansion-essay30.md", "expansion-essay26.md",
    "expansion-essay20.md", "expansion-essay18.md",
]

def is_bq_line(line):
    return line.lstrip().startswith('>')

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Pass 1: Fix intra-line corruption and apply NEG removal
    for i in range(len(lines)):
        raw = lines[i]
        if is_bq_line(raw) or not raw.strip():
            continue
        
        line = raw.rstrip('\n')
        
        # Repair em-dash remnants: "It is it is" → "It is"
        line = re.sub(r'\b(it|he|she|they)\s+is\s+\1\s+is(?=\s)', 
                      lambda m: m.group(1).capitalize() + ' is ', line, flags=re.IGNORECASE)
        line = re.sub(r'\b(it|he|she|they)\s+is\s+\1\s+', 
                      lambda m: m.group(1).capitalize() + ' ', line, flags=re.IGNORECASE)
        
        # Repair "You do it is" → "It is"
        line = re.sub(r'\bYou\s+do\s+(it|he|she|they)\s+is\s+', 
                      lambda m: m.group(1).capitalize() + ' is ', line)
        
        # Repair "A daemon does smoke" → need to restore the line below
        # This is too specific for regex, handle in pass 2
        
        # REGULAR NEG REMOVAL:
        # Pattern: semicolon "not X; Y" → "Y" 
        # e.g., "The body is not the obstacle to union with the divine; it is the vehicle."
        # → "The body is the vehicle."
        # But careful: only when the pattern follows the "not X but Y" structure
        # Actually "not X; Y" where Y restates positively
        
        # Pattern: em-dash "[verb] not [X] — [pronoun] [verb] [Y]" → "[verb] [Y]"
        # But only on non-corrupted text (where the em-dash is still present)
        m = re.search(r'\b(is|are|was|were|does|do)\s+not\s+(.+?)\s*—\s+(?:it|he|she|they)\s+\1\s+', line, re.IGNORECASE)
        if m:
            verb = m.group(1)
            prefix_end = m.start()
            rest = line[m.end():]
            line = line[:prefix_end] + verb + ' ' + rest
        
        # Pattern: "not X but Y" → "Y" (intra-sentence)
        # Skip "not only X but also Y"
        m = re.search(r'\bnot\s+((?!only)\w+(?:\s+\w+){0,5}?)\s+but\s+', line, re.IGNORECASE)
        if m:
            x_part = m.group(1)
            # Check if this looks like a valid X in "not X but Y"
            after_but = line[m.end():]
            # Only remove if what follows "but" makes sense as the assertion
            line = line[:m.start()] + after_but
        
        # Pattern: "cannot" followed by positive assertion in same clause
        # This is too varied for regex, handle in pass 2
        
        lines[i] = line + '\n' if not line.endswith('\n') else line
    
    # Pass 2: Handle cross-sentence patterns
    # "[Subject] [negation] [X]. [It/They] [positive]" → "[Subject] [positive]"
    result = []
    skip_next = False
    
    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue
        
        raw = lines[i]
        if is_bq_line(raw) or not raw.strip():
            result.append(raw)
            continue
        
        if i + 1 >= len(lines):
            result.append(raw)
            continue
        
        next_raw = lines[i + 1]
        if is_bq_line(next_raw) or not next_raw.strip():
            result.append(raw)
            continue
        
        s1 = raw.rstrip('\n')
        s2 = next_raw.rstrip('\n')
        
        # Try: "[Subject] {is|are|was|were|does|do} not [X]. {It|They} [positive]"
        m1 = re.search(r'\b(is|are|was|were|does|do)\s+not\s+(.+?)\.\s*$', s1, re.IGNORECASE)
        if m1:
            verb = m1.group(1)
            negated = m1.group(2)
            # Get subject
            verb_idx = m1.start(1)
            subject = s1[:verb_idx].strip()
            
            # Check if s2 starts with pronoun
            m2 = re.match(r'(It|They|He|She|You)\s+(.+)', s2.strip(), re.IGNORECASE)
            if m2:
                pronoun = m2.group(1)
                rest = m2.group(2)
                
                if pronoun.lower() in ('it', 'he', 'she', 'they'):
                    merged = subject + ' ' + rest
                else:
                    merged = 'You ' + rest
                
                # Capitalize
                if s1[0].isupper():
                    merged = merged[0].upper() + merged[1:]
                
                result.append(raw[:len(raw)-len(s1)] + merged + '\n')
                skip_next = True
                continue
        
        result.append(raw)
    
    out = ''.join(result)
    with open(filepath, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    for fname in FILES:
        src = os.path.join(BKP, fname + '.bak')
        dst = os.path.join(BASE, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        print(f'Processing {fname}...')
        fix_file(dst)
        print(f'  Done')
