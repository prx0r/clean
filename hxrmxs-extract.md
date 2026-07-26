# HXRMXS — Reusable Code, Patterns & Features

Extracted from the hxrmxs repository. Organised by what maps to our stack.

---

## 1. Research Arm — Shadow Model + ThinkTank

**Source:** `research arm.txt`

### Core Pattern

```
Shadow Model (unsupervised clustering) → finds novel patterns in data
  → ClusterAnalysis object passed to BORIS Orchestrator
    → ThinkTank crew (Analyst, Namer, Definer, Critic)
      → Debate and refine
        → Research Report published to "Research Tab"
          → Human-in-the-loop validation
```

### Reusable Agent Roles

```
Analyst Agent: Reviews raw data, summarises common themes
Namer Agent: Proposes candidate names based on Analyst summary
Definer Agent: Drafts formal, falsifiable definition
Critic Agent: Argues AGAINST the hypothesis — searches for counter-evidence,
              checks overlap with existing categories, critiques for ambiguity
```

### Reusable Code — ThinkTank Orchestration Pattern

```python
# Pattern: The BORIS Orchestrator that spins up agent crews
class ThinkTankOrchestrator:
    def __init__(self):
        self.agents = {
            'analyst': AnalystAgent(),
            'namer': NamerAgent(),
            'definer': DefinerAgent(),
            'critic': CriticAgent(),
        }
    
    async def investigate(self, cluster_data: ClusterAnalysis) -> ResearchReport:
        # 1. Analyst reviews raw data
        analysis = await self.agents['analyst'].summarize(cluster_data)
        
        # 2. Namer proposes candidates
        names = await self.agents['namer'].propose(analysis)
        
        # 3. Definer drafts formal definition
        definition = await self.agents['definer'].draft(names[0], analysis)
        
        # 4. Critic attacks the hypothesis
        critique = await self.agents['critic'].challenge(definition)
        
        # 5. Loop until consensus or stable state
        while critique.has_issues:
            definition = await self.agents['definer'].revise(definition, critique)
            critique = await self.agents['critic'].challenge(definition)
        
        # 6. Produce final research report
        return ResearchReport(
            name=names[0],
            definition=definition,
            confidence=self._compute_confidence(critique),
            supporting_evidence=analysis.exemplars,
            counter_arguments=critique.issues,
            validation_proposal=self._propose_validation_question(definition)
        )
```

### Research Report Schema

```json
{
  "name": "Proposed trait name",
  "definition": "Falsifiable scientific definition",
  "confidence": 0.85,
  "supporting_evidence": ["exemplar responses"],
  "counter_arguments": ["issues raised by Critic"],
  "validation_proposal": "New question to validate this trait"
}
```

### Human-in-the-Loop Research Portal

```
"Research Tab" features:
  - Naming Committees: users vote on best name
  - Definition Refinement: users rate if definition matches exemplar feeling
  - Participate in Studies: opt-in validation questions deployed to users
  - AI discovers pattern → human community validates → pattern confirmed or rejected
```

**Map to our stack:** The ThinkTank replaces the hypothesis engine. The Critic agent is the falsifier checker. The Research Tab is the Satsang reputation system (users earn Q-score by voting on definitions, names, classifications).

---

## 2. Magnum Opus v5 — Ouroboros Three-Loop Architecture

**Source:** `v5 bb.txt`

### The Three Loops

```
┌─────────────────────────────────────────────────┐
│              LIVE LOOP (Daytime)               │
│  User → Teacher + Librarian → Response         │
│  Real-time interaction                         │
└──────────────────────┬──────────────────────────┘
                       │ feeds session logs
                       ▼
┌─────────────────────────────────────────────────┐
│           STRATEGIC LOOP (The Charioteer)       │
│  Reads history → selects best Truthcore         │
│  + best Pedagogy for current student state      │
│  Injects [STRATEGY] instruction before Teacher  │
└──────────────────────┬──────────────────────────┘
                       │ feeds consolidated data
                       ▼
┌─────────────────────────────────────────────────┐
│            DREAMING LOOP (Nighttime)            │
│  Consolidator: promotes useful temp Truthcores  │
│  Gap Analyst: finds missing knowledge           │
│  Critic: re-evaluates past pedagogy blocks      │
│  Generates research missions for next day       │
└─────────────────────────────────────────────────┘
```

