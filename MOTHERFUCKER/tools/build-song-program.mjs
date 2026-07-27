#!/usr/bin/env node

import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { buildDeterministicProgram } from "../src/program-builder.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

const continuitySystems = [
  {
    id: "relational-song",
    meaning: "The essay's invariant pattern: real only through transformations, never owned by one performance.",
    treatment: "A gold interval-pattern returns in different geometries. Its relations persist while instruments, scale, and material change.",
  },
  {
    id: "local-interface",
    meaning: "The operationally real boundary through which a finite perspective selects and acts.",
    treatment: "Indigo apertures and rings admit some marks, exclude others, and remain porous enough for reciprocal exchange.",
  },
  {
    id: "dependency-field",
    meaning: "The enabling network that prevents any participant from becoming an isolated source.",
    treatment: "Fine gold and indigo links carry delayed pulses without a privileged root node.",
  },
  {
    id: "ownership-knot",
    meaning: "The extra claim that a local self owns, originates, or must permanently secure the process.",
    treatment: "A crimson feedback branch tightens around a still-functional gold current, then cools without erasing the current.",
  },
  {
    id: "memory-trace",
    meaning: "The past surviving as a transformed constraint interpreted by a changed receiver.",
    treatment: "A travelling trace changes shape and routing weights across time instead of appearing as an intact recording.",
  },
  {
    id: "listening-current",
    meaning: "Recognition becoming ethical coordination among partial local worlds.",
    treatment: "Distinct instruments retain their colors while pulses retune and propagate across their shared field.",
  },
  {
    id: "open-frontier",
    meaning: "The unresolved disagreement about reflexive manifestation and final ground.",
    treatment: "Two paths share a bridge, diverge at the same luminous question, and remain visibly connected without forced closure.",
  },
];

const chapterBands = [
  [4, "Prologue · Four Starting Coordinates"],
  [36, "Preamble · Happy Birthday"],
  [38, "Part I · Seven Remembrances"],
  [50, "1 · Nothing Stands by Itself"],
  [68, "2 · Different Worlds of Relevance"],
  [80, "3 · Nature Achieves an Observer"],
  [100, "4 · Boundary Before Perspective"],
  [124, "5 · Memory as Translation"],
  [145, "6 · Identity Through Change"],
  [164, "7 · Recognition Without an Owner"],
  [195, "Part II · Pattern, Instrument, Performance"],
  [216, "Part III · Happy Birthday to a World"],
  [248, "Part IV · The Vortex"],
  [267, "Part V · The Cooling of Ownership"],
  [287, "Part VI · The Śaiva Question"],
  [329, "Part VII · The Bodhisattva"],
  [357, "Part VIII · Source, Disposition, Runtime"],
  [397, "Part IX · Direct Instruction"],
  [410, "Part X · What Recognition Is"],
  [430, "Part XI · The Open Why"],
  [460, "Coda · Happy Birthday, Again"],
  [477, "Final · Listening Inside the Song"],
];

const terms = {
  "identity-across-change": ["Anvaya", "अन्वयः"],
  dependency: ["Pratītya-samutpāda", "प्रतीत्यसमुत्पादः"],
  interface: ["Mukhadvāra", "मुखद्वारम्"],
  emergence: ["Utpāda", "उत्पादः"],
  containment: ["Maryādā", "मर्यादा"],
  selection: ["Vikalpa", "विकल्पः"],
  sequence: ["Kāla", "कालः"],
  feedback: ["Āvarta", "आवर्तः"],
  translation: ["Saṃskāra", "संस्कारः"],
  comparison: ["Upamā", "उपमा"],
  recursion: ["Pratyavekṣaṇa", "प्रत्यवेक्षणम्"],
  propagation: ["Paramparā", "परम्परा"],
  transformation: ["Pariṇāma", "परिणामः"],
  cessation: ["Nibbāna", "निब्बानम्"],
  inquiry: ["Vicāra", "विचारः"],
  divergence: ["Bheda", "भेदः"],
  convergence: ["Saṅgati", "सङ्गतिः"],
  "self-modification": ["Bhāvanā", "भावना"],
  coordination: ["Saṅghaṭana", "सङ्घटनम्"],
  differentiation: ["Viśeṣa", "विशेषः"],
};

function chapterFor(range) {
  return chapterBands.find(([end]) => range[0] <= end)?.[1] ?? chapterBands.at(-1)[1];
}

