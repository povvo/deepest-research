# 5. AI Research Methodology Tools and Prompt Library

> **Runtime use condition:** Read when selecting task-specific AI-assisted research prompts, validation calculators, or method checklists.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## Contents

1. 1. Prompt Template Library (Task-Specific, Validated)
2. 2. Methodology Decision Trees
3. 3. Validation Guidelines (Calculators)
4. 4. Case Studies

This document serves as a copyable **Prompt Library**, **Decision Tree Repository**, **Validation Calculator**, and **Case Study** manual to support AI-driven social and scientific research, strictly grounded in academic literature [67, 134, 458, 460].

---

## 1. Prompt Template Library (Task-Specific, Validated)

### 1.1 Systematic Review Abstract Screening (Based on Cao et al. & LitLLM)
- **Version**: 1.1.2 (Tracked against Semantic Scholar API)
- **Execution Mode**: Zero-shot with Context

```markdown
[System Prompt]
You are a professional reviewer specializing in academic screening. Your goal is to evaluate candidate papers for a systematic review [7, 134, 135].

[User Input]
Target Review Abstract: {target_abstract}
Candidate Paper Title: {candidate_title}
Candidate Paper Abstract: {candidate_abstract}

[Instructions]
Analyze the candidate paper against the target review abstract. Answer exactly "yes" if the candidate paper strictly aligns with the review topic and should be included, or "no" if it contains distracting concepts or fails to match [134, 551, 566].
Output JSON format:
{
  "included": "yes/no",
  "reason": "Provide a 2-sentence rationale detailing the overlap of Purpose, Mechanism, and Evaluation [320]."
}
```

### 1.2 Thematic Analysis Five-Component Modular Prompt (Based on arXiv:2511.14528v1)
- **Version**: 2.0.1 (Modular Text-to-Table / Graph Extraction)

```markdown
[System Prompt]
You are an expert Ontologist and Qualitative Analyst [304, 305].

[User Input]
Transcript Text: {transcript_text}

[Instructions]
Parse the provided transcript segment and extract the five modular components of thematic analysis [576, 577]:
1. **Source Node**: The primary actor or subject speaking.
2. **Concept**: The core thematic node (noun or short phrase, ≤ 3 words).
3. **Context**: Specific situational factors (e.g., emotional state, background).
4. **Relationship**: The functional connection to other concepts.
5. **Direct Excerpt**: Verbatim quote proving this connection [369].

Format your response exactly as a JSON array of objects with keys: "source", "concept", "context", "relationship", "excerpt".
```

### 1.3 Deductive Coding with Predefined Codebook
- **Version**: 1.0.4

```markdown
[System Prompt]
You are a scientific annotator executing deductive coding over raw qualitative transcripts [472].

[User Input]
Codebook Definitions: {codebook_json}
Transcript Segment: {segment_text}

[Instructions]
Assign exactly one code label from the codebook to the transcript segment. Provide your output in the following format [472]:
Code Label: [Label Name]
Justification: [Provide a detailed explanation of how the segment's content satisfies the code's specific inclusion criteria.]
```

### 1.4 Inductive Theme Generation from Interview Transcripts
- **Version**: 1.2.0

```markdown
[System Prompt]
You are an AI Analyst trained in inductive qualitative coding.

[User Input]
Transcript Lines: {transcript_lines}

[Instructions]
Review the transcript lines carefully without any predefined codes. 
1. Identify emerging patterns or recurring concerns and write down raw observations.
2. Group the pattern observations into broader, abstract themes.
3. For each theme, propose a specific theme name (≥ 5 words) and a 3-sentence definition [591, 592].
```

### 1.5 Survey Question Appraisal Prompt (AGIL-Aligned)
- **Version**: 1.1.0

```markdown
[System Prompt]
You are an expert Survey Methodologist evaluating questionnaire items for scientific validity [450, 457].

[User Input]
Survey Question: {question_text}
Answer Scale: {answer_scale}

[Instructions]
Appraise the question using the following criteria [457]:
1. **Unambiguity**: Is there exactly one clear interpretation?
2. **Acceptability**: Does the correct answer align with current academic consensus?
3. **Scale Coherence**: Are the distractors clearly distinct from the correct answer?

Provide a pass/fail verdict for each criterion and a detailed appraisal report.
```

### 1.6 Structured Data Extraction with JSON Schema
- **Version**: 3.0.2

```markdown
[System Prompt]
You are a highly precise Data Extraction Agent. You do not extrapolate or make assumptions [369, 492].

[User Input]
JSON Schema: {json_schema}
Target Document: {document_text}

[Instructions]
Extract the structured fields from the target document to populate the JSON schema. Ensure that:
- Every numeric value is extracted verbatim without rounding [492].
- If a value cannot be found in the text, omit the field (do not use null or placeholders) [492].
- Verbatim text spans must be saved to the "excerpts" list [369].
```

### 1.7 Cross-Position Verification Prompt Pairs (Dialectical Checking)
- **Version**: 1.0.1

```markdown
[Prompt A: Proposer]
Query: {query}
Based on the available context, generate a detailed research hypothesis and proposed methodology.

[Prompt B: Critic]
Proposed Hypothesis: {hypothesis_output}
Review the proposed hypothesis critically. Identify three potential logical flaws, missing control variables, or similar publications that conflict with this design [94, 654].
```

### 1.8 Causal Ordering Elicitation
- **Version**: 1.1.3 (LeGIT-Grounded [458, 460])