### Reusable Code — The Charioteer (Strategy Injector)

```python
class Charioteer:
    """
    Real-time steering based on student state history.
    Before the Teacher speaks, injects a [STRATEGY] instruction.
    """
    def __init__(self):
        self.policy_graph = PolicyGraph()  # state + topic → best truthcore + best pedagogy
    
    def get_strategy(self, student_state: str, topic: str) -> dict:
        """Query the policy graph for the best approach."""
        best = self.policy_graph.query(student_state, topic)
        return {
            "strategy_id": best.id,
            "instruction": f"User rejected scientific metaphor. Force metaphysical interpretation of this truthcore.",
            "pedagogical_angle": best.angle,
            "recommended_truthcore": best.truthcore_id,
        }

class PolicyGraph:
    """
    Maps {Student State + Topic} → {Best Truthcore + Best Pedagogy}.
    Trained from interaction outcomes.
    """
    def __init__(self):
        self.edges = {}  # (state, topic) → (truthcore_id, pedagogy_id, success_count)
    
    def query(self, state: str, topic: str) -> Edge:
        return self.edges.get((state, topic), self._fallback())
    
    def update(self, state: str, topic: str, truthcore_id: str, pedagogy_id: str, success: bool):
        key = (state, topic)
        if key not in self.edges:
            self.edges[key] = Edge(truthcore_id, pedagogy_id, 0, 0)
        self.edges[key].successes += 1 if success else 0
        self.edges[key].attempts += 1
```

### Reusable Code — The Dreamer (Nightly Consolidation)

```python
class Dreamer:
    """
    Grows the system while it sleeps.
    Consolidates temporary knowledge, finds gaps, re-evaluates past performance.
    """
    def __init__(self):
        self.consolidator = Consolidator()
        self.gap_analyst = GapAnalyst()
        self.critic = Critic()
    
    async def dream(self, session_logs: List[SessionLog]):
        # 1. Consolidate temporary truthcores
        promoted = await self.consolidator.promote_useful(session_logs)
        
        # 2. Find knowledge gaps
        research_missions = await self.gap_analyst.find_gaps(session_logs)
        
        # 3. Re-evaluate past pedagogy
        corrections = await self.critic.review_past_performance(session_logs)
        
        return {
            "promoted_truthcores": promoted,
            "research_missions": research_missions,
            "pedagogy_corrections": corrections,
        }

class Consolidator:
    async def promote_useful(self, logs):
        """Temporary truthcores with high engagement → permanent."""
        promoted = []
        for log in logs:
            for tc in log.temporary_truthcores:
                if tc.engagement_score > 0.7 and tc.usage_count > 3:
                    tc.status = 'permanent'
                    promoted.append(tc)
        return promoted

class GapAnalyst:
    async def find_gaps(self, logs):
        """Identify topics users asked about that had no good truthcores."""
        gaps = []
        for log in logs:
            for turn in log.turns:
                if turn.impact_score < 0.3 and not turn.truthcore_found:
                    gaps.append({
                        "topic": turn.topic,
                        "user_intent": turn.user_intent,
                        "urgency": self._compute_urgency(turn),
                    })
        return gaps
```

### Truthcore v5 Schema

```json
{
  "id": "tc_entropy_01",
  "domain": ["physics", "metaphysics"],
  "invariant": "Entropy in an isolated system always increases.",
  "mechanisms": [
    {
      "name": "Probability Constraint",
      "desc": "Disorder is more probable than order; structure requires energy input."
    }
  ],
  "pedagogical_hooks": [
    {"target_state": "nihilism", "angle": "Decay is not failure, it is gravity."},
    {"target_state": "control_freak", "angle": "You cannot defeat probability, only surf it."}
  ],
  "source_quality": 0.95,
  "usage_stats": {"successes": 15, "failures": 2}
}
```

### Session Log Schema (What the Dreamer Eats)

```json
{
  "session_id": "sess_001",
  "turns": [
    {
      "user_input": "I feel like I'm falling apart.",
      "student_state_detected": "nihilistic_collapse",
      "librarian_action": {"type": "retrieve", "truthcore_id": "tc_entropy_01"},
      "teacher_output": "...",
      "outcome": {
        "user_reaction": "Wow, I never thought of it that way.",
        "impact_score": 0.9
      }
    }
  ]
}
```

