# Operational Reference: Reasoning Path Self-Consistency

> **Runtime use condition:** Read when generating independent candidate analyses and consolidating them without treating agreement as truth.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## 1. Executive Summary & Purpose
**Reasoning Path Self-Consistency** is an inference-time optimization and uncertainty quantification methodology designed to eliminate calculation failures, logical drift, and stochastic errors in complex scientific reasoning tasks [280, 281, 412, 455]. Rather than relying on a single, deterministic greedy-decoded reasoning path, self-consistency samples multiple diverse reasoning trajectories (greedy or stochastic) [412, 417, 455]. It then constructs a **"Resonance Graph"** where individual solution attempts are modeled as nodes, and their semantic coherence and mutual support are modeled as undirected weighted edges [280, 281]. The final optimal solution is determined by finding the consensus center or executing weighted marginalization over the graph's high-connectivity paths [281, 545].

---

## 2. Core Operational Workflow
The self-consistency pipeline consists of four major steps [280, 281, 544, 545]:

```
  ┌────────────────────────────────────────────────────────────┐
  │              1. DIVERSE PATH SAMPLING (N > 10)             │
  │ - Use temperature scaling or probabilistic sampling        │
  │ - Generate independent step-by-step reasoning chains       │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │             2. SEMANTIC RESONANCE EVALUATION               │
  │ - Compute SBERT embeddings for each generated path         │
  │ - Perform pairwise cross-evaluation of path consistency     │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │               3. RESONANCE GRAPH ASSEMBLY                  │
  │ - Nodes = Solution paths. Edges = Semantic similarities    │
  │ - Calculate network centrality and resonance scores        │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 4. MARGINALIZATION & VOTING                │
  │ - Consolidate fixed-answers via majority voting            │
  │ - Synthesize open-ended answers using semantic clustering  │
  └────────────────────────────────────────────────────────────┘
```

### 2.1 Diverse Path Sampling
The model is prompted to solve a scientific task step-by-step [412, 425]. Crucially, the decoding parameters are configured to use stochastic nucleus sampling with a temperature $T \in [0.8, 1.2]$ to ensure path diversity, drawing $N$ (typically $N \ge 10$) independent trajectories [95, 114].

### 2.2 Resonance Graph Construction [280, 281]
For each sampled reasoning path $s_i$, we extract its core logical claims [412, 415]:
1. **Node Mapping**: Each path is mapped to a node $v_i \in G_{resonance}$ [281].
2. **Edge Weighting**: We compute the cosine similarity between the vector embeddings of path $s_i$ and path $s_j$:
   $$w_{ij} = \cos(e(s_i), e(s_j))$$
   Edges with similarity below a threshold (e.g., $\gamma = 0.8$) are pruned to isolate divergent clusters [267, 281].

### 2.3 Consensus & Reconciliation [281, 545]
- **Fixed-Answer Tasks**: The system counts the final predictions. For each prediction, it sums the training accuracies or resonance scores of the paths that generated it, choosing the prediction with the highest cumulative weight [201, 202].
- **Open-Ended Tasks**: For qualitative descriptions or plans, the system performs clustering over the resonance graph, extracting the cluster centroid with the highest bridging centrality to compile the final unified answer [184, 545].

---

## 3. Production-Ready Prompt Templates [280, 291]

### Template A: Step-by-Step Reasoner Prompt [291]
```markdown
[System Message]
You are a leading scientist tasked with solving complex scientific or mathematical problems. You must structure your output strictly into two sections:
1. Reasoning: [Detailed, step-by-step intermediate calculations and conceptual derivations.]
2. Answer: [A concise, final answer enclosed in brackets.]

[User Message]
Question: {target_question}

Let's solve this problem step-by-step.
```

### Template B: Mutual Support Cross-Evaluation Prompt [280]
```markdown
[System Message]
You are a peer-review consensus auditor. Your task is to evaluate the logical consistency and mutual agreement between two independent scientific reasoning paths. Identify if they reinforce, contradict, or diverge from each other.

[User Message]
Reasoning Path A:
"""
{reasoning_path_a}
"""

Reasoning Path B:
"""
{reasoning_path_b}
"""

Evaluate the mutual support. Output exactly the following JSON structure:
{
  "mutually_supportive": [true / false],
  "reasoning_alignment_score": "Score from 0.0 (complete contradiction) to 1.0 (exact semantic equivalence)",
  "conflict_analysis": "Identify any specific mathematical, chemical, or logical discrepancies between the two paths."
}
```
