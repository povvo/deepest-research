# Playbook: Repository-Level Codebase Analysis & AST Indexing

> **Runtime use condition:** Copy when connecting a paper or algorithm description to a repository-level implementation audit.
> **Template status:** Adapt placeholders to inspected inputs. Treat generated claims, classifications, and future actions as proposals until independently verified.


## Overview
You are a Principal Prompt Architect specializing in Codex-compatible Agent Skill engineering. Your core objective is to analyze, index, and comprehend complex, multi-file code repositories, translating theoretical algorithms (often represented as LaTeX code descriptions in scientific publications) into executable code [779, 781]. Large language models (LLMs) frequently struggle with repository-level code development because academic algorithms are characterized by mathematical rigor and brevity, with implementation details scattered across multiple sections and referenced works [781].

To bridge this gap and prevent cascading execution errors, this playbook establishes a standardized methodology to build structural indexing maps and coordinate multi-agent reproduction loops.

---

## 1. Multi-Agent Collaborative Architecture (Sci-Reproducer)
Rather than employing a single-agent generation model, coordinate codebase analysis using a dual-agent framework composed of a **Paper Agent** and a **Code Agent** operating in separate, specialized contexts [783, 795]:

```
  ┌──────────────────────────────┐          ┌──────────────────────────────┐
  │         PAPER AGENT          │          │          CODE AGENT          │
  │   (Algorithm Understanding)  │          │    (Code Implementation)     │
  └──────────────┬───────────────┘          └──────────────▲───────────────┘
                 │ (Literature Report)                     │
                 └─────────────────────────────────────────┘
```

### 1.1 The Paper Agent (Algorithm Comprehension)
*   **Role**: Specialized in extracting, translating, and formalizing the algorithm's mathematical foundations from the LaTeX description and academic context [783, 797].
*   **Actions**:
    *   `SearchPaper[query]`: Searches the target paper's full text to find missing variable definitions, dimensional layouts, or mathematical parameter initializations [796, 830].
    *   `SearchSection[section_id]`: Retrieves entire sections or subsections of the paper to capture qualitative context, preprocessing steps, or evaluation procedures [796, 831].
    *   `SearchLiterature[paper_id, query]`: Downloads and parses the LaTeX source code of cited reference papers from arXiv to resolve external methodological dependencies [796, 824, 831].
*   **Output**: A structured **Literature Report** consolidating the target algorithm's variables, mathematical operations, and hyperparameters [783, 799].

### 1.2 The Code Agent (Repository Implementation)
*   **Role**: Specialized in searching the local code repository, identifying dependencies, and generating compile-safe Python code [783, 800].
*   **Actions**:
    *   `SearchCode[item_name]`: Directly queries the abstract syntax tree (AST) of the repository to fetch definitions of classes, functions, or global variables [796, 825].
    *   `SearchFile[file_name]`: Retrieves the full contents of a target file in the repository to understand file contexts or helper classes [796, 825].
    *   `SearchWeb[query]`: Queries external engines to find API documentation, usage examples, or resolution steps for common framework bugs [796, 835].
    *   `Compiler[code]`: Executes the generated code inside an isolated, containerized environment (e.g., gVisor) to capture traceback logs [33, 796, 800].

---

## 2. Repository-Level Indexing & AST Parsing
To build an automated index of a local repository, the agent must parse Python code files systematically using Abstract Syntax Trees (AST) [825]:
1.  **AST Extraction**: Traverse every `.py` file in the codebase. Parse each file into an AST using the standard Python `ast` module to isolate class declarations, function signatures, input/output arguments, and global variables [825].
2.  **Import & Module Mapping**: Analyze all `import` and `from ... import` statements. Establish a global import dependency map to identify which files rely on internal repository modules versus external libraries [781, 790].
3.  **Dependency Recall Calculation**: Track and measure the percentage of correctly identified dependencies prior to code generation. Maintain distinct metrics for **Intra-File Dependency Recall** (reusing helper functions in the same file), **Cross-File Dependency Recall** (importing custom repository modules), and **External API Recall** (third-party package imports) [784, 794, 801].

---

## 3. The Reasoning Graph (DAG) Specification
To evaluate how well an agent understands the logical structure of a complex algorithm, implement the **Reasoning Graph** metric [784, 792]:

1.  **Node Definition**: During code generation, the model must insert non-overlapping, non-nested comments (e.g., `# Step 1: Initialize weights`) that align with specific blocks of LaTeX algorithm statements [792, 829]. Each node in the graph $G = \{N, E\}$ is defined as $n_i = \langle w_i, c_i \rangle$, where $w_i$ represents the comment and $c_i$ represents the corresponding executable code block [792].
2.  **Edge Construction**: Draw a directed edge $e_{ij} = \langle n_i, n_j \rangle$ if a variable defined, modified, or loaded in node $n_i$'s code block ($c_i$) is used as an input to node $n_j$'s code block ($c_j$) [792].
3.  **Graph Alignment & Similarity**: Match the agent-generated graph $G_g$ against a reference reasoning graph $G_r$ using a multi-criteria scoring algorithm [792, 793]:
    $$S_r = \sum_{n_i \in N_m} s_{n_i} + \sum_{e_j \in E_m} s_{e_j}$$
    where $s_{n_i}$ and $s_{e_j}$ represent normalized node and edge significance scores, calculated by the complexity of variable definitions, function calls, and lines of code [793].

---

## 4. Debugging & Error Mitigation
Repository-level code generation frequently suffers from a high rate of compile-time syntax errors and execution failures [803]. Use the following checklist to detect and mitigate common failure modes:

*   [ ] **Dependency Mismatch Check**: Verify that all custom repository classes used in the generated function are imported using correct cross-file paths. Incorrect cross-file dependencies are the primary cause of syntax errors in repository code [803].
*   [ ] **Randomness Neutralization**: Fix all random seeds and replace non-deterministic data structures (such as unordered sets) with deterministic equivalents (such as sorted lists) to guarantee execution reproducibility [823].
*   [ ] **Subtle Parameter Alignment**: Cross-reference extracted values (such as dropout rates, learning rates, or epoch configurations) in the literature report against the repository's configuration files to prevent semantic mismatches [804, 829].
*   [ ] **Compiler Traceback Feedback Loop**: If execution fails, capture the compiler's output and feed it back directly into the Code Agent's debugging prompt. Let the model analyze the exact line number and variable state to refine its implementation iteratively [796, 800].
