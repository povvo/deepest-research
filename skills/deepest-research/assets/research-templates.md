# assets/research-templates.md

> **Runtime use condition:** Copy when using the original decomposition, pathfinding, seven-facet proposal, novelty-swap, or rigor-report cards.
> **Template status:** Adapt placeholders to inspected inputs. Treat generated claims, classifications, and future actions as proposals until independently verified.


This asset library contains the static templates, prompt specifications, and structured questionnaire templates used by the **Deep Research Planner**.

---

## Template A: Problem Analysis & Decomposition Card
Use this structured prompt to guide the Analyst agent in analyzing a research question and performing low-rank adaptation style decomposition [463, 475, 611].

```markdown
[System Message]
You are an expert AI Analyst specializing in scientific research problem decomposition. Your objective is to extract, analyze, and partition the core components of the provided research topic [149, 399].

[User Message]
Analyze the following research background and decompose it into logically independent sub-questions:
Research Background: {research_background}

You must output a JSON object adhering exactly to this format:
{
  "Cluster Name": "A clear and specific title focusing on the problem domain (minimum 5 words)",
  "Problem Analysis": {
    "overarching_problem_domain": "The broad scientific field where this problem resides",
    "challenges_and_difficulties": "Specific technical or practical challenges addressed",
    "fundamental_research_goal": "The core objective of the investigation"
  },
  "Decomposed Subquestions": [
    {
      "id": "q1",
      "question": "First logically independent sub-question",
      "reasoning_rationale": "Explanation of why this sub-question is required"
    },
    {
      "id": "q2",
      "question": "Second logically independent sub-question",
      "reasoning_rationale": "Explanation of why this sub-question is required"
    }
  ]
}
```

---

## Template B: Ontological Path Definition Schema
Use this schema to define term properties and connection attributes extracted from knowledge graph paths [236].

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OntologicalPathSchema",
  "type": "object",
  "properties": {
    "path_string": {
      "type": "string",
      "description": "The exact node-relationship-node path traversed"
    },
    "definitions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "term": { "type": "string" },
          "scientific_definition": { "type": "string" },
          "source_relevance": { "type": "string" }
        },
        "required": ["term", "scientific_definition"]
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "node_1": { "type": "string" },
          "node_2": { "type": "string" },
          "relationship_description": { "type": "string" },
          "contextual_implication": { "type": "string" }
        },
        "required": ["node_1", "node_2", "relationship_description"]
      }
    }
  },
  "required": ["path_string", "definitions", "relationships"]
}
```

---

## Template C: 7-Aspect Research Proposal Prompt
Use this prompt to instruct the primary Scientist agent to synthesize a groundbreaking research proposal [205, 237].

```markdown
[System Message]
You are a highly sophisticated Scientist trained in multi-disciplinary research, materials informatics, and biological engineering [191, 237]. You must follow the structural templates strictly.

[User Message]
Given the ontological definitions and relationships, synthesize a detailed, quantitative research proposal that integrates ALL of the identified concepts [237].

Your response must include exactly the following seven keys in valid JSON format:
{
  "1- hypothesis": "A well-defined, novel, and highly detailed hypothesis for the proposed research question.",
  "2- outcome": "Expected findings and impact. Must be quantitative, including material properties, chemical formulas, sequences, or exact numerical values.",
  "3- mechanisms": "Detailed physical, biological, or chemical behaviors across scales (molecular to macroscopic).",
  "4- design principles": "Exhaustive, creative design principles focused on the novel conceptual elements.",
  "5- unexpected properties": "Specific predictions of emergent properties, accompanied by clear logical reasoning.",
  "6- comparison": "A detailed, quantitative comparison table comparing the proposed material/system with conventional technologies.",
  "7- novelty": "A rigorous discussion of how this proposal advances over existing literature, highlighting specific scientific gaps."
}
```

---

## Template D: Novelty Classifier and Suggestion Card
Use this template to classify proposed research ideas and suggest adaptations when overlaps are detected [232, 291, 313].

```markdown
[System Message]
You are an expert Reviewer and Novelty Assistant. Your primary task is to critically evaluate research hypotheses for novelty and feasibility, ensuring zero significant overlap with published work [232].

[User Message]
Evaluate the following research idea against the retrieved related publications:
Proposed Idea: {proposed_idea}
Top-10 Related Papers: {related_papers}

Your response must follow this format:
### Novelty Classification
- **Verdict**: [Novel / Not Novel]
- **Confidence Rating (1-10)**: [Rating]
- **Detailed Overlap Analysis**: [Provide 3-5 sentences analyzing overlap with retrieved papers]

### Adaptability Suggestions (If Overlapped)
Provide three modified idea suggestions, each replacing a different facet:
1. **Alternative Purpose**: Solve a different target problem using the same mechanism.
2. **Alternative Mechanism**: Solve the same target problem using a mechanism retrieved from a distant domain.
3. **Alternative Evaluation**: Validate the relationship using a novel analytical or interventional method.
```

---

## Template E: Experimental Setup and Rigor Report
This template is used by the **Experimental Rigor Engine** to validate experimental designs prior to code execution [434, 451].

```markdown
# Experimental Setup & Rigor Verification

## 1. Variable Isolation Map
| Variable Category | Name / Identifier | Physical Unit / Scale | Isolation / Control Protocol |
| :--- | :--- | :--- | :--- |
| **Independent** | | | |
| **Dependent** | | | |
| **Control 1** | | | |
| **Control 2** | | | |

## 2. Setup Integrity Assessment
- [ ] **Objective Alignment**: The independent and dependent variables directly map to the core hypothesis [437, 451].
- [ ] **Environmental Controls**: All random seeds, hardware configurations (CPUs, GPUs), and environment variables are strictly defined [437].
- [ ] **No Fabricated Data**: The data pipeline uses real, raw inputs rather than mock generator values [437].
- [ ] **Reproducibility Verification**: Setup scripts include complete environment installation instructions [437].

## 3. Iterative Execution Trace (Time Machine Log)
- **Timestamp**: {timestamp}
- **Current Partition**: {partition_id}
- **Baseline Result**: {baseline_metric}
- **Action Taken**: {action_description}
- **Reasoning**: {rationale}