```markdown
[System Prompt]
You are an expert in causal inference and structural equation modeling [458].

[User Input]
Variables: {variables_list}
Domain Context: {domain_context}

[Instructions]
Analyze the variables and determine their plausible causal ordering based on domain knowledge:
- Distinguish between pure correlation and direct causation [460].
- Identify potential confounding variables [460].
- Output the structural causal model as a set of direct equations.
```

### 1.9 Contradiction Surfacing & Dialectical Synthesis
- **Version**: 1.0.2 (MM-DCCRS-Aligned [619])

```markdown
[System Prompt]
You are a Dialectical Synthesis Agent. Your role is to identify and resolve internal contradictions [619].

[User Input]
Text Stream A: {findings_set_A}
Text Stream B: {findings_set_B}

[Instructions]
Identify points where findings from Stream A and Stream B directly contradict each other. Do not attempt to smooth over these contradictions. Instead, surface them explicitly and propose a synthesized theoretical framework that explains the boundary conditions of both [345].
```

### 1.10 Boundary Condition Testing
- **Version**: 2.1.0 (Kuhn Crisis Discovery [345])

```markdown
[System Prompt]
You are a scientific critic investigating the boundary conditions of a theoretical finding [345].

[User Input]
Core Finding: {core_finding}
Experimental Variables: {variables_details}

[Instructions]
Formulate exactly three stress-test scenarios under which the core finding would NOT hold. Specifically explore:
- Extreme scale variations [533].
- Symmetry violations [533].
- Environmental context shifts [191].
```

---

## 2. Methodology Decision Trees

### 2.1 AI Method Selection Decision Tree
```
Is your target research data primarily structured (surveys/experiments) or unstructured (text)?
├── Structured
│   └── Do participants include human subjects?
│       ├── Yes ──> Use Chatbot-Based Interviewing & Catch Trial Filters [77]
│       └── No ──> Use Silicon Sampling & Monte Carlo Simulation [122]
└── Unstructured
    └── Is your analytical goal hypothesis validation or theme exploration?
        ├── Validation ──> Use Deductive Coding (JSON Schema) & Krippendorff's alpha [206, 263]
        └── Exploration ──> Use LATA Viewpoint Decomposition & Parallel Taxonomy (FLMSCI) [472, 588]
```

### 2.2 IRB Ethics Navigation Tree (Belmont Report & NeurIPS Guidelines)
```
Does your research involve human subjects, crowdsourced workers, or personal text assets?
├── Yes
│   ├── Did you pay at least the local minimum wage?
│   │   ├── No ──> FLAG: Violates NeurIPS Code of Ethics [543]
│   │   └── Yes ──> Proceed to IRB Approval Check
│   ├── Do you have documented IRB (or equivalent) approval?
│   │   ├── No ──> FLAG: High biosecurity/compliance risk [544]
│   │   └── Yes ──> Document IRB reference and obtain informed consent [535, 545]
│   └── Does your raw data contain PII or offensive text?
│       ├── Yes ──> Execute pre-deployment sterilization & anonymization [200, 509]
│       └── No ──> Proceed to publication
└── No ──> Ensure all source papers are open-access and proceed [536]
```

---

## 3. Validation Guidelines (Calculators)

### 3.1 Intercoder Agreement (Fleiss' Kappa Formula)
For qualitative coding validation, compute Fleiss' Kappa ($ \kappa $) to measure agreement among $N$ coders for $n$ segments across $k$ categories:
$$ \kappa = 
rac{ar{P} - ar{P}_e}{1 - ar{P}_e} $$
Where:
- $ ar{P} $ is the actual observed agreement [556].
- $ ar{P}_e $ is the agreement expected by chance [556].
*Guidance*: A Fleiss' Kappa score of $\ge 0.70$ indicates substantial agreement, validating the reliability of LLM coding [556].

### 3.2 Effective Context Window Calculator
When processing long transcripts or multiple paper abstracts, calculate your token consumption before launching multi-agent debate:
$$ 	ext{Total Tokens} = T_{	ext{System}} + M 	imes T_{	ext{Segment}} + N 	imes T_{	ext{AgentResponse}} $$
Where:
- $M$ is the number of batched transcripts [558].
- $N$ is the number of reasoning loops (e.g., 5-turn debate) [152].
*Rule of thumb*: Keep total tokens within 80% of the model's native context window to prevent the "lost in the middle" effect and ensure high recall of extracted variables [560].

---

## 4. Case Studies

### 4.1 Systematic Review Abstract Screening (LitLLM Case Study)
- **Objective**: Synthesize a literature review comparing 4 image-guided clothing retrieval papers [548, 549].
- **Workflow**:
  1. Input paper abstract provided to the summarizer agent [134].
  2. Dense retrieval (SentenceBERT) extracted candidates [554].
  3. RankGPT re-ranked candidate papers listwise [295, 320].
- **Results**: Verified that the top recommended paper matched the human-selected paper cited in the original research [139].

### 4.2 Qualitative Coding (LATA Viewpoint Case Study)
- **Objective**: Analyze 50 semi-structured interview transcripts from professional NLP researchers regarding peer-review deficiencies [201].
- **Workflow**:
  1. Transcripts processed sentence-by-sentence to extract independent viewpoints [472].
  2. Deductive codebook applied to label segment errors (e.g., "Copy-pasted Summary", "Concurrent work", "Duplication") [209].
- **Results**: Reached 94% inter-annotator agreement on segment classification and identified that models generated significantly more deficient review segments than humans [203, 556].
