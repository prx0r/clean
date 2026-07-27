import os, sys

# Read the first pack as reference template parts
ref = open("/root/projects/tantraloka/goldrender/spacious_present_platinum.py").read()

# Extract the helper functions/imports section (everything before "# Continuity object:")
lines = ref.split('\n')
helper_end = 0
for i, l in enumerate(lines):
    if l.strip().startswith('# Continuity object:') or l.strip().startswith('# =') and i > 100:
        # find the section boundary
        pass

# Actually, let me just generate each remaining pack individually
# by writing the content carefully

# Let me write each remaining pack file by constructing it in python
# without using triple quotes in the content

# The approach: write content using single-quoted strings and escape what needs escaping

print("WRITING PACKS...")

# I'll write each pack to the file system
packs_to_write = [
    ("morphospace_navigation", "morphospace_navigation_platinum.py"),
    # add the rest
]

for slug, fname in packs_to_write:
    fpath = f"/root/projects/tantraloka/goldrender/{fname}"
    print(f"Would write {fpath}")

print("Done")
