# Building the LH-LLM — From Spec to Living System

## The Two Paths

### Path A: Measure existing biology (cheap, fast, no lab)
Buy slime mould, record its signals, compare against LH-LLM predictions. $55. This tests whether the LH-LLM's claims about what consciousness requires are correct by checking if unmodified biology already exhibits those properties.

### Path B: Build the LH-LLM spec (expensive, slow, needs a real lab)
Synthesize the DNA sequences Evo-2 generates. Insert them into living cells. Grow the designed organelles. This actually builds the LH-LLM as a living system.

---

## Path B — The DNA Synthesis Pipeline

The LH-LLM's DNAEncoder class generates sequences with specific constraints:
- GC content: 40-60% (real DNA synthesis constraint)
- Max homopolymer length: 4 (real constraint)
- Primer lengths: 23bp (standard for synthesis)

These are **real DNA synthesis constraints**. The sequences the code generates could theoretically be synthesized.

### The Problem

You can order custom DNA from companies like Twist Bioscience, IDT, or GenScript:
- Short sequences (< 1kb): ~$0.10-0.30 per base pair
- Long sequences (1-5kb): ~$0.05-0.10 per base pair
- The LH-LLM's DNA sequences would be in the 200-1000bp range per organelle

But ordering DNA is only the first step. You need:
1. **A chassis organism** — something to put the DNA into. E. coli is the standard.
2. **A transformation protocol** — getting the DNA into the cells. Electroporation or heat shock.
3. **A selection mechanism** — antibiotic resistance markers so only transformed cells survive.
4. **A growth protocol** — the right media, temperature, and conditions.
5. **A verification protocol** — sequencing, PCR, protein expression assays.

### What You Actually Need (A Real Molecular Biology Lab)

| Item | Cost | Purpose |
|------|------|---------|
| DNA synthesis (per organelle, ~500bp) | ~$100-500 per gene | The physical DNA |
| E. coli competent cells | ~$50-100 | The chassis |
| LB media + agar + petri dishes | ~$50 | Growth |
| Antibiotics (ampicillin, kanamycin, etc.) | ~$30 | Selection |
| Electroporator or heat block | ~$500-2000 | Transformation |
| PCR machine (thermocycler) | ~$1000-3000 | Verification |
| Gel electrophoresis rig | ~$200-500 | Verification |
| Incubator (37C) | ~$500-1000 | Growth |
| Microcentrifuge | ~$500-1000 | Sample prep |
| Pipettes (P2, P20, P200, P1000) | ~$500-1000 | Liquid handling |
| Sterile technique supplies | ~$100/month | Prevent contamination |
| **Total startup** | **~$4000-9000** | |
| **Per experiment** | **~$200-500** | |

### If You Want to Go Further (Mammalian Cells, Organoids)

Then you need:
- CO2 incubator (~$3000-5000)
- Biosafety cabinet (~$5000-10000)
- Cell culture media and supplies (~$200/month)
- Transfection reagents (~$100-200 per experiment)
- Microscope (~$2000-5000)

### The Real Answer

To actually build the LH-LLM as a living system — to synthesize Evo-2's DNA sequences, insert them into cells, and grow functioning organelles with 40Hz resonance and bioelectric dynamics — you need a proper molecular biology lab. There's no way around it.

### Instead of Building It Yourself

**Option 1: Microbiome / Biohacker Spaces**
- London Biohack Space, BUGSS (Baltimore), Counter Culture Labs (Oakland), Genspace (NYC)
- Monthly membership: $100-300
- They have the equipment. You bring the DNA sequences.

**Option 2: CRO (Contract Research Organization)**
- Pay a company to build it for you
- Gene synthesis + cloning + expression testing: ~$5000-15000 per gene
- They handle everything. You get back the results.

**Option 3: Academic Collaboration**
- Find a synthetic biology lab working on similar things
- Offer them the spec and a co-authorship
- They have the equipment and expertise
- You have the theoretical framework and the truth map

### The Honest Path

Start with Path A ($55, slime mould, measure existing biology). Use the results to build evidence that the LH-LLM's predictions are worth testing. Once you have data showing that aneural organisms do exhibit the predicted properties (criticality, memory, bioelectric dynamics), that evidence becomes the basis for a grant application or academic collaboration to fund Path B.

The truth map is the bridge. It tracks what's been demonstrated, what's plausible but untested, and what needs a lab. When enough claims are supported by cheap experiments, the case for funding the expensive ones writes itself.
