#!/usr/bin/env python3
"""
Rewrite badly corrupted files with correct NEG-removed content.
For each file, provides specific fixes to restore from corruption.
"""
import os, shutil

BASE = '/root/projects/blog/scripts'
BKP = '/tmp'

# For each file that's still corrupted, restore from backup and apply specific fixes
# The fixes restore original text AND apply NEG removal in one step

fixes = {
# === essay16 - badly corrupted ===
'expansion-essay16.md': [
    # Restore L7 corruption: "the guru does imparts transformation" → "does not give information but imparts transformation"
    ('The guru-disciple relationship is the initiatic model: the guru does imparts transformation.',
     'The guru-disciple relationship is the initiatic model: the guru does not give information but imparts transformation.'),
    # But this should NEG to: "the guru imparts transformation"
    # So two-step: fix corruption first, then NEG remove
    
    # Actually let me just restore from backup and apply fixes in the right order
],

# === essay49 - minor corruption ===
'expansion-essay49.md': [
    # Line 41: "Sleep is because" → "Sleep is not valuable because consciousness becomes vague but because"
    # After NEG removal: "Sleep is because the bodily mode can be loosened"
    # This one doesn't cleanly follow the pattern - "not valuable because X but because Y" → "because Y"
    # So: "Sleep is because the bodily mode can be loosened"
    ('Sleep is because the bodily mode can be loosened and the soul can receive from wholes.',
     'Sleep is because the bodily mode can be loosened and the soul can receive from wholes.'),
    # Actually this is already correct! The original "Sleep is not valuable because consciousness becomes vague but because" was corrupted to "Sleep is because" which is what we want after NEG removal.
    
    # Line 51: "The theurgist becomes solar." ✓ already NEG removed
    
    # Line 67: "Perfect sacrifice does not touch only one level." - this still has "does not"
    # But there's no positive assertion that follows cleanly. "It moves physical sympathies..." is the assertion.
    # Actually: "Perfect sacrifice does not touch only one level. It moves physical sympathies..." → "Perfect sacrifice moves physical sympathies..."
    # But wait, the "does not" negates "touch only one level", so "It moves..." IS the positive assertion.
    
    # Line 97: "Iamblichus did not believe that the gods were diminished by needing us. He believed that needing was the structure of love."
    # → "Iamblichus believed that needing was the structure of love."
    ('Iamblichus did not believe that the gods were diminished by needing us. He believed that needing was the structure of love.',
     'Iamblichus believed that needing was the structure of love.'),
],

# === essay17 - badly corrupted ===
'expansion-essay17.md': [
    # Fix line 25 corruption: "The formless is by using form" → fix to "The formless is not accessed by abandoning form but by using form"
    # After NEG removal: "The formless is accessed by using form so precisely that it becomes transparent to the formless."
    ('The formless is by using form so precisely that it becomes transparent to the formless.',
     'The formless is accessed by using form so precisely that it becomes transparent to the formless.'),
    
    # Fix line 35: "material gestures produce spiritual effects, through ontological resonance" 
    # This is corrupted from "not through symbolism but through ontological resonance"
    ('material gestures produce spiritual effects, through ontological resonance.',
     'material gestures produce spiritual effects through ontological resonance.'),
    
    # Fix line 49: "The goal of theurgy is the god's body." 
    # Original: "The goal of theurgy is not to see the gods or to speak with them. The goal is to become the shape through which a god can act in the world. The priest does not represent the god; he is the god's body."
    # After NEG removal: "The goal of theurgy is to become the shape through which a god can act in the world. The priest is the god's body."
    ('The goal of theurgy is the god\'s body.',
     'The goal of theurgy is to become the shape through which a god can act in the world. The priest is the god\'s body.'),
    
    # Fix line 51 corruption: "This is refined to the point where it can resonate with a divine note without distortion."
    # Original: "This is not possession in the crude sense of the word — the displacement of one personality by another. It is more like tuning an instrument to a specific frequency. The theurgist's own soul is not erased; it is refined to the point where it can resonate with a divine note without distortion."
    # After NEG removal: 
    # "This is not possession" → keep? "This is not possession" has no positive assertion follow-up with "It is more like tuning" as the follow-up.
    # Actually: "This is not possession in the crude sense of the word — the displacement of one personality by another. It is more like tuning an instrument to a specific frequency."
    # The em-dash pattern: "not X — Y" → "Y" doesn't quite work here because Y is "the displacement" which is a noun phrase, not a full clause.
    # Let me just restore the original text.
    ('This is refined to the point where it can resonate with a divine note without distortion.',
     'This is not possession in the crude sense of the word — the displacement of one personality by another. It is more like tuning an instrument to a specific frequency. The theurgist\'s own soul is not erased; it is refined to the point where it can resonate with a divine note without distortion.'),
    # Then NEG remove: "The theurgist's own soul is not erased; it is refined" → "The theurgist's own soul is refined"
    # This is in the same line. Let me handle it.
    
    # Fix line 59: "His reward is the experience of being used as an instrument of the divine."
    # Original: "His reward is not recognition but the experience of being used as an instrument of the divine."
    # After NEG removal: "His reward is the experience of being used as an instrument of the divine." ✓ already correct!
    
    # Fix line 43: "becomes a living bridge between the material and the spiritual worlds — in fact."
    # Original: "becomes a living bridge between the material and the spiritual worlds — not in theory but in fact."
    # After NEG removal: "becomes a living bridge between the material and the spiritual worlds — in fact." ✓ already correct!
],

# === essay18 - badly corrupted ===
'expansion-essay18.md': [
    # Fix L9: "These channels are it is the fire of pure awareness that burns away all duality."
    # Original: "These channels are not metaphorical. They are as real as arteries, but they carry force, not blood. The left channel (iḍā) is lunar, cool, associated with the parasympathetic nervous system. The right channel (piṅgalā) is solar, hot, sympathetic. The central channel (suṣumṇā) is neither — it is the fire of pure awareness that burns away all duality."
    # After NEG removal: "These channels are as real as arteries, but they carry force, not blood. The left channel (iḍā) is lunar, cool, associated with the parasympathetic nervous system. The right channel (piṅgalā) is solar, hot, sympathetic. The central channel (suṣumṇā) is neither — it is the fire of pure awareness that burns away all duality."
    ('These channels are it is the fire of pure awareness that burns away all duality.',
     'These channels are as real as arteries, but they carry force, not blood. The left channel (iḍā) is lunar, cool, associated with the parasympathetic nervous system. The right channel (piṅgalā) is solar, hot, sympathetic. The central channel (suṣumṇā) is neither — it is the fire of pure awareness that burns away all duality.'),
    
    # Fix L15: "These seven centers are from the density of survival at the base to the density of transcendent awareness at the crown."
    # Original: "These seven centers are not locations in the physical body. They are thresholds in the subtle body where consciousness condenses into different densities — from the density of survival at the base to the density of transcendent awareness at the crown."
    # After NEG removal: "These seven centers are thresholds in the subtle body where consciousness condenses into different densities — from the density of survival at the base to the density of transcendent awareness at the crown."
    ('These seven centers are from the density of survival at the base to the density of transcendent awareness at the crown.',
     'These seven centers are thresholds in the subtle body where consciousness condenses into different densities — from the density of survival at the base to the density of transcendent awareness at the crown.'),
    
    # Fix L21: "The subtle body is like a radio that manifests the signal it receives."
    # Original: "The subtle body is not a metaphor for the nervous system. It is a parallel infrastructure, as real as the nerves but operating at a different frequency. The nerves are the physical extension of this deeper, non-material system — like a radio that manifests the signal it receives."
    # After NEG removal: "The subtle body is a parallel infrastructure, as real as the nerves but operating at a different frequency. The nerves are the physical extension of this deeper, non-material system — like a radio that manifests the signal it receives."
    ('The subtle body is like a radio that manifests the signal it receives.',
     'The subtle body is a parallel infrastructure, as real as the nerves but operating at a different frequency. The nerves are the physical extension of this deeper, non-material system — like a radio that manifests the signal it receives.'),
    
    # Fix L25: "Kuṇḍalinī is a gross transformation contradictory to Kuṇḍalinī's real nature."
    # Original: "Kuṇḍalinī is not chemical energy, because chemical energy is derived from food and tissue — a gross transformation contradictory to Kuṇḍalinī's real nature."
    # After NEG removal: this doesn't follow the pattern cleanly.
    ('Kuṇḍalinī is a gross transformation contradictory to Kuṇḍalinī\'s real nature.',
     'Kuṇḍalinī is not chemical energy, because chemical energy is derived from food and tissue — a gross transformation contradictory to Kuṇḍalinī\'s real nature.'),
    
    # Fix L39: "The energy that moves through your body and mind is the stillness that makes motion possible."
    # Original: "The energy that moves through your body and mind is not the whole story. There is a static pole to existence — the stillness that makes motion possible."
    # After NEG removal: can't cleanly merge - "the energy... is not the whole story" doesn't have a positive re-assertion with the same subject.
    ('The energy that moves through your body and mind is the stillness that makes motion possible.',
     'The energy that moves through your body and mind is not the whole story. There is a static pole to existence — the stillness that makes motion possible.'),
    
    # Fix L45: "The awakening is but it returns transformed"
    # Original: "The awakening is not a permanent ascent. The power rises, illuminates, and then returns — but it returns transformed"
    # After NEG removal: "The power rises, illuminates, and then returns — but it returns transformed, and it transforms..."
    ('The awakening is but it returns transformed, and it transforms the ordinary consciousness it descends into.',
     'The power rises, illuminates, and then returns — but it returns transformed, and it transforms the ordinary consciousness it descends into.'),
    
    # Fix L51: "when the bell fades into silence, the yogin does he becomes it."
    # Original: "These sounds are not imagined. They are the actual auditory correlates of the prāṇic flow in each channel, audible to the yogin whose concentration has been refined through practice."
    # Wait that's different. Let me re-read line 51.
    # Line 51 original: "These sounds are not imagined. They are the actual auditory correlates of the prāṇic flow in each channel, audible to the yogin whose concentration has been refined through practice. The Tantrāloka describes them as precise indicators of the state of the channels — diagnostic signs on the inner anatomy."
    # After NEG removal: "These sounds are the actual auditory correlates of the prāṇic flow in each channel, audible to the yogin whose concentration has been refined through practice. The Tantrāloka describes them as precise indicators of the state of the channels — diagnostic signs on the inner anatomy."
    ('when the bell fades into silence, the yogin does he becomes it. These sounds are diagnostic signs on the inner anatomy.',
     'when the bell fades into silence, the yogin does not hear silence — he becomes it. These sounds are not imagined. They are the actual auditory correlates of the prāṇic flow in each channel, audible to the yogin whose concentration has been refined through practice. The Tantrāloka describes them as precise indicators of the state of the channels — diagnostic signs on the inner anatomy.'),
    
    # Fix L55: "The body you cannot see is like ice floating on water"
    # Original: "The body you cannot see is not a phantom or a fantasy. It is a more fundamental version of the body you know. The physical body is its outer expression, its densest form — like ice floating on water"
    # After NEG removal: "The body you cannot see is a more fundamental version of the body you know. The physical body is its outer expression, its densest form — like ice floating on water"
    ('The body you cannot see is like ice floating on water, visible but dependent on the invisible medium beneath.',
     'The body you cannot see is not a phantom or a fantasy. It is a more fundamental version of the body you know. The physical body is its outer expression, its densest form — like ice floating on water, visible but dependent on the invisible medium beneath.'),
],
}

def apply():
    for fname, file_fixes in fixes.items():
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            print(f'{fname}: not found')
            continue
        
        with open(path, 'r') as f:
            content = f.read()
        
        for old, new in file_fixes:
            if old in content:
                content = content.replace(old, new)
                print(f'{fname}: Fixed: {old[:50]}...')
            else:
                print(f'{fname}: NOT FOUND: {old[:50]}...')
        
        with open(path, 'w') as f:
            f.write(content)
        print(f'{fname}: Done')

if __name__ == '__main__':
    apply()
