# Playbook: Computational Notebook Engineering (Jupyter / ipynb)

> **Runtime use condition:** Read when the plan uses Jupyter or another stateful computational notebook and must control execution order and outputs.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


Computational notebooks (such as Jupyter and Google Colab) are interactive computing environments that freely mix natural language, executable code, visualizations, and execution states [90, 92]. To successfully deploy autonomous research agents in computational notebooks, the system must handle multi-turn interaction, maintain state continuity, and evaluate code correctness dynamically [89, 92].

---

## 1. Linearization and Context Construction
Computational notebooks must be serialized into a flat, sequential text string to be ingested by Large Language Models [101, 112].

### 1.1 Serialization using nbconvert
The system utilizes the `nbconvert` library to linearize Jupyter notebooks (.ipynb) to standard Python code [101]:
- **Cell Delimiters**: Code cells must be concatenated using the special structured delimiter:
  ```python
  # In[<cell_index>]:
  ```
  to separate code blocks and preserve cell execution order [101].
- **Markdown Conversion**: Markdown cells containing explanations, tutorial instructions, or user goals are converted directly to Python comments (preceded by `# `) [101].
- **Data Filtering**: To prevent training-to-test data leakage, pre-processing must strip out redundant instructional outlines, hints, and reference answers from tutorially-derived notebooks [101, 110].

### 1.2 Interactive State Tracking
Unlike single-file code completion, data science notebooks feature multi-round execution blocks with complex dependency structures [92, 94]:
- **Execution States**: The agent must maintain a log of the execution history of preceding cells. Variables (such as pandas DataFrames or numpy arrays) modified in-place must be tracked across cell transitions [94, 101].
- **Long-Range Data Dependencies**: Code generation must account for variables instantiated in early setup blocks (e.g., loading a CSV dataset via `pd.read_csv()`) and modified sequentially throughout the session [91, 92].

---

## 2. Few-Shot Prompting and Step-by-Step (SbS) Decomposition
To elicit high-quality, explainable, and diverse data science code, the system deploys targeted few-shot prompting templates [93]:

```markdown
[System Message]
You are an expert Data Science Assistant. Your goal is to write pandas and numpy code to execute data wrangling and exploratory data analysis (EDA) tasks in computational notebooks [94].

[User Intent / Cell Prompt]
Intent: {user_intent}
Preceding Notebook Context:
{notebook_context}

Write your solution step-by-step. For each step:
1. Provide an inline natural language comment explaining the data transformation [93, 104].
2. Write the corresponding executable Python statement.
Ensure all intermediate results are assigned to descriptive variables [93, 104].
```

### 2.1 Preamble and Explanation Benefits
Prompting models to write inline comments explaining their data transformations (e.g., "Step 1: Create a new column with the average score") significantly enhances:
- **Prediction Diversity**: Explaining steps iteratively increases the structural variation of generated programs, facilitating **self-consistency re-ranking** [93, 104].
- **Novice Comprehension**: Code blocks annotated with clear procedural rationale are vastly easier for human scientists to audit and steer [93, 104].

---

## 3. Dynamic Execution and Fuzzy Output Matching
Traditional code benchmarks rely on strict, signature-based unit testing [98]. In computational notebooks with free-form code, the agent's output must be evaluated utilizing **Fuzzy Output Matching** heuristics to verify functional equivalence [98, 99].

### 3.1 Verification and Canonicalization Heuristics
When evaluating a generated cell script against a ground-truth reference, the execution framework applies the following normalization rules [99]:
1. **Container Alignment**: If the output variable is a container type (e.g., List, Tuple, Set, numpy.ndarray, pandas.Series, or single-column pandas.DataFrame), the system canonicalizes the variable into a standardized array type prior to comparison [99].
2. **Partial DataFrame Matching**: For complex multi-column DataFrames, the generated frame is marked as functionally correct if it contains all of the columns (and corresponding cell values) present in the reference DataFrame [99]:
   $$
orall v_i \in V_{	ext{reference}}, \quad v_i \in V_{	ext{generated}}$$
   This allows the user to easily filter or slice the target columns without penalizing the agent for generating supplementary columns [99].
3. **Reproducibility Controls**: All random seeds must be fixed, and non-deterministic structures (e.g., unordered sets or dictionary traversals) must be replaced with deterministic equivalents to prevent execution variance [383, 397].
