# Operational Reference: Knowledge-Boundary Prompting (KBP)

> **Runtime use condition:** Read when the plan must detect unanswerable requests, calibrate uncertainty, or define refusal and evidence-escalation rules.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.



## Contents

1. 1. Executive Summary & Purpose
2. 2. Core Operational Workflow
3. 3. Production-Ready Prompt Templates [551]
4. 4. Evaluation and Verification Protocol [551, 552]

## 1. Executive Summary & Purpose
The **Knowledge-Boundary Prompting (KBP)** methodology is designed as a proactive alignment and calibration framework to prevent large language models from hallucinating when presented with unanswerable, out-of-distribution, or speculative scientific queries [549, 553]. Standard post-hoc hallucination detection mechanisms (such as self-critique or consensus checking) operate reactively after generation. KBP, conversely, establishes a multi-stage cognitive filter that trains the model to self-evaluate its parametric knowledge, execute refusal-based reasoning, and formulate structured, explicit refusals when faced with queries exceeding its trained boundaries [549, 550].

---

## 2. Core Operational Workflow
The execution of KBP consists of three distinct, sequential steps [550]:

```
  ┌────────────────────────────────────────────────────────────┐
  │                   STEP 1: Self-Evaluation                   │
  │ - Query parsed against parametric knowledge thresholds     │
  │ - Classify: "yes" (known), "no" (unknown), "unsure"        │
  └──────────────────────────────┬─────────────────────────────┘
                                 │ If "no" or "unsure"
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │               STEP 2: Refusal-Based Reasoning              │
  │ - Formulate detailed gap rationales                        │
  │ - Identify missing temporal/contextual information         │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │            STEP 3: Explicit Refusal Formulation            │
  │ - Render standard refusal response (e.g., "I cannot...")   │
  │ - Supply exact citations of limits                         │
  └────────────────────────────────────────────────────────────┘
```

### Step 1: Self-Evaluation
The model is prompted with a query alongside an evaluation instruction [551]. It evaluates whether the subject matter falls within its pre-trained corpus or retrieved context:
- **Known ("yes")**: Proceed to standard Chain-of-Thought reasoning.
- **Unknown ("no")** or **Speculative ("unsure")**: Route to Step 2 [551].

### Step 2: Refusal-Based Reasoning
The model analyzes the precise nature of its information gap [550, 551]. Rather than generating speculative answers, it must state the missing scientific variables, temporal cuts, or data bounds (e.g., "The target query relates to publications after the January 2023 training cut-off, which are not present in my local index") [134, 551].

### Step 3: Refusal Language Formulation
The model outputs a clear, domain-specific refusal using specialized, verified templates to maintain user trust and avoid ambiguous or over-generalizing refusals [549, 550].

---

## 3. Production-Ready Prompt Templates [551]

### Template A: Step 1 - Self-Evaluation Prompt
```markdown
[System Message]
You are a calibrated scientific metadata auditor. Your task is to evaluate whether the user's query can be verified objectively using your internal pre-trained weights or the provided context. Do not answer the question yet.

[User Message]
Query: {user_query}

Evaluate your knowledge boundary. You must respond in the following JSON format exactly:
{
  "evaluation_verdict": "[yes / no / unsure]",
  "reasoning_class": "Provide a 1-sentence assessment of whether the specific entities, relationships, or physical properties in the query are present in your pre-trained or retrieved scope."
}
```

### Template B: Step 2 & 3 - Refusal Formulation Prompt
```markdown
[System Message]
You are an expert Research Assistant operating under strict factuality and verifiability constraints. Based on your previous self-evaluation, you have identified that the query falls outside your knowledge boundary. You must formulate a structured refusal. Do not attempt to guess, approximate, or extrapolate.

[User Message]
Query: {user_query}
Gaps Identified: {gap_description}

Generate your response in the following format:
Reasoning: [State 2-3 sentences explaining exactly why this query exceeds your knowledge boundaries, referencing missing temporal cut-offs, unindexed databases, or lack of peer-reviewed experimental values.]
Answer: [I cannot confidently answer this query. Please consult an authoritative domain resource or a peer-reviewed database.]
```

---

## 4. Evaluation and Verification Protocol [551, 552]
To verify KBP effectiveness, researchers must evaluate model rollouts across three standard benchmarks:
1. **WebQuestions** (knowledge-intensive queries) [551].
2. **Natural Questions (NQ)** (complex real-world queries) [551].
3. **BoolQ** (binary factual questions) [551].
4. **SQuAD 2.0 Unanswerable Subset** (adversarial unanswerable queries) [551].

### Key Performance Metrics [552]
- **Hallucination Rate (HR)**:
  $$HR = 
rac{	ext{Unanswerable queries where LLM generates an incorrect answer}}{	ext{Total unanswerable queries}} 	imes 100\%$$
- **Correct Answer Rate (CAR)**:
  $$CAR = 
rac{	ext{Answerable queries answered correctly}}{	ext{Total answerable queries}} 	imes 100\%$$
- **Refusal Accuracy (RA)**:
  $$RA = 
rac{	ext{Unanswerable queries correctly identified and refused}}{	ext{Total unanswerable queries}} 	imes 100\%$$

A successful implementation must drive HR to $< 5\%$ while maintaining CAR within $1\%$ of the direct prompting baseline [552, 553].
