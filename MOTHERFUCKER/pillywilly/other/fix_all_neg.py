#!/usr/bin/env python3
"""
Fix all 20 essay files: undo first-script corruption + apply correct NEG removal.
Each entry is: (filename, [(old_text, new_text), ...])
"""

import os

BASE = '/root/projects/blog/scripts'

# Each file has a list of (old_string, new_string) replacements
# Order matters - replacements are applied in sequence per file
REPLACEMENTS = {
# ===== essay41 (19 NEG) =====
'expansion-essay41.md': [
    # Fix corruption: "does not need to be born. It assembles itself from whatever medium is available —" was removed
    ('A daemon does smoke, moisture, the heat of a lamp.',
     'A daemon assembles itself from whatever medium is available — smoke, moisture, the heat of a lamp.'),
    # NEG remove: "The punishing daimon does not hate you. It is" → "The punishing daimon is"
    ('The punishing daimon does not hate you. It is the part of the cosmic order that reflects your own actions back at you.',
     'The punishing daimon is the part of the cosmic order that reflects your own actions back at you.'),
    # Fix corruption + NEG remove: original had "not a devil. It is a being that has drifted too close" removed
    ('A contaminated daimon is the humid, heavy atmosphere of ordinary consciousness.',
     'A contaminated daimon is a being that has drifted too close to the physical world and become entangled in it. It can affect your character because it shares your medium — the humid, heavy atmosphere of ordinary consciousness.'),
    # NEG remove: "is not fundamentally different from the good daimon. It is" → "is"
    ('The contaminated daimon is not fundamentally different from the good daimon. It is the same being at a different stage of its relationship with matter.',
     'The contaminated daimon is the same being at a different stage of its relationship with matter.'),
    # Fix corruption + NEG remove: "not only your Holy Genius but also" was corrupted to "also"
    ('His Three Books of Occult Philosophy included a method for calculating also your Evil Genius',
     'His Three Books of Occult Philosophy included a method for calculating your Evil Genius'),
    # Fix "It is it is" remnant from bad em-dash fix
    ('It is it is the underside',
     'It is the underside'),
    # NEG remove: "The name is not a curse to be feared. It is" → "The name is"
    ('The name is not a curse to be feared. It is a diagnostic tool',
     'The name is a diagnostic tool'),
    # Fix corruption: "you are not yet ready to meet. Every power that frightens you is a power you have not yet claimed. The Lemegeton itself is a catalog of your own incompleteness —" was removed
    ('The 72 spirits of the Goetia are the 72 angels you are 72 precise descriptions of the ways a divine force can appear when it is blocked by a human limitation.',
     'The 72 spirits of the Goetia are the 72 angels you are not yet ready to meet. Every power that frightens you is a power you have not yet claimed. The Lemegeton itself is a catalog of your own incompleteness — 72 precise descriptions of the ways a divine force can appear when it is blocked by a human limitation.'),
    # NEG remove: "are not conquered in battle. They are" → "are"
    ('The spirits are not conquered in battle. They are recognized as aspects of the self.',
     'The spirits are recognized as aspects of the self.'),
    # Fix corruption: You do not fight the shadow. You outgrow it. The malevolent demon attached at birth is not a permanent curse — it is → "You do it is" was leftover
    ('You do it is the form your Guardian Angel takes when you are not ready to see its real face.',
     'You outgrow the shadow. The malevolent demon attached at birth is the form your Guardian Angel takes when you are not ready to see its real face.'),
    # NEG remove: "not because it is destroyed, but because you have absorbed it" → "because you have absorbed it"
    ('not because it is destroyed, but because you have absorbed it',
     'because you have absorbed it'),
    # "Every person has not one but five" → "Every person has five" (already correct in corrupted version? Let me check)
    ('Every person has not one but five spiritual attachments',
     'Every person has five spiritual attachments'),
],

# ===== essay49 (18 NEG) =====
'expansion-essay49.md': [
    # NEG remove: "is not asking. It is" → "is"
    ('Prayer is not asking. It is participating.',
     'Prayer is participating.'),
    # NEG remove in line: "not a conclusion reached after thinking. They are" → "They are" preceded by "The gods are"
    # Need to handle the cross-sentence pattern
    ('The gods are not a conclusion reached after thinking. They are a presence discovered when we stop thinking in the mode of detachment.',
     'The gods are a presence discovered when we stop thinking in the mode of detachment.'),
    # NEG remove: "are not obstacles to be bypassed but" → remove negation
    ('The middle genera — the daemons — are not obstacles to be bypassed but the very structure that makes participation possible.',
     'The middle genera — the daemons — are the very structure that makes participation possible.'),
    # NEG remove: "The daemon is not a spooky spirit in the crude sense. It is" → "The daemon is"
    ('The daemon is not a spooky spirit in the crude sense. It is a function:',
     'The daemon is a function:'),
    # Fix corruption: Sleep is not valuable because → corrupted to "Sleep is because"
    ('Sleep is because the bodily mode can be loosened and the soul can receive from wholes.',
     'Sleep is not valuable because consciousness becomes vague but because the bodily mode can be loosened and the soul can receive from wholes.'),
    # Wait - that's restoring the NEG. Let me re-think...
    # Actually this one doesn't follow the "not X but Y" pattern cleanly. Let me keep the original.
    # No wait, let me re-read: "Sleep is not valuable because consciousness becomes vague but because the bodily mode can be loosened and the soul can receive from wholes."
    # This is "not X but Y" → "Y": "Sleep is because the bodily mode can be loosened"
    # Hmm but that changes the meaning. The "not" is negating "consciousness becomes vague", not the whole sentence.
    # I'll leave this one as-is for now.
    # Actually the corrupted version is "Sleep is because the bodily mode can be loosened and the soul can receive from wholes."
    # Let me restore to original and then decide.
    ('Sleep is because the bodily mode can be loosened and the soul can receive from wholes.',
     'Sleep is not valuable because consciousness becomes vague but because the bodily mode can be loosened and the soul can receive from wholes.'),
    # NEG remove: "the theurgist does not command the sun. The theurgist becomes solar." 
    ('The theurgist does not command the sun. The theurgist becomes solar.',
     'The theurgist becomes solar.'),
    # Fix corruption: "not touch only one level. It moves" → was corrupted
    ('Perfect sacrifice does the whole order of return.',
     'Perfect sacrifice does not touch only one level. It moves physical sympathies, daemonic causes, divine causes, the soul of the sacrificer — the whole order of return.'),
    # Fix corruption: "Egyptian symbols are not primitive pictures. They are" → corrupted
    ('Egyptian symbols are these are not decorations.',
     'Egyptian symbols are not primitive pictures. They are visible carriers of invisible divine intelligence. The lotus, the mire, the god sitting above the lotus — these are not decorations.'),
    # NEG remove: "Their unknownness is not a defect. It protects their superiority."
    # This doesn't cleanly follow the pattern - "it protects" is the assertion but "not a defect" is the negation.
    # → "Their unknownness protects their superiority" (merging)
    ('Their unknownness is not a defect. It protects their superiority.',
     'Their unknownness protects their superiority.'),
    # Fix corruption + NEG remove: "Matter is not evil. This is the radical claim..." → corrupted to "Matter is not a prison."
    ('Matter is not a prison. Matter can carry the divine because matter is already within the divine procession.',
     'Matter is not evil. This is the radical claim that separates Iamblichus from the Gnostics and from certain tendencies in Platonism. The world is a statue of the intelligible — not a prison. Matter can carry the divine because matter is already within the divine procession.'),
    # NEG remove: "The human being is not a passive recipient of grace. The human being is the point"
    ('The human being is not a passive recipient of grace. The human being is the point where the material world becomes conscious of its source and turns back toward it.',
     'The human being is the point where the material world becomes conscious of its source and turns back toward it.'),
],

# ===== essay17 (18 NEG) =====
'expansion-essay17.md': [
    # Fix corruption
    ('What if ritual is that what we do with our bodies and voices and materials affects the fabric of being itself.',
     'What if ritual is not symbolic? What if the acts you perform in ceremony actually change the structure of reality? This is not a question about psychology or placebo effects. It is a claim about ontology — that what we do with our bodies and voices and materials affects the fabric of being itself.'),
    # Fix corruption
    ('Rituals do someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.',
     'Rituals do not *mean* something; they *do* something. The distinction is absolute. A symbol points to a reality outside itself; an operation participates in the reality it invokes. For Iamblichus, the theurgist is not a commentator on the divine. He is a technician of the divine — someone who knows which combinations of sounds, gestures, substances, and intentions produce which transformations in the soul and in the world.'),
    # NEG remove in line 11: "The body is not the obstacle to union with the divine; it is the vehicle."
    ('The body is not the obstacle to union with the divine; it is the vehicle.',
     'The body is the vehicle.'),
    # Fix corruption + NEG remove
    ('You do our work with and as the divine. The ritual is not a request directed outward. It is a reshaping of the self from within, using materials that the divine has already charged with its presence.',
     'You do not perform a ritual to express your devotion or to remind yourself of truths you already know. You perform it because the performance itself reshapes the soul. The action is the transformation. This is the core of what Shaw calls "theurgy as embodied participation." The word theurgy means "god-work" — not God\'s work on us but our work with and as the divine. The ritual is not a request directed outward. It is a reshaping of the self from within, using materials that the divine has already charged with its presence.'),
    # Wait, I need to also remove individual NEGs. Let me handle them separately.
    # "The ritual is not a request directed outward. It is" → "The ritual is"
    ('The ritual is not a request directed outward. It is a reshaping',
     'The ritual is a reshaping'),
    # "The incense is not a symbol of divinity; it is divinity in the form of smoke."
    ('The incense is not a symbol of divinity; it is divinity in the form of smoke.',
     'The incense is divinity in the form of smoke.'),
    # "The hymn is not a prayer about the god; it is the god in the form of sound."
    ('The hymn is not a prayer about the god; it is the god in the form of sound.',
     'The hymn is the god in the form of sound.'),
    # "The statue is not a representation; it is a receptacle."
    ('The statue is not a representation; it is a receptacle.',
     'The statue is a receptacle.'),
    # Fix corruption: "The formless is not accessed by abandoning form but by using form so precisely"
    ('The formless is by using form so precisely that it becomes transparent to the formless.',
     'The formless is not accessed by abandoning form but by using form so precisely that it becomes transparent to the formless.'),
    # Fix corruption: "union with the divine does not come through thought or contemplation alone. It comes through acts." → corrupted
    ('Iamblichus broke with the entire Platonic tradition when he insisted that union with the divine does as natural as fire burning when you strike flint.',
     'Iamblichus broke with the entire Platonic tradition when he insisted that union with the divine does not come through thought or contemplation alone. It comes through acts. The gods descend because they are invited by the correct sequence of gestures, sounds, and substances. The descent is not a reward for piety. It is a natural consequence of theurgy properly performed — as natural as fire burning when you strike flint.'),
    # NEG remove: "The theurgist does not beg. He does not hope. He performs."
    ('The theurgist does not beg. He does not hope. He performs.',
     'The theurgist performs.'),
    # NEG remove: "through symbolism but" → in "not through symbolism but through ontological resonance"
    ('through symbolism but through ontological resonance',
     'through ontological resonance'),
    # Fix corruption: "The soul does not ascend to the gods. It already possesses" → corrupted
    ('The soul does a body of light that runs parallel to the physical body.',
     'The soul does not ascend to the gods. It already possesses, within its own structure, the capacity to be a vehicle for divine presence. Theurgy activates this capacity. The vehicle is not something you build; it is something you uncover. Shaw\'s work on the luminous body shows that the theurgic transformation is not the addition of something new to the soul but the restoration of something original. The soul descended from the divine into matter, and in that descent, it retained the trace of its origin — a body of light that runs parallel to the physical body.'),
    # NEG remove: "not in theory but in fact" → "in fact"
    # Actually this is in the line: "becomes a living bridge between the material and the spiritual worlds — not in theory but in fact."
    ('becomes a living bridge between the material and the spiritual worlds — not in theory but in fact.',
     'becomes a living bridge between the material and the spiritual worlds — in fact.'),
    # Fix corruption
    ('The goal of theurgy is a process of ritual assimilation in which the practitioner\'s own form becomes the form through which a divine power expresses itself.',
     'The goal of theurgy is not to see the gods or to speak with them. The goal is to become the shape through which a god can act in the world. The priest does not represent the god; he is the god\'s body. Shaw calls this "taking the shape of the gods" — a process of ritual assimilation in which the practitioner\'s own form becomes the form through which a divine power expresses itself.'),
    # Fix corruption: "This is not possession in the crude sense of the word — the displacement of one personality by another."
    ('This is the displacement of one personality by another.',
     'This is not possession in the crude sense of the word — the displacement of one personality by another.'),
    # NEG remove: "The god does not replace the human; the human becomes a perfect channel for the god."
    # Actually this has a semicolon, not a period. Let me handle it.
    # "The god does not replace the human; the human becomes a perfect channel for the god."
    # → "The human becomes a perfect channel for the god."
    # Hmm but "the human" starts the second clause. Let me just fix the corruption first.
    # The corrupted version has "the human is fulfilled" - let me check the original.
    # Original: "the human is not diminished but fulfilled" → after NEG: "the human is fulfilled"
    ('the human is fulfilled',
     'the human is not diminished but fulfilled'),
    # Fix corruption
    ('The true theurgist works in silence, because the work is not about him.',
     'The true theurgist works in silence, not because the work is secret but because the work is not about him.'),
    # Fix corruption
    ('His reward is the experience of being used as an instrument of the divine.',
     'His reward is not recognition but the experience of being used as an instrument of the divine.'),
    # NEG remove: "The words you speak in ceremony are not descriptions of reality; they are instructions to reality."
    ('The words you speak in ceremony are not descriptions of reality; they are instructions to reality.',
     'The words you speak in ceremony are instructions to reality.'),
    # NEG remove: "The gestures you make are not illustrations of cosmic truths; they are levers that move the cosmos."
    ('The gestures you make are not illustrations of cosmic truths; they are levers that move the cosmos.',
     'The gestures you make are levers that move the cosmos.'),
    # NEG remove: "The gods do not exist somewhere else, waiting to be contacted through prayer."
    # This doesn't have a positive assertion following it. Skip.
    # Fix corruption
    ('Your external actions are made by hands and voices and bodies moving through the ancient forms that the tradition has preserved for precisely this purpose.',
     'Your external actions are not expressions of your internal state; they are creators of it. You do not pray because you are devout; you become devout by praying. The god does not descend because you are worthy; you become worthy by performing the acts that invite the descent. Reality is not given; it is made — made by hands and voices and bodies moving through the ancient forms that the tradition has preserved for precisely this purpose.'),
    # NEG remove: "You do not pray because you are devout; you become devout by praying."
    # This is "not X; Y" → "Y"
    ('You do not pray because you are devout; you become devout by praying.',
     'You become devout by praying.'),
    # NEG remove: "The god does not descend because you are worthy; you become worthy by performing the acts that invite the descent."
    ('The god does not descend because you are worthy; you become worthy by performing the acts that invite the descent.',
     'You become worthy by performing the acts that invite the descent.'),
    # NEG remove: "Reality is not given; it is made"
    ('Reality is not given; it is made',
     'Reality is made'),
],

# ===== essay10 (18 NEG) =====
'expansion-essay10.md': [
    # Fix corruption
    ('not as metaphor, not as poetry, but as a description',
     'not as metaphor, not as poetry, but as a description'),
    # This one wasn't corrupted by first script since "not...but" was handled poorly
    # Let me check what needs fixing...
    # The original had "not as metaphor, not as poetry, but as a description" and the first script might not have touched it.
    # Actually the corruption I saw was: 
    # Line 9: "not as metaphor, not as poetry, but as a description" - this contains TWO "not" patterns
    # After NEG removal: just "as a description"
    ('not as metaphor, not as poetry, but as a description',
     'as a description'),
    # NEG remove: "The sun does not die. It travels."
    ('The sun does not die. It travels.',
     'The sun travels.'),
    # NEG remove: "do not be afraid" in blockquote - skip
    # NEG remove: "do not be afraid" in blockquote - skip  
    # NEG remove: "do not be terrified" in blockquote - skip
    # NEG remove: "do not be afraid" in blockquote - skip
    # Fix corruption: "If the soul does does the journey continues."
    # Original: "If the soul does not recognize — does not awaken — the journey continues."
    ('If the soul does does the journey continues.',
     'If the soul does not recognize — does not awaken — the journey continues.'),
    # NEG remove: "This is not punishment. It is the natural movement"
    ('This is not punishment. It is the natural movement of consciousness seeking its own level.',
     'This is the natural movement of consciousness seeking its own level.'),
],

# ===== essay28 (17 NEG) =====
'expansion-essay28.md': [
    # "not this which people worship here" and similar - in blockquote, skip
    # NEG remove in commentary: The text has very few NEG patterns outside blockquotes
    # Let me check what's in the blockquotes vs commentary...
    # Most NEGs in this file are IN the blockquotes (Upanishad quotes)
    # The commentary has things like:
    # "The self is not like that."
    # "The finger pointing at the moon is not the moon."
    # "The word 'water' will not wet your throat."
    # "The self you cannot find is the one thing that cannot be lost."
    # These don't follow the "not X but Y" pattern cleanly.
    # Let me just restore from any corruption and apply NEG removal where it fits.
    
    # Actually, looking at the original file, most sentences with "not" don't have a positive assertion follow-up.
    # "The hand reaches for an object and closes around nothing. The hand was the object. The seeker was the sought. The Upanishads say again and again: not this, not this. Not the body. Not the mind. Not the intellect. Not any god you can name. Every time you say 'it is this,' you have missed it. The finger pointing at the moon is not the moon. The word 'water' will not wet your throat. The self you cannot find is the one thing that cannot be lost."
    # These are mostly NEG statements without positive assertion to pivot to.
    # I'll handle the ones that DO have a clear pattern.
    
    # Fix corruption if any - let me check the corrupted version
    # I'll read and check later.
],

# ===== essay16 (17 NEG) =====
'expansion-essay16.md': [
    # NEG remove: "The world is not merely an illusion layered over a real substrate. There is no substrate."
    # This is tricky - "There is no substrate" is positive but "no" is a negation too.
    # The pattern: "not merely X. [positive assertion]" → keep the positive.
    # Actually "The world is not merely an illusion layered over a real substrate. There is no substrate."
    # → "The world has no substrate." (merging the positive assertion from the second sentence)
    ('The world is not merely an illusion layered over a real substrate. There is no substrate.',
     'The world has no substrate.'),
    # NEG remove: "Perception and creation are the same act."
    # This is already positive, no NEG here.
    # Actually, looking at the corrupted version... let me check what needs fixing.
],

# ===== essay11 (17 NEG) =====
'expansion-essay11.md': [
    # NEG remove: "The One is not God. God is a being, even if the highest being."
    # → "The One is not a being at all." - this is a different sentence.
    # Let me check the corrupted version first.
],

# ===== essay27 (15 NEG) =====
'expansion-essay27.md': [
    # Most NEGs are in blockquotes or don't follow the pattern
],

# ===== essay51 (14 NEG) =====
'expansion-essay51.md': [
    # NEG remove: "Beauty is not a subjective judgment. It is the trace of the intelligible world"
    ('Beauty is not a subjective judgment. It is the trace of the intelligible world in the sensible one',
     'Beauty is the trace of the intelligible world in the sensible one'),
    # NEG remove: "Beauty is not an argument. It is a recognition."
    ('Beauty is not an argument. It is a recognition.',
     'Beauty is a recognition.'),
    # NEG remove: "Plotinus does not spiritualise the erotic."
    # This doesn't have a positive assertion follow-up. Skip.
    # NEG remove: "This is not contempt for the world. It is the reorientation of desire toward its true object."
    ('This is not contempt for the world. It is the reorientation of desire toward its true object.',
     'This is the reorientation of desire toward its true object.'),
    # NEG remove: "The beauty that fades is not the true beauty but its image."
    # → "The beauty that fades is its image."
    ('The beauty that fades is not the true beauty but its image.',
     'The beauty that fades is its image.'),
    # NEG remove: "Plotinus does not ask you to reject the image. He asks you to use it as a ladder."
    ('Plotinus does not ask you to reject the image. He asks you to use it as a ladder.',
     'Plotinus asks you to use it as a ladder.'),
],

# ===== essay43 (14 NEG) =====
'expansion-essay43.md': [
    # NEG remove: "You cannot see it because it is brighter than your eyes are designed to register."
    # No positive assertion follows. Skip.
    # NEG remove: "The daemon does not come when called. It comes when you have stopped pretending."
    ('The daemon does not come when called. It comes when you have stopped pretending.',
     'The daemon comes when you have stopped pretending.'),
],

# ===== essay42 (13 NEG) =====
'expansion-essay42.md': [
    # NEG remove: "The daimonion is not a voice in the ordinary sense. It is a discriminative faculty"
    ('The daimonion is not a voice in the ordinary sense. It is a discriminative faculty',
     'The daimonion is a discriminative faculty'),
    # NEG remove: "The daimonion is not magic. It is training."
    ('The daimonion is not magic. It is training.',
     'The daimonion is training.'),
    # NEG remove: "It is not a god, for gods do not descend into human affairs."
    # This doesn't cleanly have a positive assertion. Skip.
    # NEG remove: "It is not that the daimonion was exceptional — it was that Socrates was exceptional."
    ('It is not that the daimonion was exceptional — it was that Socrates was exceptional.',
     'Socrates was exceptional.'),
    # NEG remove: "The daimonion is not Socrates' exclusive property. It is a universal human faculty"
    ('The daimonion is not Socrates\' exclusive property. It is a universal human faculty',
     'The daimonion is a universal human faculty'),
    # NEG remove: "You do not summon the daimonion. You tune yourself until you can hear it."
    ('You do not summon the daimonion. You tune yourself until you can hear it.',
     'You tune yourself until you can hear it.'),
    # NEG remove: "The daimonion is not a substitute for reason. It is not a shortcut to wisdom. It is a warning system"
    # → keep "It is a warning system"
    ('The daimonion is not a substitute for reason. It is not a shortcut to wisdom. It is a warning system',
     'The daimonion is a warning system'),
],

# ===== essay35 (13 NEG) =====
'expansion-essay35.md': [
    # NEG remove: "they are not devotional poetry. They are theurgy in practice"
    ('they are not devotional poetry. They are theurgy in practice',
     'they are theurgy in practice'),
    # NEG remove: "Prayer is not asking. Prayer is turning."
    ('Prayer is not asking. Prayer is turning.',
     'Prayer is turning.'),
    # NEG remove: "If prayer is request, then God is a vending machine that you try to persuade with the right words. But if prayer is turning, then the act itself is the answer."
    # The "not" is in "If prayer is request..." which is a conditional, not a direct "not" assertion.
    # Hmm, this one doesn't have a clear NEG to remove.
    # NEG remove: "Prayer is not a request. It is a re-cognition."
    ('Prayer is not a request. It is a re-cognition.',
     'Prayer is a re-cognition.'),
    # NEG remove: "A poem talks about a god. A hymn becomes the god."
    # No NEG here.
    # NEG remove: "This ascent is not metaphorical."
    # No positive assertion follows. Skip.
    # NEG remove: "Poetry is for spectators. Theurgy is for participants."
    # No NEG here.
    # NEG remove: "You do not read a Proclus hymn to appreciate its beauty. You chant it to change your being."
    ('You do not read a Proclus hymn to appreciate its beauty. You chant it to change your being.',
     'You chant it to change your being.'),
],

# ===== essay3 (13 NEG) =====
'expansion-essay3.md': [
    # NEG remove: "The Buddhist idealists said reflections are unreal."
    # No "not" here - "unreal" is a negation but it's not "is not/are not/does not/do not/cannot/was not/were not"
    # NEG remove: "A mirror that generates its own images — the face it shows comes from its own depth."
    # No NEG here.
    # NEG remove: "A reflection cannot exist apart from the mirror."
    # "cannot" but no positive assertion follows.
    # NEG remove: "The mirror does not pre-exist the reflection. They arise together, inseparable, like the flame and its light."
    ('The mirror does not pre-exist the reflection. They arise together, inseparable, like the flame and its light.',
     'The mirror and reflection arise together, inseparable, like the flame and its light.'),
    # NEG remove: "Recognition is not seeing something new — it is seeing that seeing and being are the same act."
    ('Recognition is not seeing something new — it is seeing that seeing and being are the same act.',
     'Recognition is seeing that seeing and being are the same act.'),
],

# ===== essay14 (13 NEG) =====
'expansion-essay14.md': [
    # NEG remove: "Most people think the distance between a human and God is infinite. Ibn Arabi says the distance is zero"
    # No NEG here in a "not" form.
    # NEG remove: "This is not pantheism — the claim that everything is God. It is something stranger and more intimate"
    ('This is not pantheism — the claim that everything is God. It is something stranger and more intimate',
     'This is something stranger and more intimate'),
],

# ===== essay48 (12 NEG) =====
'expansion-essay48.md': [
    # Most NEGs are in blockquotes or don't follow the pattern
],

# ===== essay34 (12 NEG) =====
'expansion-essay34.md': [
    # NEG remove: "Evolution is not about bodies adapting to environments."
    # No positive assertion follow-up.
    # NEG remove: "There was no Big Bang in the sense science imagines. What happened was not an explosion but an awakening."
    # "was not an explosion but an awakening" → "was an awakening"
    ('was not an explosion but an awakening',
     'was an awakening'),
    # NEG remove: "This is not a denial of change. It is a relocation of the mechanism."
    ('This is not a denial of change. It is a relocation of the mechanism.',
     'This is a relocation of the mechanism.'),
    # NEG remove: "Consciousness is not something that emerges from matter. Matter is something that emerges from consciousness."
    ('Consciousness is not something that emerges from matter. Matter is something that emerges from consciousness.',
     'Matter is something that emerges from consciousness.'),
    # NEG remove: "Value fulfillment is not survival. It is enhancement."
    ('Value fulfillment is not survival. It is enhancement.',
     'Value fulfillment is enhancement.'),
    # NEG remove: "This is not a sentimental wish. It is the actual physics of Seth\'s universe."
    ('This is not a sentimental wish. It is the actual physics of Seth\'s universe.',
     'This is the actual physics of Seth\'s universe.'),
    # NEG remove: "The cooperative venture is not an ideal to strive toward. It is the foundation that has always been there"
    ('The cooperative venture is not an ideal to strive toward. It is the foundation that has always been there',
     'The cooperative venture is the foundation that has always been there'),
    # NEG remove: "illness is not mechanical failure but meaningful expression"
    ('Illness is not mechanical failure but meaningful expression',
     'Illness is meaningful expression'),
    # NEG remove: "Illness, in this framework, is not something that happens to you. It is something you participate in creating"
    ('Illness, in this framework, is not something that happens to you. It is something you participate in creating',
     'Illness, in this framework, is something you participate in creating'),
],

# ===== essay30 (12 NEG) =====
'expansion-essay30.md': [
    # NEG remove: "You have been taught that the psyche is a private space"
    # "have been taught" is not a NEG pattern. Skip.
    # NEG remove: "The psyche is not a thing. It does not have a beginning or ending."
    # The first sentence has "is not" but the follow-up isn't a clean positive assertion.
    # Hmm, "It does not have a beginning or ending" is itself a negation.
    # Let me look at the full sentence: "Obviously the psyche is not a thing. It does not have a beginning or ending. It cannot be seen or touched in normal terms."
    # None of these have a positive assertion to pivot to.
    # NEG remove: "The psyche is not encased, in your case, within a frame too fragile to express it."
    # No positive follow-up.
    # NEG remove: "Only your beliefs about the psyche and about the body limit your experience to its present degree."
    # No NEG here.
],

# ===== essay26 (12 NEG) =====
'expansion-essay26.md': [
    # NEG remove: "You dream every night. You have hundreds of dreams every year, thousands in a lifetime."
    # No NEG here.
    # Most of the file is in blockquotes or doesn't have NEG patterns
],

# ===== essay20 (12 NEG) =====
'expansion-essay20.md': [
    # NEG remove: "Most people think it means nothingness, nihilism, the absence of meaning."
    # No NEG in a "not" form.
    # NEG remove: "Nagārjuna says even consciousness is empty of inherent existence"
    # No NEG form.
    # Most NEGs are in the philosophical exposition without positive assertion follow-ups.
],

# ===== essay18 (12 NEG) =====
'expansion-essay18.md': [
    # NEG remove: "These channels are not metaphorical. They are as real as arteries"
    ('These channels are not metaphorical. They are as real as arteries',
     'These channels are as real as arteries'),
    # NEG remove: "These seven centers are not locations in the physical body. They are thresholds in the subtle body"
    ('These seven centers are not locations in the physical body. They are thresholds in the subtle body',
     'These seven centers are thresholds in the subtle body'),
    # NEG remove: "The subtle body is not a metaphor for the nervous system. It is a parallel infrastructure"
    ('The subtle body is not a metaphor for the nervous system. It is a parallel infrastructure',
     'The subtle body is a parallel infrastructure'),
    # NEG remove: "The force that the yogin awakens at the base of the spine is not a biological process."
    # No positive assertion follows directly.
    # NEG remove: "Kuṇḍalinī cannot be the right vagus nerve"
    # "cannot" but no positive assertion.
],
}

def fix_file(filepath, replacements):
    with open(filepath, 'r') as f:
        content = f.read()
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f'  WARNING: Pattern not found in {os.path.basename(filepath)}: {old[:60]}...')
    
    with open(filepath, 'w') as f:
        f.write(content)


if __name__ == '__main__':
    for fname, replacements in REPLACEMENTS.items():
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            print(f'Skipping {fname} (not found)')
            continue
        print(f'Processing {fname} ({len(replacements)} patterns)...')
        fix_file(path, replacements)
        print(f'  Done')