**Map to our stack:** The Ouroboros architecture maps to our factory system:
- Live Loop = our content production pipeline (EO → essay → video)
- Strategic Loop = the Charioteer selecting which content to show based on user state (feed algorithm)
- Dreaming Loop = nightly consolidation of truth map, promoting evidence, retiring stale questions, generating new research missions
- Truthcore = truth map question with pedagogical hooks for different user states
- Session logs = Satsang user interaction data feeding the geometric engine training

---

## 3. Endgame — VR Proxy Mapping

**Source:** `endgame.txt`

### Core Principle

Every web interaction is a cheap VR prototype. Design the web version with VR in mind — every interaction maps directly.

### Input Mapping Table

| Web Interaction | VR Equivalent | What It Measures |
|----------------|---------------|-----------------|
| `mouseMovement` | `handTracking` | Hesitation patterns (identical) |
| `mouseHover` | `gazeTarget` | What you examine before choosing |
| `clickDecision` | `handPointing` | Final choice selection |
| `keyboardInput` (WASD) | `spatialMovement` | Walking toward/away |
| `scrollBehavior` | `approachDistance` | Zoom in/out → step closer/back |
| `typingPauses` | `verbalHesitation` | Speech pattern analysis |
| `pageRefocus` | `headTurning` | Attention redirection |

### Reusable Code — VR-Ready Scenario Design

```javascript
// Every web scenario includes its VR translation spec
const behaviorMapping = {
  mouseMovement: 'handTracking',
  mouseHover: 'gazeTarget',
  clickDecision: 'handPointing',
  keyboardInput: 'spatialMovement',
  scrollBehavior: 'approachDistance',
  typingPauses: 'verbalHesitation',
  pageRefocus: 'headTurning'
};

class VRReadyScenario {
  constructor(webScenario) {
    this.webVersion = webScenario;
    this.vrBlueprint = {
      environmentType: webScenario.backgroundSetting,
      interactionMethod: this.mapInputToVR(webScenario.inputs),
      trackingMetrics: this.mapMouseToSpatial(webScenario.tracking),
      psychologicalTarget: webScenario.traitMeasurement
    };
  }

  mapInputToVR(inputs) {
    return inputs.map(i => ({
      web: i.type,
      vr: behaviorMapping[i.type] || 'unknown',
      measures: i.measures
    }));
  }

  validateTranslationReadiness() {
    // Can this scenario work in VR? Check all interactions have VR mappings
    return this.webVersion.inputs.every(i => behaviorMapping[i.type]);
  }
}

// Example: 2D web scenario designed for VR from day one
const scenario = new VRReadyScenario({
  backgroundSetting: "party_room",
  inputs: [
    { type: 'mouseMovement', measures: ['hesitation', 'speed'] },
    { type: 'clickDecision', measures: ['choice', 'reaction_time'] }
  ],
  tracking: ['mouse_path_to_decision', 'hover_time_on_each_option'],
  traitMeasurement: 'social_anxiety'
});
```

**Map to our stack:** Design the Satsang.web interface with VR tradition worlds in mind. Every clickable element, every scroll, every hover should have a known VR equivalent. The web version validates the interaction before the 3D build.

---

## 4. The Monolith — Paper to Visual Narrative Pipeline

**Source:** `monolith2.txt`

### 14-Phase Pipeline

```
INPUT: Scientific paper (PDF/text) + Creative direction
  → Phase 0: Creative consultation (human-AI ideation)
  → Phase 1-14: Algorithmic synthesis
OUTPUT: 45-second looping cinematic visualization with:
  - Canvas-based animation
  - Tone.js ambient audio landscape
  - Synchronized subtitle progression
  - Mathematical equation evolution
  - Seamless loop structure
```

### Core Architecture

```python
class MonolithPipeline:
    """
    14-phase pipeline from scientific paper to visual narrative.
    Every output must be visually unique while maintaining structural coherence.
    """
    
    def __init__(self):
        self.phases = [
            self.creative_consultation,
            self.extract_narrative_arc,
            self.design_visual_vocabulary,
            self.compose_audio_landscape,
            self.sync_subtitle_progression,
            self.evolve_mathematical_equations,
            self.build_canvas_animation,
            self.ensure_loop_seamlessness,
            self.cross_modal_synchronization,
            self.quality_control,
            self.render_preview,
            self.human_review,
            self.final_render,
            self.deploy
        ]
    
    async def run(self, paper_text: str, creative_direction: dict) -> str:
        """Execute the 14-phase pipeline."""
        result = paper_text
        for phase in self.phases:
            result = await phase(result, creative_direction)
        return result  # HTML file with embedded canvas + audio + subtitles
```

