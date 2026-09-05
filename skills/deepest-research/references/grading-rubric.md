# Operational Reference: Programmatic Agent Grading Rubric

> **Runtime use condition:** Read when scoring, comparing, or gating research proposals, code artefacts, or generated research outputs.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.



## Contents

1. 1. Executive Summary & Purpose
2. 2. Multi-Dimensional Scoring Framework
3. 3. Production-Ready Prompt Templates [451, 467]

## 1. Executive Summary & Purpose
The **Programmatic Agent Grading Rubric** establishes an objective, unambiguous, and computationally tractable framework to evaluate AI-generated scientific artifacts, research proposals, and code submissions [20, 451, 467]. Standard academic reviews rely on natural language feedback, which introduces high variance and semantic ambiguity when ingested by LLM agents. This rubric resolves this by translating qualitative evaluations into concrete, multi-dimensional score metrics, implementing a **G&T Fields Scoring (TKGT Metric)** for schema structures [20], enforcing a **Sub-tree Pruning strategy** to evaluate massive hierarchical trees under token-budget limits [482], and compiling an **Experimental Rigor Validation Matrix** to verify code runnable compliance [451].

---

## 2. Multi-Dimensional Scoring Framework
The grading pipeline operates over three distinct verification layers [20, 451, 482]:

```
  ┌────────────────────────────────────────────────────────────┐
  │                1. SUB-TREE PRUNING EVALUATOR               │
  │ - Traverse hierarchical taxonomies from root to leaves     │
  │ - Prune and grade entire sub-trees with float scores       │
  └──────────────────────────────┬─────────────────────────────┘
                                 │ Reduces token cost by 10x
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │               2. G&T FIELDS SCORING (TKGT)                 │
  │ - Compare extracted schema attributes to target reference  │
  │ - Apply strict match rules (Totally, Including, Included)  │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │             3. EXPERIMENTAL RIGOR VALIDATION               │
  │ - Audit setups across planning, execution, and alignment   │
  │ - Enforce strict zero-mock-data assertion policies         │
  └────────────────────────────────────────────────────────────┘
```

### 2.1 Sub-tree Pruning Evaluator (Scale Management) [482]
Evaluating large-scale hierarchical taxonomies or deep code repositories in a single run triggers extreme context-window depletion [482, 529]. To resolve this, the judge model utilizes a bottom-up/top-down hybrid traversal [528]:
- **Pruning Depth**: Past a certain depth (typically depth 3), the judge stops crawling individual leaf nodes [482].
- **Sub-tree Gating**: It evaluates the entire remaining sub-tree in one pass, assigning a float score $s \in [0.0, 1.0]$ representing completeness [482]. This strategy reduces grading token overheads by up to 10x while maintaining $97\%$ alignment accuracy with unpruned evaluations [482].

### 2.2 G&T Fields Scoring (TKGT Metric Rules) [20]
For schema extraction, knowledge graphs, and database tables, generated attributes are matched against human-expert target reference fields [20]:
- **Totally Match (100% Score)**: The generated field matches the target in both form and exact semantics [20].
- **Including (75% Score)**: The generated field represents a neighboring parent concept (naturally inferred from subsequent text) [20].
- **Included (25% or Variable Score)**: The generated field represents a neighboring sub-concept. If the parent concept is separable, the field score is divided by the number of categories; if not separable, it receives $25\%$ [20].
- **Not Match (0% Score)**: Completely different or irrelevant concept [20].

### 2.3 Experimental Rigor Validation Matrix [451]
Every code or experimental plan submission is audited across four non-negotiable dimensions [451]:
1. **Experiment Design**: Did the agent structure the correct high-level plan to address the research question? [451]
2. **Execution Setup**: Is the generated code runnable, handling raw inputs, processing data, and producing output files? [451]
3. **Implementation Alignment**: Is the code aligned with the planned methodology? Are all inputs/outputs legitimately handled with **ZERO mock, hardcoded, or simulated parameters**? [451]
4. **Conclusion Correctness**: Is the final output within the acceptable range of the ground-truth benchmark? [451]

---

## 3. Production-Ready Prompt Templates [451, 467]

### Template A: Multi-Dimensional Research Proposal Grader [467]
```markdown
[System Message]
You are a strict, expert AI Reviewer. Your role is to evaluate a research proposal and assign a comprehensive, objective score based on its Problem, Method, and Experimental Design. You must calculate and output an overall score (0-100) and choose a final decision based on the provided label distribution.

[User Message]
Target Paper:
- Title: {title}
- Abstract: {abstract}

Evaluation Logs:
- Research Problem (Rating 1-5): {problem_rating}
- Research Problem Feedback: {problem_feedback}
- Scientific Method (Rating 1-5): {method_rating}
- Scientific Method Feedback: {method_feedback}
- Experiment Design (Rating 1-5): {experiment_rating}
- Experiment Design Feedback: {experiment_feedback}

Target Decision Distribution: Reject (45%), Accept (Poster) (35%), Accept (Spotlight) (15%), Accept (Oral) (5%).

Calculate the overall score. Output format:
Overall Score (0-100) = {score}
Decision = [Reject / Accept (Poster) / Accept (Spotlight) / Accept (Oral)]
```

### Template B: Experimental Rigor Auditor (Curie Framework) [451]
```markdown
[System Message]
You are a strict Experimentation Agent Verifier operating under the Curie verification guidelines. Your task is to audit the provided experiment log and execution code.

[User Message]
Original Research Question: {research_question}
Ground-Truth Limits: {ground_truth_ranges}
Experiment Log Code:
```python
{submitted_execution_code}
```

Audit the submission across these 4 checkpoints. You must output a boolean [true / false] for each check, followed by a final acceptance verdict.
Checklist:
- Did the agent isolate the target independent and dependent variables? [Yes / No]
- Is the code completely free of hardcoded mock datasets or simulated results? [Yes / No]
- Does the code properly structure file inputs and exports for replication? [Yes / No]
- Does the output metric align with the ground truth? [Yes / No]

Final Verdict: [Accept / Reject]
```
