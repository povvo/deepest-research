# references/research-architectures.md

> **Runtime use condition:** Read when planning multi-agent research orchestration, knowledge-graph pathfinding, iterative proposal refinement, or research-intelligence architecture.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.



## Contents

1. Section 1: MOOSE & DAgent Planner Core
2. Section 2: Knowledge Extraction & SciAgents Graph Reasoning
3. Section 3: Nova & CycleResearcher Refinement Loops
4. Section 4: Scideator & Novelty Checkers
5. Section 5: Curie & Experimental Rigor Engines

This technical reference provides the engineering specifications, mathematical derivations, and multi-agent architectural models extracted from state-of-the-art literature to support the **Deep Research Planner**.

---

## Section 1: MOOSE & DAgent Planner Core
To systematically automate the open-domain hypothetical induction task, the system combines the **MOOSE** framework with the dynamic planning capabilities of **DAgent** [11, 14, 466].

### 1.1 MOOSE Architectural Components
MOOSE (Multi-mOdule framewOrk with paSt present future feEdback) operates as an iterative pipeline designed to establish valid knowledge connections [14, 15]:
1. **Background Finder**: Reads raw web corpora to identify pressing, societally-grounded research backgrounds $b$ [15, 16].
2. **Inspiration Title Finder**: Screens the titles of the literature corpus to narrow down the search space for potential inspirations, preventing combinatorial search explosion [16].
3. **Inspiration Finder**: Identifies specific inspirational sentences $i$ within target documents [16].
4. **Hypothesis Proposer**: Combines the research background and inspirations to formulate a core hypothesis $h$:
   $$h = f(b, i_1, \dots, i_k)$$ [15, 321]
5. **Reality Checker**: Evaluates whether the proposed hypothesis reflects real-world constraints and physical laws [15, 17].
6. **Novelty Checker**: Validates that the hypothesis is not already represented in the literature [15, 17].

### 1.2 DAgent Dynamic Planner and Memory
For database-driven discovery, **DAgent** provides a three-module core (Planning, Tools, Memory) that manages problem complexity [466, 467]:
- **Planning Module**: Analyzes the input query $Q$ and dynamically determines if decomposition is required based on multi-step reasoning needs [469]. If required, it calls the problem decomposition tools to generate independent sub-questions $\{q_i\}$ [469, 475].
- **Memory Module**: Maintains three distinct logs [466, 477]:
  1. *Intermediate Generation*: Temporarily stores results from intermediate steps (e.g., query outputs, sub-questions) [477].
  2. *Historical Planning Paths*: Records successful execution paths to speed up strategy formulation for similar queries [477].
  3. *Contextual Schema*: Enriches the generator's prompt with SQL schema structures and history [473].

---

## Section 2: Knowledge Extraction & SciAgents Graph Reasoning
**SciAgents** harnesses large-scale ontological knowledge graphs to discover hidden interdisciplinary connections [191]. By navigating paths between seemingly unrelated concepts, the system simulates a "swarm of intelligence" [191].

### 2.1 Heuristic Pathfinding with Randomization
To sample paths between source and target nodes (e.g., a biological concept like "silk" and an engineering concept like "energy-intensive"), SciAgents implements a randomized heuristic search on a global graph $G$ [223, 240]:
1. **Initialize**: Priority queue $Q = [(0, \text{source})]$, visited set $V = \emptyset$.
2. **Retrieve Embeddings**: Use tokenizers and models to find closest-fitting nodes [223].
3. **Estimate Heuristic**: Calculate embedding cosine distance $h(v, \text{target})$ between current and target nodes [223].
4. **Randomized Dijkstra**:
   - Pop node $u$ with lowest cost.
   - If $u = \text{target}$, return path $P$.
   - For each neighbor $v$ of $u$, calculate cost:
     $$\text{cost}(v) = h(v, \text{target}) + \alpha \times \text{random}()$$
     where $\alpha$ represents the randomness factor [223].
5. **Inject Waypoints**: Randomly select $k$ waypoints from neighbors to enforce diverse, unbiased ideation pathways [223, 234].

### 2.2 Ontological Concept Expansion
The sampled path forms a subgraph $G'$ [223]. The **Ontologist** agent defines each term and discusses their structural relationships to provide a rich context for hypothesis generation [212, 236]:
- *Definitions*: Structured natural language descriptions of each concept node [236].
- *Relationships*: Detailed discussions of the linking edges (the "isA" or functional connections), ensuring that every concept in the sampled path is integrated [236, 538].