### 5-Act Dramatic Structure (Compressed to 45s)

```
Act 1 (0-8s):  Setup — present the puzzle
Act 2 (8-18s): Complication — introduce the tension
Act 3 (18-27s): Crisis — the peak, the equation, the reveal
Act 4 (27-36s): Resolution — the insight lands
Act 5 (36-45s): Return — loop back to the opening, transformed
```

### Visual Vocabulary Types (Beyond Geometric Nodes)

```
1. Particle systems
2. Wave propagation
3. Field visualizations
4. Topological morphing
5. Biomechanical forms
6. Fractal generation
7. Constellation/network graphs
8. Fluid dynamics
9. Light/spectrum gradients
10. Architectural/structural forms
```

**Map to our stack:** This is a template for short-form video content (45-second loops for Instagram/TikTok/Shorts). Each truth map question could have a 45-second Monolith loop as its visual summary. The 5-act structure maps to the rhetorical map stage of the video factory.

---

## 5. The Gold — Triangulated Psychological Event (TPE)

**Source:** `the gold.txt`

### The TPE Data Model

```
TPE = (Psychological Profile, Scenario Specification, Behavioral Signature, Reflective Rationale)

P: Who was the user before the event? (profile, scores, history)
S: What was the precise experiment? (scenario JSON)
A: What did the user actually do? (event stream, attention data)
R: What did the user say about what they did? (justification text)
```

### Reusable Code — Mouse-as-Gaze Event Stream

```python
class GazeEventStream:
    """
    High-frequency stream of semantic events, not raw X/Y coordinates.
    Each event has meaning: what the user looked at, for how long, in what order.
    """
    def __init__(self):
        self.events = []
    
    def record_gaze_enter(self, target_id: str, timestamp: float):
        self.events.append({
            "event": "gaze_enter",
            "target_id": target_id,
            "timestamp": timestamp
        })
    
    def record_gaze_dwell(self, target_id: str, duration_ms: int):
        self.events.append({
            "event": "gaze_dwell",
            "target_id": target_id,
            "duration_ms": duration_ms
        })
    
    def record_gaze_exit(self, target_id: str, timestamp: float):
        self.events.append({
            "event": "gaze_exit",
            "target_id": target_id,
            "timestamp": timestamp
        })

class DecisionMetrics:
    """
    Quantifies hesitation and cognitive load from interaction patterns.
    """
    def __init__(self):
        self.decision_reversal_count = 0
        self.mouse_trajectory_points = []
    
    def record_reversal(self):
        """Incremented when gaze moves toward one choice then another before acting."""
        self.decision_reversal_count += 1
    
    def compute_trajectory_entropy(self) -> float:
        """
        High entropy = chaotic/wandering path = high cognitive load or anxiety.
        Low entropy = direct straight path = confidence.
        """
        if len(self.mouse_trajectory_points) < 3:
            return 0.0
        # Compute path curvature as proxy for entropy
        dx = self.mouse_trajectory_points[-1][0] - self.mouse_trajectory_points[0][0]
        dy = self.mouse_trajectory_points[-1][1] - self.mouse_trajectory_points[0][1]
        direct_distance = (dx**2 + dy**2) ** 0.5
        actual_distance = sum(
            ((self.mouse_trajectory_points[i][0] - self.mouse_trajectory_points[i-1][0])**2 +
             (self.mouse_trajectory_points[i][1] - self.mouse_trajectory_points[i-1][1])**2) ** 0.5
            for i in range(1, len(self.mouse_trajectory_points))
        )
        return actual_distance / max(direct_distance, 0.001) - 1.0  # 0 = straight, >0 = wandering
```

### PerceivedSelfGraph Versioning

