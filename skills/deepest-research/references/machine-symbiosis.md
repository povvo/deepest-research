# Operational Reference: Model-Machine Symbiosis

> **Runtime use condition:** Read when coordinating paper interpretation with code, simulator, compiler, instrument, or sandbox execution.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## 1. Executive Summary & Purpose
**Model-Machine Symbiosis** is an operational integration framework that coordinates generative language models with sandboxed executable environments, physical simulators, and local compilers to achieve objective, non-hallucinated verification of research findings [120, 144, 440, 470, 483]. Generative models excel at high-level planning and analogical reasoning but are fundamentally limited by single forward-pass limits and arithmetic failures [119, 120, 487]. Machine Symbiosis resolves this by embedding a **ReAct thought-action-observation loop** [120, 260, 471], partitioning tasks between a **Paper Agent** and a **Code Agent** [470], and enforcing a **Pre-Commitment Verification contract** where claims only enter the agent's state when verified by compiled executions [575].

---

## 2. Coordinated Dual-Agent Architecture [470]
The execution pipeline separates literature understanding from repository implementation:

```
                  Scientific Problem / Target Algorithm
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                      PAPER AGENT                       │
       │ - Parses Dense LaTeX Formulas and sections             │
       │ - Downloads and extracts cited works from arXiv        │
       │ - Compiles Literature Report (Theory, Variables, Units) │
       └────────────────────────────┬───────────────────────────┘
                                    │ Outputs report
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                       CODE AGENT                       │
       │ - AST Repository Indexing & Dependency Mapping         │
       │ - Generates and debugs Python execution script         │
       │ - Runs validation test suites (NumPy, SciPy, SymPy)    │
       └────────────────────────────┬───────────────────────────┘
                                    │ Executes in Sandbox
                                    ▼
                   State Update: Verified Observations
```

### 2.1 The Paper Agent (Comprehension Phase) [470, 471]
The Paper Agent handles the literature context [470]. It parses LaTeX code, identifies algorithm variables, and maps references [473]. It executes specialized tools such as `SearchPaper` (resolving undefined variables) and `SearchLiterature` (retrieving cited methodologies to fill gaps) [479, 480]. It outputs a highly structured **Literature Report** [473].

### 2.2 The Code Agent (Implementation Phase) [470, 474]
The Code Agent ingests the Literature Report and walks the repository using Abstract Syntax Tree (AST) tools to parse class and method dependencies [474]. It writes code matching the specified mathematical formulas [474].

### 2.3 Pre-Commitment Verification Loop [575]
To prevent post-hoc rationalization and confirmation bias, the Code Agent operates under a strict verification contract [575]:
1. **Pre-Commit Log**: Before running any script, the agent must log its exact prediction, target metric boundaries, and assertion checks [575].
2. **Deterministic Match**: A compiler executing the script matches the live stdout outputs against the pre-commit logs [159, 575].
3. **Invalidation Gating**: If execution yields errors or deviates from the assertion boundaries, the run invalidates itself [59, 575]. This blocks mock outputs and enforces reproducible setups [437, 451].

---

## 3. Production-Ready Prompt Templates [478, 480]

### Template A: Paper Agent (ReAct Loop) [480]
```markdown
[System Message]
You are a Paper Agent specializing in algorithmic comprehension. Your goal is to systematically extract details from a paper's LaTeX source to compile a Literature Report.
You must formulate your response strictly using the following ReAct sequence:
Thought: [Reason about the current state of understanding]
Action: [Select ONE action: SearchPaper[query], SearchSection[label], SearchLiterature[key, query], or Finish]
Observation: [The system will return the output of your action]

[User Message]
LaTeX Source:
"""
{latex_source_code}
"""

Begin your information extraction step-by-step.
```

### Template B: Pre-Commitment Verification Script [451, 575]
```markdown
[System Message]
You are an Execution Agent. Before writing and running your Python verification code, you must declare your predictions and write assertion tests.
No mock outputs, hardcoded return values, or unverified assumptions are allowed.

[User Message]
Target Equation: {target_equation}
Experimental Bounds: {input_bounds}

Generate a Python script inside a <work> block. The script must:
1. Define the mathematical model using NumPy or SciPy.
2. Formulate 3 distinct unit-testing assertions.
3. Print final verified metrics to stdout.
```