function beat(range, title, subtitle, role, operator, relation, visual, system, claim, extra = {}) {
  return {
    range,
    chapter: chapterFor(range),
    title,
    subtitle,
    role,
    operator,
    relation,
    visual,
    system,
    claim,
    term: terms[relation][0],
    devanagari: terms[relation][1],
    ...extra,
  };
}

const beats = [
  beat([1, 4], "Four Coordinates", "Relation, emptiness, interface, and reflexivity establish the field of inquiry.", "hook", "emerge", "emergence", "relational-birth", "relational-song", "The essay begins where four traditions converge on conditioned appearing without yet resolving its ultimate ground."),
  beat([5, 8], "Where Is the Song?", "The melody survives the loss of any piano or passing vibration.", "question", "compare", "identity-across-change", "pattern-ensemble", "relational-song", "A song cannot be reduced to one instrument or one transient acoustic event."),
  beat([9, 10], "No Hidden Container", "Neither score nor ideal performance can privately contain the whole pattern.", "objection", "frame", "containment", "smallness-cage", "relational-song", "Treating notation or an imagined perfect performance as the song simply relocates the mistaken container."),
  beat([11, 14], "One Pattern, Many Voices", "Different embodiments preserve enough relation for recognition.", "mechanism", "coordinate", "coordination", "dependency-network", "dependency-field", "Performances, memories, expectations, and possible transformations coordinate the song without a central owner."),
  beat([15, 19], "Invariant, Not Substance", "Identity persists across transformations but never stands outside them.", "thesis", "reveal", "identity-across-change", "pattern-ensemble", "relational-song", "The song is the recognizable invariant across performances, not a hidden object behind them."),
  beat([20, 23], "The Instrument Selects", "Construction opens one performable world while excluding others.", "definition", "differentiate", "interface", "boundary-gates", "local-interface", "An instrument actively selects which version of the pattern can occur through its particular capacities and limits."),
  beat([24, 26], "The Event Is Real", "Temporary coordination is an event, not an illusion.", "example", "reveal", "emergence", "multiscale-agent", "relational-song", "A performance becomes real when material, action, memory, expectation, and listening coordinate for a time."),
  beat([27, 28], "Nothing Plays Alone", "Pianist, learning, culture, and contrast enter the sounding event.", "mechanism", "construct", "dependency", "dependency-network", "dependency-field", "The current performance depends on nested histories and relations that no single participant contains."),
  beat([29, 33], "The Ownership Error", "A local instrument mistakes participation for authorship and permanence.", "objection", "enclose", "feedback", "powered-prison", "ownership-knot", "The self-like error appears when an instrument turns local disruption into evidence that music itself is owned or damaged."),
  beat([34, 36], "Music Without Possession", "The performance remains while the enclosing claim loses fuel.", "reversal", "open", "cessation", "opening-fist", "ownership-knot", "Recognition ends the attempt to possess the process rather than ending the real local performance."),
  beat([37, 38], "Seven Tests", "The remembrances are observational pressures, not imposed axioms.", "thesis", "reveal", "differentiation", "textures-display", "dependency-field", "Seven distinct examinations will test how relation, boundary, memory, identity, and recognition actually function."),

  beat([39, 42], "Identity Begins in Contrast", "Words, colors, and persons arise inside fields of difference.", "definition", "differentiate", "differentiation", "textures-display", "dependency-field", "Determinate identity is constituted through contrasts and enabling relations from the beginning."),
  beat([43, 45], "Relation Does Not Erase Reality", "Dependence revises substance without turning the world into nothing.", "reversal", "recontextualize", "transformation", "limitation-reversal", "dependency-field", "Relational existence is fully real even though no thing first completes itself in isolation."),
  beat([46, 50], "The Open Cup", "Remove clay, hands, use, gravity, and language; no private cup remains.", "mechanism", "construct", "dependency", "dependency-network", "dependency-field", "The cup is possible because it is open to a world of conditions, not because it contains independent cup-substance."),

  beat([51, 57], "Five Relevant Worlds", "Different bodies enact different domains of meaningful difference.", "example", "differentiate", "comparison", "umwelt-windows", "listening-current", "Bacterium, plant, tick, bat, and human do not merely hold opinions about one already-finished world."),
  beat([58, 64], "A Boundary Selects", "Sensing, memory, need, and action turn one branch into many meanings.", "example", "select", "selection", "umwelt-windows", "local-interface", "The same surroundings become different affordances because each organism selects relevance through embodied capacities."),
  beat([65, 68], "Worlds Intermingle", "Local centres remain partial while sharing and altering one nature.", "synthesis", "coordinate", "coordination", "tuning-network", "listening-current", "Nature is an interacting ecology of local worlds rather than either a private universe or one perspective-free inventory."),

  beat([69, 72], "No Witness in the Machine", "Observation emerges from coordinated discriminating, valuing, remembering, and acting.", "definition", "reveal", "emergence", "multiscale-agent", "local-interface", "An observer is an achieved organization of processes, not a tiny indivisible spectator added behind the eyes."),
  beat([73, 78], "Continuation by Activity", "Cell, tissue, animal, and person protect different scales of concern.", "mechanism", "coordinate", "coordination", "multiscale-agent", "dependency-field", "Organisms continue by coordinating protective activities across nested spatial, behavioural, and autobiographical scales."),
  beat([79, 80], "Concern Becomes One", "Many processes temporarily treat disturbances as one shared problem.", "thesis", "emerge", "emergence", "multiscale-agent", "local-interface", "The self is the scale at which distributed concern becomes sufficiently coordinated to act as a provisional one."),

  beat([81, 86], "Boundary Before Mind", "A perimeter first creates selective access, not consciousness.", "definition", "frame", "interface", "boundary-gates", "local-interface", "Inside and outside become operationally different before memory, value, or reflexive modelling create perspective."),
  beat([87, 90], "Channels of Partiality", "Entry, exclusion, threat, nourishment, and control precede a point of view.", "mechanism", "construct", "selection", "boundary-gates", "local-interface", "A boundary partitions causal access, and perspective appears only when further capacities organize that partiality."),
  beat([91, 96], "The Coordinates of Here", "Boundary, memory, prediction, value, and action construct a provisional centre.", "mechanism", "emerge", "emergence", "local-power", "local-interface", "Here, before, not-yet, better-or-worse, and alterable jointly generate the geometry of a finite agent."),
  beat([97, 100], "Five Dimensions of Finitude", "The kañcukas describe constraint, time, knowledge, action, and desire as enabling limits.", "comparison", "differentiate", "differentiation", "five-lenses", "local-interface", "Finitude is a structured set of limiting dimensions that makes a particular perspective possible rather than punishing it."),

  beat([101, 108], "The Past Is Not Retrieved", "Earlier encounters leave altered constraints that a later system must read.", "reversal", "recontextualize", "translation", "memory-relay", "memory-trace", "Memory is a transformed message reaching a receiver that did not exist in the same form when the trace was made."),
  beat([109, 114], "A Changed Receiver", "Continuity requires interpretation because sender and receiver are not identical.", "mechanism", "translate", "translation", "memory-relay", "memory-trace", "The present organism translates an earlier alteration through current body, goals, and environment."),
  beat([115, 119], "One Trace, Many Futures", "A constraint can become fear, wisdom, vigilance, compassion, or a released story.", "example", "differentiate", "differentiation", "textures-display", "memory-trace", "Memory outcomes diverge because the same trace is interpreted inside different present conditions."),
  beat([120, 124], "Memory Makes a World", "A trace directs attention, expectation, and prepared response.", "consequence", "sequence", "feedback", "causal-vortex", "memory-trace", "The deepest memory often acts as a readiness that helps construct the next self and its expected world."),

  beat([125, 132], "Continuity Through Change", "Matter, perception, belief, and capacity alter while some structure persists.", "thesis", "reveal", "identity-across-change", "morphing-invariant", "relational-song", "Personal identity functions through preserved invariants across change rather than through immobility."),
  beat([133, 139], "Flame, Melody, River", "Persistence depends on exchange, movement, and selective preservation.", "analogy", "compare", "comparison", "morphing-invariant", "relational-song", "Flame, melody, river, and person each show how continuity can require ongoing material transformation."),
  beat([140, 145], "Which Invariants Matter?", "Identity becomes an ethical question about what to preserve and release.", "question", "compare", "identity-across-change", "pattern-ensemble", "relational-song", "The practical problem is choosing worthwhile invariants rather than keeping every inherited pattern alive."),

  beat([146, 149], "Every Witness Is Noticed", "Each candidate observer becomes another appearance in the field.", "question", "recurse", "recursion", "recursive-observer", "ownership-knot", "Searching for an ultimate inner witness repeatedly turns the proposed witness into another observable object."),
  beat([150, 152], "One Process Models Both", "World, body, uncertainty, attention, and ownership enter one representational loop.", "mechanism", "construct", "recursion", "recursive-observer", "ownership-knot", "The organized process can model the world and aspects of its own modelling without adding an infinite series of watchers."),
  beat([153, 159], "The Knower Enters the Field", "Self-representation becomes one conditioned event among the known.", "recognition", "recurse", "recursion", "recursive-observer", "dependency-field", "Recognition includes the act of knowing inside the same dependent field it was examining."),
  beat([160, 164], "The Model Remains", "Functional self-representation continues while ownership loosens.", "reversal", "open", "cessation", "opening-fist", "ownership-knot", "Recognition weakens the stance of independent ownership without deleting the useful self-model."),

  beat([165, 170], "Correcting the Old Metaphor", "A pre-existing ideal song would reinstall hidden substance.", "objection", "frame", "containment", "smallness-cage", "relational-song", "The song must not be pictured as a perfect object stored beyond every performance."),
  beat([171, 177], "Distributed Reproducibility", "Bodies, scores, habits, memory, expectation, and future enactment sustain the pattern.", "definition", "reveal", "dependency", "dependency-network", "dependency-field", "The song is real as a reproducible pattern distributed across conditions, none of which contains or owns it completely."),
  beat([178, 180], "Three Functional Levels", "Pattern, instrument, and current event are distinct without becoming separate substances.", "definition", "differentiate", "differentiation", "textures-display", "relational-song", "The pattern, enabling local structure, and occurring performance must be distinguished to avoid category errors."),
  beat([181, 187], "Three Confusions", "Performance demands permanence, instrument claims authorship, pattern claims independence.", "consequence", "construct", "feedback", "powered-prison", "ownership-knot", "Suffering grows when each functional level recursively claims a privilege its conditions cannot provide."),
  beat([188, 191], "Impossible Requirements", "Permanence, isolated production, and context-free intelligibility fail in their own terms.", "objection", "compare", "transformation", "limitation-reversal", "ownership-knot", "Each ownership claim crashes against the event-like and relational structure required for music to exist."),
  beat([192, 195], "One Real Place", "Finitude is not the error; independence is.", "recognition", "recontextualize", "identity-across-change", "pattern-ensemble", "relational-song", "Liberation recognizes the instrument as one genuine site of music without making it the only source."),

  beat([196, 203], "A New Centre of Concern", "Birth operationally differentiates inside, outside, support, and threat.", "thesis", "emerge", "emergence", "relational-birth", "local-interface", "Birth creates a new place from which events can matter rather than an isolated substance."),
  beat([204, 210], "A World Learns Its Centre", "Touch, voice, object, body, history, and name assemble through interaction.", "mechanism", "construct", "emergence", "relational-birth", "local-interface", "A child's world and sense of mine emerge gradually through relationally coordinated distinctions."),
  beat([211, 216], "Constructed and Real", "Bridge, melody, and self can be constructed while still carrying consequence.", "reversal", "recontextualize", "dependency", "dependency-network", "dependency-field", "Construction does not imply falsity; the error begins only when a constructed pattern claims to stand alone."),

  beat([217, 224], "Reciprocal Reeds", "Consciousness and meaningful world lean upon and specify one another.", "analogy", "compare", "dependency", "reciprocal-reeds", "dependency-field", "Self-model and world-model arise reciprocally rather than as a finished subject inspecting a finished object."),
  beat([225, 235], "The Vortex Builds Evidence", "Expectation directs attention, interpretation, action, and a changed world back into memory.", "mechanism", "loop", "feedback", "causal-vortex", "memory-trace", "A self-confirming loop rebuilds the expected self and expected world through its own consequences.", {
    caption: "memory → expectation → attention → action → world",
  }),
  beat([236, 242], "A Useful Loop Hardens", "Inherited expectation saves work until the model hides its own participation.", "reversal", "recontextualize", "self-modification", "powered-prison", "ownership-knot", "Adaptive prediction becomes bondage when the system treats its model as reality rather than as a conditioned instrument."),
  beat([243, 248], "Grasping Confirms Itself", "A threatened identity repeatedly produces the evidence required to protect it.", "consequence", "sequence", "feedback", "causal-vortex", "ownership-knot", "Grasping is pathological self-confirmation in which defensive action makes the feared world more likely."),

  beat([249, 257], "The Branch Cools", "Functional distinctions remain while the ownership route is removed from the chain.", "reversal", "cool", "cessation", "cooling-chain", "ownership-knot", "Nibbāna changes the process by cooling the mine-and-becoming branch, not by destroying every boundary or response.", {
    caption: "appearance → feeling → clear response",
  }),
  beat([258, 263], "Feeling Without Appropriation", "Pain and pleasure continue without recruiting an identity around repetition or prevention.", "mechanism", "sequence", "sequence", "cooling-chain", "ownership-knot", "The signal continues to clear response while catastrophic and possessive ownership narratives lose their automatic extension."),
  beat([264, 267], "Regulation Without Metaphysics", "The organism acts, but no independent centre must own every node.", "recognition", "open", "cessation", "cooling-chain", "ownership-knot", "What ceases is the fuel for metaphysical ownership, while embodied regulation remains intact."),

  beat([268, 272], "Shared Ground, First Divergence", "Buddhism refuses a final ground behind processes already dependently designated.", "comparison", "compare", "divergence", "dialectic-bridge", "open-frontier", "The traditions share a critique of the empirical ego but diverge over whether a final reflexive ground should be established."),
  beat([273, 274], "Luminous Reflexivity", "Pratyabhijñā interprets finite appearing as contraction of universal self-apprehension.", "comparison", "compare", "divergence", "open-question", "open-frontier", "The Śaiva position treats the non-objectifiability of awareness as compatible with intrinsically reflexive manifestation."),
  beat([275, 279], "One Practical Consequence", "Song without singer and singing as singer meet at non-ownership.", "synthesis", "coordinate", "convergence", "dialectic-bridge", "open-frontier", "The formal dispute remains open while both views affirm that the local voice is real and not an isolated owner."),
  beat([280, 283], "The Buddhist Warning", "Luminous appearing must not harden into another eternal substance.", "objection", "compare", "divergence", "dialectic-bridge", "open-frontier", "The Buddhist critique protects reflexive presence from being converted into a reified metaphysical object."),
  beat([284, 287], "The Śaiva Reply", "Failure to objectify awareness does not by itself establish unreality.", "open-question", "differentiate", "divergence", "open-question", "open-frontier", "The disagreement remains alive because neither objectification nor its failure settles the status of reflexive presence."),

  beat([288, 293], "An Instrument Learns to Listen", "Non-ownership improves tuning and permits difference without rivalry.", "recognition", "recontextualize", "coordination", "tuning-network", "listening-current", "An awakened local performance remains active while becoming more responsive to other partial performances."),
  beat([294, 297], "Pain Repeats a Room", "Damage and one learned chord can make every difference feel threatening.", "consequence", "sequence", "feedback", "causal-vortex", "ownership-knot", "Rigid suffering can recursively turn diverse environments into confirmations of one defended pattern."),
  beat([298, 302], "Real Suffering, Porous Isolation", "Compassion rejects both denial and absolute separation.", "reversal", "recontextualize", "comparison", "limitation-reversal", "listening-current", "The bodhisattva sees a real painful performance whose isolation is less absolute than it appears."),
  beat([303, 307], "Transparent Local World", "A boundary remains operational, ethical, and non-absolute.", "definition", "frame", "interface", "boundary-gates", "local-interface", "The bodhisattva is a finite world transparent enough to its conditions that other worlds no longer appear fundamentally foreign."),
  beat([308, 309], "No Private Liberation", "Relationally arisen selves cannot be transformed in complete isolation.", "thesis", "reveal", "dependency", "dependency-network", "dependency-field", "Compassion follows from relational constitution rather than from claiming that all beings are one numerical person."),
  beat([310, 318], "Clarity Changes Conditions", "Language, teaching, calm, truth, and community alter what can arise elsewhere.", "synthesis", "propagate", "propagation", "tuning-network", "listening-current", "Liberation propagates through conditions because every attained clarity becomes part of other systems' future support sets."),
  beat([319, 324], "Tuning the Missing Note", "Another instrument can alter the support-set until reorganization becomes possible.", "mechanism", "coordinate", "coordination", "tuning-network", "listening-current", "A teacher does not insert recognition but participates in conditions that let the learner's own system retune."),
  beat([325, 329], "Relationships Open Worlds", "Help changes probability, environment, attention, and interpretation rather than transmitting substance.", "consequence", "propagate", "propagation", "tuning-network", "listening-current", "Every relationship participates in determining which local worlds and responses become possible."),

  beat([330, 335], "Three Computational Levels", "Reproducible pattern, inherited disposition, and living runtime replace the cosmic source file.", "analogy", "sequence", "sequence", "source-compile-runtime", "memory-trace", "The code metaphor becomes useful only when its three levels remain functional and immanent to enactment."),
  beat([336, 340], "The Past as Probability", "Compiled disposition biases noticing, fear, possibility, and likely action.", "mechanism", "translate", "translation", "source-compile-runtime", "memory-trace", "Past conditions survive not as supernatural data but as altered routing probabilities in the present system."),
  beat([341, 348], "Finite Freedom", "Runtime can notice and reorganize some conditions without escaping causality.", "consequence", "transform", "self-modification", "source-compile-runtime", "memory-trace", "A conditioned process gains finite freedom when its outputs can modify some of its future dispositions."),
  beat([349, 354], "The Runtime Error", "A provisional model demands permanence, total control, and authorship of its own causes.", "objection", "enclose", "self-modification", "powered-prison", "ownership-knot", "The basic error is granting runtime configuration the privileges of an unchanging source for the whole process."),
  beat([355, 357], "Correct the Privilege", "Recognition keeps the runtime while changing which claims it is allowed to make.", "recognition", "recontextualize", "self-modification", "source-compile-runtime", "ownership-knot", "The living process is not deleted; its self-model loses the impossible status of independent author."),

  beat([358, 368], "Begin With One Appearance", "Sound, pressure, or word opens into body, environment, attention, memory, and contrast.", "practice", "select", "selection", "attention-beam", "local-interface", "Direct inquiry starts from a present distinction and reveals the many conditions required for it to appear this way."),
  beat([369, 373], "Inquiry Has Conditions", "Language, concepts, reading, body, and history place the knower inside the field.", "recognition", "recurse", "recursion", "recursive-observer", "dependency-field", "The act of investigation is itself dependently arisen and cannot stand outside the conditions it reveals."),
  beat([374, 380], "Notice the Observer-Model", "Location, inner voice, tension, and watcher become appearances rather than a second witness.", "practice", "recurse", "recursion", "recursive-observer", "ownership-knot", "The felt knower can be observed as the system's own representation without inventing another watcher behind it."),
  beat([381, 387], "Threat Reveals Ownership", "Tension, narrowed attention, recruited memory, and catastrophe expose the shift from observer to owner.", "practice", "recurse", "inquiry", "recursive-observer", "ownership-knot", "The ownership stance becomes visible through the conditioned cascade that follows when the self-model feels threatened."),
  beat([388, 394], "Reveal the Support Set", "Earlier wound, exhaustion, expectation, sensation, future, and habit loosen false necessity.", "practice", "unfold", "inquiry", "practice-folds", "memory-trace", "A response becomes more workable when inquiry unfolds its conditions instead of suppressing or absolutizing it."),
  beat([395, 397], "Practical Recognition", "Conditions become visible and an assembled response loses the force of inevitability.", "recognition", "open", "transformation", "opening-fist", "ownership-knot", "Recognition begins as the loosening of false necessity rather than as a cosmic flash."),

  beat([398, 404], "Neither Blankness Nor Grandeur", "Recognition is transparency of enactment, not an extraordinary identity claim.", "definition", "differentiate", "differentiation", "textures-display", "ownership-knot", "Recognition must be distinguished from permanent blankness, cosmic authorship, and a magnified version of the same brittle ego."),
  beat([405, 406], "Real Without Absolute", "Body, identity, boundary, perspective, suffering, and action each keep reality while losing independence.", "thesis", "reveal", "comparison", "limitation-reversal", "local-interface", "Recognition holds paired truths together: each finite structure is real, conditioned, changeable, and incomplete."),
  beat([407, 410], "The Observer Becomes Lighter", "Memory informs, identity changes, uncertainty is tolerated, and action continues.", "consequence", "transform", "transformation", "morphing-invariant", "ownership-knot", "Embodied recognition changes the system's responses while preserving a functional observer and meaningful action."),

  beat([411, 418], "Why Anything Appears", "Formal models explain function without yet explaining presence from within.", "open-question", "reveal", "inquiry", "open-question", "open-frontier", "Science can model boundary, regulation, memory, action, and observer emergence while the fact of experience remains open."),
  beat([419, 424], "Three Non-Final Answers", "Madhyamaka, Pratyabhijñā, and illusionism protect different explanatory risks.", "comparison", "compare", "divergence", "dialectic-bridge", "open-frontier", "Three interpretations diverge over foundation, reflexive appearing, and introspective representation without closing the question."),
  beat([425, 430], "Make the Question Inhabitable", "Myth may open possibility only while remembering that it is not proof.", "coda", "open", "inquiry", "open-question", "open-frontier", "The disciplined function of myth is to sustain an open question without disguising premature closure as knowledge."),

  beat([431, 439], "A Pattern Survives a Year", "Child, adolescent, adult, body, world, and reconstructed memory all change.", "analogy", "compare", "identity-across-change", "morphing-invariant", "relational-song", "A birthday celebrates continuity achieved through transformation rather than an immortal object hidden behind it."),
  beat([440, 448], "Messages Move Both Ways", "The present receives earlier traces and becomes a sender to later selves.", "consequence", "sequence", "translation", "memory-relay", "memory-trace", "Temporal identity is a relay in which changing selves inherit, interpret, and transmit constraints."),
  beat([449, 454], "This Performance Is Irreplaceable", "Dependence removes ownership without making the local life unreal or disposable.", "recognition", "open", "dependency", "dependency-network", "local-interface", "This life neither owns the music nor stands apart from its conditions, yet its exact performance could occur nowhere else."),
  beat([455, 460], "Listening While Playing", "A living relation and finite world open beyond isolated possession.", "coda", "open", "cessation", "opening-fist", "ownership-knot", "The final birthday gesture releases the ownership knot so a bounded performance can listen while it continues."),

  beat([461, 468], "No Centre Owns the Network", "Memory, identity, observer, and action arise collaboratively inside changing conditions.", "synthesis", "coordinate", "dependency", "dependency-network", "dependency-field", "Recognition sees the relational network without installing an independent owner at its centre."),
  beat([469, 473], "Compassion Enters the Music", "Partial instruments help one another hear and change without becoming identical.", "synthesis", "propagate", "coordination", "tuning-network", "listening-current", "Compassion is recognition propagated across genuinely different perspectives through deliberate dependent origination."),
  beat([474, 477], "Listening Is in the Song", "Singing and listening close the film as mutually arising parts of one performance.", "coda", "recontextualize", "identity-across-change", "pattern-ensemble", "relational-song", "There is no final singer outside the performance; the closing invariant is relation becoming able to recognize its own participation."),
];