```python
class PerceivedSelfGraph:
    """
    The user's personality model (mean vector + covariance matrix) is versioned.
    Snapshot before every scenario deployment.
    """
    def __init__(self):
        self.versions = {}  # scenario_id → BeliefState_T_minus_1
    
    def snapshot_before(self, scenario_id: str, belief_state: dict):
        """Save the user's exact state of mind before the event."""
        self.versions[scenario_id] = {
            "mean_vector": belief_state.get("mean"),
            "covariance_matrix": belief_state.get("covariance"),
            "timestamp": belief_state.get("timestamp"),
            "scenario_id": scenario_id
        }
    
    def get_snapshot(self, scenario_id: str) -> dict:
        return self.versions.get(scenario_id)
```

### Justification-Integration Score

```python
class JustificationScorer:
    """
    Transforms qualitative user justification into quantitative score.
    Measures: how well does the user's explanation match their stated self-image?
              how well does it match their actual behavior?
    """
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
    
    def score(self, perceived_self_concept: str, revealed_self_action: str, justification_text: str) -> dict:
        # Embed all three
        emb_self = self.embedding_model.encode(perceived_self_concept)
        emb_action = self.embedding_model.encode(revealed_self_action)
        emb_just = self.embedding_model.encode(justification_text)
        
        # Compute similarities
        similarity_to_perception = cosine_similarity(emb_just, emb_self)
        similarity_to_action = cosine_similarity(emb_just, emb_action)
        
        return {
            "similarity_to_perceived_self": similarity_to_perception,
            "similarity_to_revealed_action": similarity_to_action,
            "justification_integration_score": (similarity_to_perception + similarity_to_action) / 2
        }
```

**Map to our stack:** The TPE data model is how Satsang user interactions should be stored for feed algorithm training. Every video watch, every question asked, every content interaction becomes a TPE: who the user was (their philosophy page, watch history, birth chart), what they watched (the video/scenario), what they did (watch duration, engagement, skip patterns), and what they said about it (comments, ratings, shares). The geometric engine trains on TPEs to predict what content will resonate.

---

## 6. Consciousness Research Platform — Audio-First Discovery

**Source:** `Consciousness Research Platform A.txt`

### Dual-Mode Architecture

| Mode | Interface | Journey Style | Narration | User Control |
|------|-----------|---------------|-----------|--------------|
| Academic | Clean, professional | Methodical exploration with explicit goals | Professional, measured, technical | Full control over depth |
| Discovery | Immersive, ambient | Serendipitous with surprising connections | Engaging, story-like, dramatic | Guided with choice points |

### Discovery Journey Mechanics

```python
class DiscoveryJourney:
    """
    After each explanation, three glowing pathways appear.
    User chooses one. New pathways reveal based on content explored.
    """
    def __init__(self):
        self.pathways = []
        self.history = []
    
    def present_choices(self, context: str) -> list:
        """Generate three branching paths based on current context."""
        return [
            {"id": "neuroscience_trail", "visual": "brain imagery with neural networks", "label": "The Neuroscience Trail"},
            {"id": "philosophy_path", "visual": "ancient scrolls morphing into modern symbols", "label": "The Philosophy Path"},
            {"id": "ai_frontier", "visual": "digital landscapes with emerging algorithms", "label": "The AI Frontier"},
        ]
    
    def choose_path(self, path_id: str):
        self.history.append(path_id)
        # After 60-90 seconds of content, new pathways reveal based on content explored
        return self._generate_next_pathways(path_id)

class ChoicePresentation:
    """Four ways to present choices to users."""
    @staticmethod
    def pathway_metaphor():
        """Branching roads leading to different intellectual territories."""
        pass
    
    @staticmethod
    def portal_system():
        """Glowing doorways showing glimpses of different research domains."""
        pass
    
    @staticmethod
    def constellation_map():
        """Stars that connect to form new patterns when selected."""
        pass
    
    @staticmethod
    def voice_only():
        """AI describes three directions, user responds naturally."""
        pass
```

### Paper Classification Schema

```json
{
  "paper_id": "...",
  "theoretical_framework": "materialism | panpsychism | dualism | idealism",
  "research_methodology": "empirical | theoretical | computational | philosophical",
  "core_claims": [
    {"claim": "...", "falsifiable": true, "test": "..."}
  ],
  "mathematical_framework": "equations, computational models, quantitative predictions",
  "empirical_evidence": {
    "supporting_studies": [],
    "replication_status": "confirmed | contested | untested"
  },
  "theoretical_relationships": [
    {"with": "other_theory", "type": "builds_on | contradicts | synthesizes"}
  ]
}
```

### Quality Tiers

