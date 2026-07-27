#!/usr/bin/env python3
"""
Fix all 20 essay files. Reads the corrupted versions (from backup), applies
specific text replacements to fix corruption AND apply NEG removal.

Each file has a list of (old_text, new_text) where old_text is the exact
text in the corrupted file and new_text is the final desired text.
"""

import os, shutil

BASE = '/root/projects/blog/scripts'
BKP  = '/tmp'

# (filename, [(old, new), ...])
FIXES = [
('expansion-essay41.md', [
    # Fix corruption: line 9 "A daemon does smoke" → restored + NEG removed
    ('A daemon does smoke, moisture, the heat of a lamp.',
     'A daemon assembles itself from whatever medium is available — smoke, moisture, the heat of a lamp.'),
    # NEG remove: line 15
    ('The punishing daemon does not hate you. It is the part of the cosmic order that reflects your own actions back at you.',
     'The punishing daemon is the part of the cosmic order that reflects your own actions back at you.'),
    # Fix corruption: line 21 "A contaminated daimon is the humid" → restored + NEG
    ('A contaminated daimon is the humid, heavy atmosphere of ordinary consciousness.',
     'A contaminated daimon is a being that has drifted too close to the physical world and become entangled in it. It can affect your character because it shares your medium — the humid, heavy atmosphere of ordinary consciousness.'),
    # NEG remove: line 21 "is not fundamentally different" → "is"
    ('The contaminated daimon is not fundamentally different from the good daimon. It is the same being at a different stage of its relationship with matter.',
     'The contaminated daimon is the same being at a different stage of its relationship with matter.'),
    # Fix corruption: line 23 "also your Evil Genius" → restored + NEG removed
    ('His Three Books of Occult Philosophy included a method for calculating also your Evil Genius',
     'His Three Books of Occult Philosophy included a method for calculating your Evil Genius'),
    # Fix em-dash remnant: line 27 "It is  the underside" (double space)
    ('It is  the underside', 'It is the underside'),
    # NEG remove: line 27 "The name is not a curse"
    ('The name is not a curse to be feared. It is a diagnostic tool',
     'The name is a diagnostic tool'),
    # Fix corruption: line 33 "you are 72 precise descriptions" → restored
    ('The 72 spirits of the Goetia are the 72 angels you are 72 precise descriptions of the ways a divine force can appear when it is blocked by a human limitation.',
     'The 72 spirits of the Goetia are the 72 angels you are not yet ready to meet. Every power that frightens you is a power you have not yet claimed. The Lemegeton itself is a catalog of your own incompleteness — 72 precise descriptions of the ways a divine force can appear when it is blocked by a human limitation.'),
    # NEG remove: "are not conquered in battle. They are"
    ('The spirits are not conquered in battle. They are recognized as aspects of the self.',
     'The spirits are recognized as aspects of the self.'),
    # Fix corruption + NEG remove: line 45 "It is the form" → restored
    ('It is the form your Guardian Angel takes when you are not ready to see its real face.',
     'You outgrow the shadow. The malevolent demon attached at birth is the form your Guardian Angel takes when you are not ready to see its real face.'),
    # NEG remove: "not because it is destroyed, but because"
    ('not because it is destroyed, but because you have absorbed it',
     'because you have absorbed it'),
]),
('expansion-essay49.md', [
    # NEG remove
    ('Prayer is not asking. It is participating.',
     'Prayer is participating.'),
    # NEG remove: cross-sentence
    ('The gods are not a conclusion reached after thinking. They are a presence discovered when we stop thinking in the mode of detachment.',
     'The gods are a presence discovered when we stop thinking in the mode of detachment.'),
    # Fix corruption: "do not describe divine power but" → was corrupted to "do participate"
    ('that the names of the gods, spoken in the right context with the right intention, do participate in it.',
     'that the names of the gods, spoken in the right context with the right intention, do not describe divine power but participate in it.'),
    # Fix corruption: "obstacles to be bypassed but" → was removed
    ('The middle genera — the daemons — are the very structure that makes participation possible.',
     'The middle genera — the daemons — are not obstacles to be bypassed but the very structure that makes participation possible.'),
    # NEG remove: "is not a spooky spirit"
    ('The daemon is not a spooky spirit in the crude sense. It is a function:',
     'The daemon is a function:'),
    # Fix corruption: "Sleep is not valuable because" → became "Sleep is because"
    ('Sleep is because the bodily mode can be loosened and the soul can receive from wholes.',
     'Sleep is not valuable because consciousness becomes vague but because the bodily mode can be loosened and the soul can receive from wholes.'),
    # NEG remove: "the theurgist does not command the sun. The theurgist becomes solar."
    ('The theurgist does not command the sun. The theurgist becomes solar.',
     'The theurgist becomes solar.'),
    # Fix corruption: "does not touch only one level. It moves" → became "does the whole order"
    ('Perfect sacrifice does the whole order of return.',
     'Perfect sacrifice does not touch only one level. It moves physical sympathies, daemonic causes, divine causes, the soul of the sacrificer — the whole order of return.'),
    # Fix corruption: "Egyptian symbols are not primitive pictures" → became garbled
    ('Egyptian symbols are these are not decorations.',
     'Egyptian symbols are not primitive pictures. They are visible carriers of invisible divine intelligence. The lotus, the mire, the god sitting above the lotus — these are not decorations.'),
    # NEG remove: "Their unknownness is not a defect. It protects their superiority."
    ('Their unknownness is not a defect. It protects their superiority.',
     'Their unknownness protects their superiority.'),
    # Fix corruption + NEG: "Matter is not evil" → became "Matter is not a prison"
    ('Matter is not a prison. Matter can carry the divine because matter is already within the divine procession.',
     'Matter is not evil. This is the radical claim that separates Iamblichus from the Gnostics and from certain tendencies in Platonism. The world is a statue of the intelligible — not a prison. Matter can carry the divine because matter is already within the divine procession.'),
    # NEG remove: "is not a passive recipient"
    ('The human being is not a passive recipient of grace. The human being is the point where the material world becomes conscious of its source and turns back toward it.',
     'The human being is the point where the material world becomes conscious of its source and turns back toward it.'),
]),
('expansion-essay17.md', [
    # Fix corruption: line 3 "What if ritual is that" → restored
    ('What if ritual is that what we do with our bodies and voices and materials affects the fabric of being itself.',
     'What if ritual is not symbolic? What if the acts you perform in ceremony actually change the structure of reality? This is not a question about psychology or placebo effects. It is a claim about ontology — that what we do with our bodies and voices and materials affects the fabric of being itself.'),
    # Fix corruption: line 9 "Rituals do someone who knows"
    ('Rituals do someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.',
     'Rituals do not *mean* something; they *do* something. The distinction is absolute. A symbol points to a reality outside itself; an operation participates in the reality it invokes. For Iamblichus, the theurgist is not a commentator on the divine. He is a technician of the divine — someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.'),
    # Fix corruption: line 17 "You do our work"
    ('You do our work with and as the divine.',
     'You do not perform a ritual to express your devotion or to remind yourself of truths you already know. You perform it because the performance itself reshapes the soul. The action is the transformation. This is the core of what Shaw calls "theurgy as embodied participation." The word theurgy means "god-work" — not God\'s work on us but our work with and as the divine.'),
    # Fix corruption: line 25 "The formless is by using form"
    ('The formless is by using form so precisely that it becomes transparent to the formless.',
     'The formless is not accessed by abandoning form but by using form so precisely that it becomes transparent to the formless.'),
    # Fix corruption: line 33 "union with the divine does as natural"
    ('Iamblichus broke with the entire Platonic tradition when he insisted that union with the divine does as natural as fire burning when you strike flint.',
     'Iamblichus broke with the entire Platonic tradition when he insisted that union with the divine does not come through thought or contemplation alone. It comes through acts. The gods descend because they are invited by the correct sequence of gestures, sounds, and substances. The descent is not a reward for piety. It is a natural consequence of theurgy properly performed — as natural as fire burning when you strike flint.'),
    # NEG remove: "The theurgist does not beg. He does not hope. He performs."
    ('The theurgist does not beg. He does not hope. He performs.',
     'The theurgist performs.'),
    # Fix corruption: line 35 "not through symbolism but" → corrupted
    ('through ontological resonance',
     'not through symbolism but through ontological resonance'),
    # Fix corruption: line 41 "The soul does a body"
    ('The soul does a body of light that runs parallel to the physical body.',
     'The soul does not ascend to the gods. It already possesses, within its own structure, the capacity to be a vehicle for divine presence. Theurgy activates this capacity. The vehicle is not something you build; it is something you uncover. Shaw\'s work on the luminous body shows that the theurgic transformation is not the addition of something new to the soul but the restoration of something original. The soul descended from the divine into matter, and in that descent, it retained the trace of its origin — a body of light that runs parallel to the physical body.'),
    # Fix corruption: "not in theory but in fact" → "in fact"
    ('becomes a living bridge between the material and the spiritual worlds — in fact.',
     'becomes a living bridge between the material and the spiritual worlds — not in theory but in fact.'),
    # Fix corruption: line 49 "The goal of theurgy is a process"
    ('The goal of theurgy is a process of ritual assimilation in which the practitioner\'s own form becomes the form through which a divine power expresses itself.',
     'The goal of theurgy is not to see the gods or to speak with them. The goal is to become the shape through which a god can act in the world. The priest does not represent the god; he is the god\'s body. Shaw calls this "taking the shape of the gods" — a process of ritual assimilation in which the practitioner\'s own form becomes the form through which a divine power expresses itself.'),
    # Fix corruption: line 51 "This is the displacement"
    ('This is the displacement of one personality by another.',
     'This is not possession in the crude sense of the word — the displacement of one personality by another.'),
    # NEG remove: "the human is not diminished but fulfilled" → corrupted to "the human is fulfilled"
    ('the human is fulfilled.',
     'the human is not diminished but fulfilled.'),
    # Fix corruption: line 59 "not because the work is secret but because"
    ('The true theurgist works in silence, because the work is not about him.',
     'The true theurgist works in silence, not because the work is secret but because the work is not about him.'),
    # Fix corruption: "His reward is not recognition but the experience"
    ('His reward is the experience of being used as an instrument of the divine.',
     'His reward is not recognition but the experience of being used as an instrument of the divine.'),
    # Fix corruption: line 73 "Your external actions are made by hands"
    ('Your external actions are made by hands and voices and bodies moving through the ancient forms that the tradition has preserved for precisely this purpose.',
     'Your external actions are not expressions of your internal state; they are creators of it. You do not pray because you are devout; you become devout by praying. The god does not descend because you are worthy; you become worthy by performing the acts that invite the descent. Reality is not given; it is made — made by hands and voices and bodies moving through the ancient forms that the tradition has preserved for precisely this purpose.'),
]),
('expansion-essay10.md', [
    # Fix corruption: "If the soul does does" → restored
    ('If the soul does does the journey continues.',
     'If the soul does not recognize — does not awaken — the journey continues.'),
    # NEG remove: "This is not punishment. It is the natural movement"
    ('This is not punishment. It is the natural movement of consciousness seeking its own level.',
     'This is the natural movement of consciousness seeking its own level.'),
]),
('expansion-essay28.md', [
    # No corruption fix needed here - most NEGs are in blockquotes
    # The commentary has very few removable NEG patterns
    # NEG remove: "The self you cannot find is the one thing that cannot be lost."
    # This doesn't follow the pattern - "cannot" but no positive assertion
    # NEG remove: "not nothing" in "The teachers say: not nothing."
    # This doesn't follow the pattern.
]),
('expansion-essay16.md', [
    # NEG remove: "The world is not merely an illusion layered over a real substrate. There is no substrate."
    ('The world is not merely an illusion layered over a real substrate. There is no substrate.',
     'The world has no substrate.'),
]),
('expansion-essay11.md', [
    # Most NEGs are in blockquotes or don't follow the pattern
]),
('expansion-essay27.md', [
    # Most NEGs are in blockquotes
]),
('expansion-essay51.md', [
    # NEG remove
    ('Beauty is not a subjective judgment. It is the trace of the intelligible world in the sensible one',
     'Beauty is the trace of the intelligible world in the sensible one'),
    # NEG remove
    ('Beauty is not an argument. It is a recognition.',
     'Beauty is a recognition.'),
    # NEG remove
    ('This is not contempt for the world. It is the reorientation of desire toward its true object.',
     'This is the reorientation of desire toward its true object.'),
    # NEG remove: "The beauty that fades is not the true beauty but its image."
    ('The beauty that fades is not the true beauty but its image.',
     'The beauty that fades is its image.'),
    # NEG remove
    ('Plotinus does not ask you to reject the image. He asks you to use it as a ladder.',
     'Plotinus asks you to use it as a ladder.'),
]),
('expansion-essay43.md', [
    # NEG remove
    ('The daemon does not come when called. It comes when you have stopped pretending.',
     'The daemon comes when you have stopped pretending.'),
]),
('expansion-essay42.md', [
    # NEG remove
    ('The daimonion is not a voice in the ordinary sense. It is a discriminative faculty',
     'The daimonion is a discriminative faculty'),
    # NEG remove
    ('The daimonion is not magic. It is training.',
     'The daimonion is training.'),
    # NEG remove: em-dash pattern
    ('It is not that the daimonion was exceptional — it was that Socrates was exceptional.',
     'Socrates was exceptional.'),
    # NEG remove
    ('The daimonion is not Socrates\' exclusive property. It is a universal human faculty',
     'The daimonion is a universal human faculty'),
    # NEG remove
    ('You do not summon the daimonion. You tune yourself until you can hear it.',
     'You tune yourself until you can hear it.'),
    # NEG remove: multiple NEGs in one sentence
    ('The daimonion is not a substitute for reason. It is not a shortcut to wisdom. It is a warning system',
     'The daimonion is a warning system'),
]),
('expansion-essay35.md', [
    # NEG remove
    ('they are not devotional poetry. They are theurgy in practice',
     'they are theurgy in practice'),
    # NEG remove
    ('Prayer is not asking. Prayer is turning.',
     'Prayer is turning.'),
    # NEG remove
    ('Prayer is not a request. It is a re-cognition.',
     'Prayer is a re-cognition.'),
    # NEG remove
    ('You do not read a Proclus hymn to appreciate its beauty. You chant it to change your being.',
     'You chant it to change your being.'),
]),
('expansion-essay3.md', [
    # NEG remove
    ('The mirror does not pre-exist the reflection. They arise together, inseparable, like the flame and its light.',
     'The mirror and reflection arise together, inseparable, like the flame and its light.'),
    # NEG remove: em-dash
    ('Recognition is not seeing something new — it is seeing that seeing and being are the same act.',
     'Recognition is seeing that seeing and being are the same act.'),
]),
('expansion-essay14.md', [
    # NEG remove: em-dash
    ('This is not pantheism — the claim that everything is God. It is something stranger and more intimate',
     'This is something stranger and more intimate'),
]),
('expansion-essay48.md', [
    # Most NEGs are in blockquotes or don't follow the pattern
]),
('expansion-essay34.md', [
    # NEG remove: "not an explosion but an awakening"
    ('There was no Big Bang in the sense science imagines. What happened was not an explosion but an awakening.',
     'There was no Big Bang in the sense science imagines. What happened was an awakening.'),
    # NEG remove
    ('This is not a denial of change. It is a relocation of the mechanism.',
     'This is a relocation of the mechanism.'),
    # NEG remove
    ('Consciousness is not something that emerges from matter. Matter is something that emerges from consciousness.',
     'Matter is something that emerges from consciousness.'),
    # NEG remove
    ('Value fulfillment is not survival. It is enhancement.',
     'Value fulfillment is enhancement.'),
    # NEG remove
    ('This is not a sentimental wish. It is the actual physics of Seth\'s universe.',
     'This is the actual physics of Seth\'s universe.'),
    # NEG remove
    ('The cooperative venture is not an ideal to strive toward. It is the foundation that has always been there',
     'The cooperative venture is the foundation that has always been there'),
    # NEG remove: "not mechanical failure but meaningful expression"
    ('Illness is not mechanical failure but meaningful expression',
     'Illness is meaningful expression'),
    # NEG remove
    ('Illness, in this framework, is not something that happens to you. It is something you participate in creating',
     'Illness, in this framework, is something you participate in creating'),
]),
('expansion-essay30.md', [
    # The corrupted version should be mostly OK
]),
('expansion-essay26.md', [
    # NEG remove: most NEGs are in blockquotes
]),
('expansion-essay20.md', [
    # The corrupted version should be mostly OK
]),
('expansion-essay18.md', [
    # NEG remove
    ('These channels are not metaphorical. They are as real as arteries',
     'These channels are as real as arteries'),
    # NEG remove
    ('These seven centers are not locations in the physical body. They are thresholds in the subtle body',
     'These seven centers are thresholds in the subtle body'),
    # NEG remove
    ('The subtle body is not a metaphor for the nervous system. It is a parallel infrastructure',
     'The subtle body is a parallel infrastructure'),
]),
]


def apply_fixes():
    for fname, fixes in FIXES:
        src = os.path.join(BKP, fname + '.bak')
        dst = os.path.join(BASE, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        
        if not os.path.exists(dst):
            print(f'Skipping {fname} (not found)')
            continue
        
        with open(dst, 'r') as f:
            content = f.read()
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f'  {fname}: Fixed pattern: {old[:50]}...')
            else:
                print(f'  {fname}: NOT FOUND: {old[:50]}...')
        
        with open(dst, 'w') as f:
            f.write(content)
        print(f'  {fname}: Done')


if __name__ == '__main__':
    apply_fixes()