const program = buildDeterministicProgram({
  shotPrefix: "song",
  program: {
    id: "song-no-singer",
    title: "The Song With No Singer",
    sourceEssay: "../essays/the-song-with-no-singer.md",
    visualThesis: "A recurring gold interval-pattern passes through indigo interfaces, distributed networks, changing memory traces, and crimson ownership loops. The film never depicts an isolated soul, cosmic singer, or hidden source object. Every shot must perform a relation—dependence, selection, feedback, translation, transformation, divergence, or coordination—and the final return to the ensemble must preserve difference while revealing music as what happens between local performances.",
    theme: "ivoryManuscript",
    seed: 734901,
    timing: {
      wordsPerMinute: 155,
      tailPadding: 0.45,
    },
    render: {
      width: 1280,
      height: 720,
      fps: 24,
      crf: 20,
      preset: "medium",
      transitionDuration: 0.65,
    },
    continuitySystems,
    captionPolicy: "Narration carries the essay. On-screen text is limited to a beat title, one interpretive subtitle, one technical term, and Devanāgarī. Diagrams supplied in fenced code are visual source and are never spoken.",
  },
}, beats);

const output = resolve(ROOT, "programs/song-no-singer-visual-program.json");
await mkdir(dirname(output), { recursive: true });
await writeFile(output, `${JSON.stringify(program, null, 2)}\n`);
console.log(output);