```
Tier 1 - Premium: Peer-reviewed journals with high impact factors
Tier 2 - Standard: Established journals with peer review
Tier 3 - Experimental: Preprints and working papers (clearly labeled)
Exclusion: Predatory journals, non-peer reviewed work claiming empirical breakthroughs
```

**Map to our stack:** The dual-mode architecture maps to Factory 2 (Academic mode = writing papers) and Factory 3 (Discovery mode = video content). The journey mechanics are the feed algorithm — branching paths instead of ranked lists. The paper classification schema is exactly what the SO (Source Object) metadata should contain.

---

## 7. Translation Layer — Archetype Discovery

**Source:** `translation layer.txt`

### Core Pipeline

```
Text → emotion coordinates → nearest archetype → musical DNA + visual DNA
```

### Reusable Code — Archetype-Based Generation

```python
class ArchetypeTranslationLayer:
    """
    Text → emotion coordinates → nearest archetype → synchronized audio-visual output.
    Eliminates arbitrary mappings by using discovered archetypes.
    """
    def __init__(self):
        self.archetypes = self._load_discovered_archetypes()
        self.emotion_extractor = TextEmotionExtractor()
    
    def generate(self, text_prompt: str) -> AudioVisualOutput:
        # 1. Text → emotion coordinates
        emotion_vector = self.emotion_extractor.extract(text_prompt)
        
        # 2. Emotion → nearest archetype
        archetype = self._find_nearest_archetype(emotion_vector)
        
        # 3. Archetype → audio generation
        audio = self._render_audio(archetype.musical_dna)
        
        # 4. Archetype → visual generation
        visual = self._render_visual(archetype.visual_dna)
        
        # 5. Both share same emotional foundation = automatic sync
        return AudioVisualOutput(audio=audio, visual=visual, sync=True)
    
    def _find_nearest_archetype(self, emotion_vector):
        """Find the closest discovered archetype by cosine similarity."""
        best_match = None
        best_sim = -1
        for archetype in self.archetypes:
            sim = cosine_similarity(emotion_vector, archetype.emotion_centroid)
            if sim > best_sim:
                best_sim = sim
                best_match = archetype
        return best_match
```

### Archetype Schema

```json
{
  "id": "melancholic_archetype",
  "emotion_centroid": [0.2, 0.8, 0.1, 0.3],
  "musical_dna": {
    "chords": ["Am", "F", "C", "G"],
    "tempo": 65,
    "timbre": "soft_attack_low_brightness"
  },
  "visual_dna": {
    "motion": "slow_downward_drift",
    "color": "deep_blue_sparse_warmth",
    "energy": 0.3
  },
  "discovery_method": "clustered_from_10k_examples",
  "cross_cultural_validated": true
}
```

**Map to our stack:** The exemplars in `exemplars/` should be analyzed this way — discover archetypal patterns in pacing, visual metaphor density, narrative arc shape, and audio profile. Then the video factory generates from discovered patterns, not guessed ones.

---

## 9. Ouroboros — Where It Lives in Our Stack

### The Dreaming Loop

Our factories currently have only the Live Loop (reactive: question → produce → publish). Adding the Dreaming Loop means every night:

**Factory 1 (Research) Dreaming:**
- Consolidates temporary ROs (stubs with enough passages get promoted to active)
- Gap analysis: finds truth map questions with no ROs → generates acquisition missions
- Re-evaluates RO quality scores based on how often they were used in EOs/videos
- Prunes stale ROs (last updated > 90 days, zero usage)

**Factory 2 (Writing) Dreaming:**
- Reviews essays that underperformed (low reads, low retention) → identifies structural patterns
- Updates the V7 algorithm based on what actually worked
- Generates research missions: "we have no essay on the intersection of X and Y"

**Factory 3 (Video) Dreaming:**
- Reviews video engagement data → identifies which visual modes drove highest retention
- Prunes GLSL shaders that consistently produce low-engagement scenes
- Recommends new shader motifs based on engagement patterns
- Generates "research missions" for the designer: "we need a scene type that explains comparative philosophy visually"

**Factory 4 (Analytics) Dreaming:**
- This factory already IS the Dreaming Loop for the other three
- Nightly batch: compute performance metrics → update truth map → generate new hypotheses
- The factory doesn't publish content. It publishes *insights* about content performance

