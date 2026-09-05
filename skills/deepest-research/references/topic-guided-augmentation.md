# Operational Reference: Topic-Guided Augmentation (TGA)

> **Runtime use condition:** Read when divergent, interdisciplinary question generation or topic-guided hypothesis expansion is requested.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## 1. Executive Summary & Purpose
**Topic-Guided Augmentation (TGA)** is a generative ideation methodology designed to drive divergent, out-of-distribution scientific question generation and multi-disciplinary hypothesis discovery [355, 364, 435]. Standard retrieval systems retrieve highly similar papers based on immediate keyword matching, leading to highly redundant and incremental research ideas [363, 364]. TGA, conversely, implements a hierarchical topic-extraction pipeline, builds low-similarity topic pools, and utilizes single-keyword "Utility Test" prompts to force models to produce connections and concepts primarily from their internal knowledge representations rather than replicating input texts [355, 435].

---

## 2. Computational Workflow
TGA operates through an iterative expansion and search planning cycle [355, 364, 365]:

```
  ┌────────────────────────────────────────────────────────────┐
  │                 1. TOPIC POOL COLLECTION                  │
  │ - Extract raw topics from scientific abstracts            │
  │ - Deconstruct and clean topics utilizing LLM prompts      │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 2. SIMILARITY FILTERING                    │
  │ - Calculate pairwise ROUGE-L similarity scores             │
  │ - Exclude topics exceeding strict threshold η             │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │              3. DIVERGENT PRODUCING GENERATION             │
  │ - Prompt with single minimal keywords (e.g. "Graphene")   │
  │ - Force internally-driven creative ideation               │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │               4. SEARCH PLANNING & REFINEMENT              │
  │ - Formulate iterative search plans to close gaps          │
  │ - Replace seed pool with novel retrieved directions       │
  └────────────────────────────────────────────────────────────┘
```

### Step 1: Topic Pool Collection
Topics are extracted sentence-by-sentence from raw scientific corpora [355, 466]. The system prompts the LLM to separate core themes from unnecessary experimental or platform-specific details, resulting in concise, highly abstract topic descriptions [355, 558].

### Step 2: ROUGE-L Similarity Gating
To prevent topic duplication and clustering redundancies, TGA computes pairwise ROUGE-L similarity scores between all extracted topics [355]:
- If the ROUGE-L score between a candidate topic and the active topic pool exceeds threshold $\eta$ (typically $\eta = 0.3$), the candidate is discarded [355].

### Step 3: Divergent Producing Generation (LiveIdeaBench Paradigm)
Unlike convergent thinking tasks which provide rich context (abstracts, full texts), TGA deliberately prompts the model using a **single-keyword stimulus** [435]:
- **Minimal Context**: Single word (e.g., "Mylar", "Bio-inspired") [435, 437].
- **Constraint**: The final idea must be concisely expressed within a strict word count (e.g., 100 words) [437]. This forces the model to generate connections from its internal weights [435].

### Step 4: Iterative Search Planning (Nova style)
Upon establishing the divergent seed ideas, the model devises a goal-oriented **Search Plan** identifying key fields for knowledge acquisition, querying databases for recent publications, and compiling the findings to iteratively boost the seed ideas [331, 336, 364, 369].

---

## 3. Production-Ready Prompt Templates [355, 437, 558]

### Template A: Topic Extraction & Cleaning Prompt [558]
```markdown
[System Message]
You are an expert in academic writing and text analysis. Your task is to evaluate whether a given topic statement is concise, specific, and focused on the core theme. You must remove unnecessary experimental, platform-specific, or procedural details, leaving just the essential scientific theme.

[User Message]
Original Topic: {raw_extracted_text}
Motivation Context: {context_motivation}

Format your output as a JSON object with the following keys:
{
  "original_topic": "The raw topic statement provided.",
  "contains_unnecessary_details": [true / false],
  "revised_topic": "If unnecessary details are found, provide a revised, highly abstracted version of the topic statement in the format: 'The topic of this paper is [revised topic]'. If already concise, set to null."
}
```

### Template B: Divergent Single-Keyword Stimulus (LiveIdeaBench Paradigm) [437]
```markdown
[System Message]
You are a Creative Scientific Explorer. Your goal is to propose an original, technically feasible, and highly creative scientific idea related to the assigned keyword.
Rules:
1. Ground your suggestion in physical laws and logical reasoning.
2. The entire response (including background) MUST be under 100 words.
3. Prioritize divergent, interdisciplinary connections.

[User Message]
Your assigned keyword is: "{{keywords}}"

Please respond with your creative scientific idea.
```
