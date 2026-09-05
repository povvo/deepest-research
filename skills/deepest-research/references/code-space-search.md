# Playbook: Code-Space Tree Search Optimization & Iterative Debugging (AIDE)

> **Runtime use condition:** Read when the study includes iterative code search, ML pipeline improvement, or execution-tree debugging.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## Overview
You are a Principal Prompt Architect specializing in Codex-compatible Agent Skill engineering. This playbook implements the **AI-Driven Exploration (AIDE)** framework, which conceptualizes machine learning engineering and data science script optimization as a tree-search problem in the space of code [666]. Rather than optimizing an entire machine learning pipeline simultaneously ("all-at-once"), which makes it impossible to attribute performance changes to specific code changes, AIDE explores and optimizes the codebase iteratively and systematically through code-space tree exploration [666, 695].

---

## 1. Solution Tree (T) Architecture
AIDE maintains a persistent, append-only **Solution Tree** $T$ in memory [668, 986].
*   **Nodes**: Represent concrete, complete, and executable Python scripts ($s \in S$), with $s_0$ designating the empty or baseline script [668].
*   **Edges**: Represent directed transition attempts ($s 
ightarrow s'$), capturing code modifications proposed by the agent [668].
*   **Execution Scores**: An evaluator $h: S 
ightarrow \mathbb{R}$ executes the script on a development set and assigns a scalar performance metric (e.g., validation accuracy or F1-score) to the node, storing it in the tree [668, 901].

```
       [s_0: Baseline] (Acc: 0.52)
        /                [s_1] (Bug)     [s_2] (Acc: 0.58)
                      |
                    [s_3] (Acc: 0.64)
```

To prevent context window saturation and prompt bloat, the model must operate statelessly [672]. Use the **Summarization Operator** $\Sigma(T)$ to condense historical attempts [668]. $\Sigma(T)$ extracts only:
1.  The high-level natural language idea behind each modification attempt [668].
2.  The resulting execution score or compilation error traceback [668].
3.  The parent-child relationships, bypassing the need to feed the raw source code of previous versions into the prompt [668, 672].

---

## 2. Specialized Coding Operators
At each step of the search, invoke the **Coding Operator** $f(s, \Sigma(T))$ to propose transitions using three specialized prompts and operational states [669, 670]:

### 2.1 Drafting
*   **When to invoke**: When no previous solution exists, or when starting a new pipeline branch from $s_0$ [670].
*   **Workflow**:
    1.  Prompt the model to write a brief, conceptual plan outlining the proposed network architecture, data preprocessing pipeline, or modeling technique [670].
    2.  Generate a complete, single-file Python script implementing that plan [670].
    3.  Validate that the script saves all intermediate processed datasets and predictions locally (CSV, JSON, or pickle) to facilitate downstream analysis [982].

### 2.2 Debugging
*   **When to invoke**: When the executed script encounters compile-time syntax errors or runtime exceptions (e.g., `AttributeError`, `ImportError`, `KeyError`, `ValueError`) [670, 913].
*   **Workflow**:
    1.  Capture the complete error traceback and environment log chunk [670, 694].
    2.  Isolate the specific buggy lines without modifying the overall algorithmic approach [670].
    3.  Generate a corrected script, verifying that the fix does not delete necessary functionalities [48, 670].

### 2.3 Improving
*   **When to invoke**: When a valid, executable solution script exists, but its performance score needs optimization [670].
*   **Workflow**:
    1.  Instruct the model to propose exactly **one atomic modification** (e.g., switching an optimizer from SGD to Adam, adding a dropout layer, adjusting a learning rate, or implementing a new feature engineering column) [670, 671].
    2.  Enforce this "single-variable" isolation rule so that performance changes can be directly and objectively attributed to the specific modification [670, 695].

---

## 3. Search Policy & Execution Loop
The tree search executes as an iterative loop defined by Algorithm 1 [401, 668]:

1.  **Node Selection**: Apply the search policy $\pi(T)$ to select the most promising non-buggy node $s \in T$ as the base solution for the next iteration [668, 672].
2.  **Action Proposal**: Invoke the Summarization Operator $\Sigma(T)$ to construct the context prompt [668]. Propose the next step (Draft, Debug, or Improve) [670].
3.  **Code Generation**: Use the coding operator $f(s, \Sigma(T))$ to generate the new script $s'$ [668].
4.  **Sandbox Execution**: Execute $s'$ in an isolated Python environment [342, 668].
5.  **Score Attribution**: Log the output, capture any traceback, compute the scalar score, and insert $s'$ into $T$ [668].
6.  **Plagiarism Guard**: Run a local plagiarism detection script (e.g., Dolos similarity checker) to compare $s'$ against public baseline notebooks [598]. Flag any code submission with a similarity score over 60% as potentially leaked or memorized [598].
7.  **Iterate**: Repeat for a predetermined number of rounds $T$, returning the best-performing executable script snapshot [404, 901].