### The Critic Agent

Sits at specific choke points where the system would otherwise accept plausible-sounding outputs:

**Gate 1: EO Proposal (Research Factory 1d)**
Before an EO enters production, the Critic tries to falsify its central hypothesis. If the Critic finds a counter-argument the EO doesn't address, the EO goes back for revision. The EO is only "ready for production" when the Critic fails to break it.

```
EO drafted
  → Critic: "Can I find evidence against this hypothesis?"
    → Yes? EO revised → Critic again
    → No (3 rounds) → EO moves to production queue
```

**Gate 2: Quote Budget (Writing Factory 2b)**
The Critic checks every published essay against the source material. Not just quote count — does the essay's claim actually follow from the sources cited? Or is the agent summarizing a source in a way that subtly changes the meaning?

```
Essay draft
  → Critic: "Does the essay's claim X actually follow from the source Y it cites?"
    → No? Flagged for human review
    → Yes? Proceed
```

**Gate 3: Falsifier Check (Truth Map — All Evidence)**
Every evidence entry in the truth map gets a Critic pass. The Critic asks: "Is there another interpretation of this same data?" If yes, that alternative interpretation gets added as evidence_against.

```
New evidence added to truth map
  → Critic: "Can this data be interpreted differently?"
    → Yes? Add alternative interpretation as evidence_against
    → No? Proceed
```

**Gate 4: Video Script (Factory 3a)**
Before a storyboard gets rendered, the Critic reviews the rhetorical map. Does the visual metaphor actually support the argument? Or is it beautiful but misleading?

```
Storyboard draft
  → Critic: "Does this visual metaphor accurately represent the concept?"
    → Misleading? Revise
    → Accurate? Proceed to render
```

### The Charioteer (Real-Time Strategy)

Sits in the feed algorithm and the Satsang user experience. Before showing a user their next piece of content, the Charioteer checks their current state:

```
User just watched a video about emptiness in Madhyamaka
  → Charioteer checks user state:
    → User is a beginner (new to philosophy)?
      → Recommend: "What is Emptiness? A Gentle Introduction"
    → User has engaged with comparative content before?
      → Recommend: "Emptiness in Madhyamaka vs Śūnyatā in Yogācāra"
    → User seems stuck (watched but didn't engage)?
      → Recommend: different format (essay instead of video)
```

The Charioteer doesn't decide what content exists. It decides which existing content is shown to whom, in what state, at what time.

---

## 10. Pattern Summary — What to Actually Build

| Pattern | Source | Priority | Maps To |
|---------|--------|----------|---------|
| ThinkTank (Analyst, Namer, Definer, Critic) | research arm.txt | HIGH | Hypothesis engine + peer review |
| Critic agent (argues against hypothesis) | research arm.txt | HIGH | Falsifier checker in truth map |
| Dreaming Loop (nightly consolidation) | v5 bb.txt | HIGH | Truth map staleness + gap analysis |
| Truthcore pedagogical_hooks | v5 bb.txt | MEDIUM | Truth map question angles for user states |
| VR proxy mapping (web → VR) | endgame.txt | MEDIUM | Satsang tradition worlds design |
| Monolith 14-phase pipeline | monolith2.txt | MEDIUM | Short-form video template |
| TPE data model (P, S, A, R) | the gold.txt | HIGH | Satsang feed algorithm training data |
| Mouse-as-gaze event stream | the gold.txt | LOW | User behavior tracking on Satsang |
| Justification-Integration Score | the gold.txt | LOW | Reputation system refinement |
| Dual-mode architecture (Academic/Discovery) | CRP A.txt | MEDIUM | Factory 2 / Factory 3 split |
| Journey mechanics (branching paths) | CRP A.txt | MEDIUM | Feed algorithm UX |
| Paper classification schema | CRP A.txt | HIGH | SO (Source Object) metadata |
| Archetype discovery from exemplars | translation layer.txt | MEDIUM | Video factory visual/music generation |
| Charioteer (real-time strategy injector) | v5 bb.txt | MEDIUM | Feed algorithm personalization |
| Session log schema | v5 bb.txt | MEDIUM | Interaction logging for geometric engine |
| Research Report with human voting | research arm.txt | MEDIUM | Satsang reputation system |
| PerceivedSelfGraph versioning | the gold.txt | LOW | User profile snapshots for A/B testing |