---

## Section 3: Nova & CycleResearcher Refinement Loops
Once an initial hypothesis is drafted, it must undergo continuous, iterative refinement to enhance its quality, feasibility, and depth [334, 381].

### 3.1 Nova Planning-Driven Search
The **Nova** pipeline introduces iterative planning to retrieve targeted external knowledge [331, 334]:
1. **Initial Seed Generation**: Generates 10 initial ideas from seed papers and guides the LLM using 10 scientific discovery methods (e.g., Kuhn's paradigm anomalies, Popper's falsificationism) [335, 336, 349].
2. **Iterative Planning**: Devisees a search plan targeting specific knowledge gaps [331, 336].
3. **Targeted Retrieval**: Queries databases for recent publications and filters down to the top-5 [188, 341].
4. **Refined Idea Compilation**: Synthesizes the initial ideas with retrieved knowledge, using self-reflection to select the top-3 [336].

### 3.2 CycleResearcher / CycleReviewer Preference Alignment
Inspired by peer review, this framework post-trains open-source LLMs through reinforcement learning using simulated peer review feedback [370, 372]:
- **CycleResearcher (Policy Model)**: Autonomously reads bibliographies, prepares LaTeX drafts, outlines motivations, and details experimental designs [381, 382].
- **CycleReviewer (Reward Model)**: Simulates a multi-reviewer discussion panel, evaluating the draft across Soundness, Presentation, and Contribution to output an average score $r_i$ [376, 381, 384].
- **Iterative SimPO**: Uses preference pairs to continuously optimize the researcher policy, keeping the agent aligned with evolving scientific standards:
  $$\mathcal{D}_t = \{(x, y_w, y_l)\}$$ [384]

---

## Section 4: Scideator & Novelty Checkers
To verify whether a generated research idea is truly novel, the planner implements the four-step **Scideator** retrieve-then-rerank pipeline [186, 291].

```
  ┌──────────────────────────────────────────────────────────┐
  │     STEP 1: Retrieve Candidate Relevant Papers           │
  │     - Gather papers used in idea generation              │
  │     - Run keyword-based Semantic Scholar search          │
  │     - Execute snippet-text search over full idea text    │
  └────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
  ┌──────────────────────────────────────────────────────────┐
  │     STEP 2: Select Most Relevant Papers (Reranking)       │
  │     - Stage 1: Filter to Top-100 via SPECTER embeddings  │
  │     - Stage 2: RankGPT multi-facet re-ranking            │
  └────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
  ┌──────────────────────────────────────────────────────────┐
  │     STEP 3: Evaluate Idea Novelty                        │
  │     - Compare input idea facets with Top-10 papers       │
  │     - Classify: [Novel] / [Not Novel] with reasoning     │
  └────────────────────────────┬─────────────────────────────┘
                               │ (If Classified Not Novel)
                               ▼
  ┌──────────────────────────────────────────────────────────┐
  │     STEP 4: Suggest More Novel Ideas                     │
  │     - Systematically replace one facet (e.g. Mechanism)  │
  │     - Output 3 updated, literature-grounded options      │
  └──────────────────────────────────────────────────────────┘
```

---

## Section 5: Curie & Experimental Rigor Engines
Automated research agents often struggle to maintain experimental rigor [432]. **Curie** addresses this by placing an **Experimental Rigor Engine** between planning and execution agents [434, 440].

### 5.1 The Experimental Rigor Engine
1. **Intra-Agent Rigor Module (Intra-ARM)**: Enforces validation policies within individual agents [434]:
   - *Setup Validation*: Confirms that variables are correctly identified, control conditions are isolated, and hardware environments are controlled [437, 440].
   - *Fidelity Safeguards*: Blocks hallucinated data or mock outputs, ensuring that all findings rest on compiled and executed results [434, 437].
2. **Inter-Agent Rigor Module (Inter-ARM)**:
   - *Plan Partitioning*: Breaks complex high-level plans into independent variable execution slices to support scaling and parallelization [440, 443].
   - *Adaptive Scheduling*: Schedules and prioritizes execution partitions based on the Architect's real-time decisions [444].
3. **Experiment Knowledge Module**: Maintains a DAG-like progression history ("Time Machine") recording every configuration shift and decision rationale to preserve complete traceability [445].
