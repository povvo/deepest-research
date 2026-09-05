# Playbook: Publication-Quality LaTeX Synthesis and Error Backtracking

> **Runtime use condition:** Read when the research deliverable includes LaTeX, equations, bibliographies, TikZ, or compile-and-backtrack validation.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


Scientific research communication relies heavily on the LaTeX typesetting system for mathematical modeling, structural tables, and figure generation [68, 122, 513]. To automate report generation and paper development, agents must compile LaTeX documents, extract and manage TikZ graphics, and dynamically resolve compilation errors [122, 124, 521].

---

## 1. LaTeX Chapter Synthesis and Notation Extraction
The paper development subsystem (e.g., **CycleResearcher**) partitions manuscript drafting into distinct, specialized LaTeX compilers [316, 521]:

### 1.1 Structural Chapter Drafting
The **Paper Agent** generates isolated chapters (e.g., Abstract, Introduction, Methodology, and Evaluation) using targeted prompts that reference preceding chapters to prevent repetition and ensure narrative flow [521, 522]:
- **Syntax Boundaries**: All generated sections must strictly output compile-ready LaTeX syntax (e.g., utilizing `\begin{align}` and `\begin{table}`) and omit Markdown formatting blocks [513, 519, 522].
- **Notation Mapping**: The agent must extract all variables, parameters, and symbols used across mathematical derivations and compile them into a standardized **Table of Notations** table using the `booktabs` package [523, 524]:
  ```latex
  \begin{table}[H]
  \centering
  \renewcommand{\arraystretch}{1.3}
  \begin{tabular}{>{\raggedright\arraybackslash}p{3cm}>{\raggedright\arraybackslash}p{11cm}}
  \toprule
  \textbf{Notation} & \textbf{Description} \\
  \midrule
  \bottomrule
  \end{tabular}
  \caption{Table of Notations}
  \label{tab:notations}
  \end{table}
  ```

---

## 2. Interactive Compilation and Safety Guards
To prevent the generation of broken or uncompilable papers, the agent operates inside a **Compilation Guard** execution loop [510]:
- **Syntactic Auditing**: Prior to committing any textual or mathematical revision to a TeX manuscript, the system triggers an offline LaTeX compilation command (e.g., `pdflatex` or `xelatex`) [122, 510].
- **State Reversion**: If the compilation fails, the system blocks the file update, logs the compiler's diagnostic output, and redirects the error stream to the backtracking module [124, 510].

---

## 3. The Iterative Resampling Backtracking Method
When LaTeX compilation or TikZ rendering throws a syntax error, the agent must not restart generation from scratch [124]. Instead, it implements the **Iterative Resampling** diagnostic backtracking algorithm [124]:

```
                     ┌───────────────────────────────┐
                     │   Step 1: Compile TeX file    │
                     └───────────────┬───────────────┘
                                     │
                                     ▼ (If Error Occurs)
                     ┌───────────────────────────────┐
                     │   Step 2: Parse Logfile to    │
                     │   locate exact error line (L)  │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │  Step 3: Calculate Reversion  │
                     │  Line: R = L - 4*(i - 1)      │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │ Step 4: Delete lines below R, │
                     │ resume sampling from there    │
                     └───────────────────────────────┘
```

### 3.1 Backtracking Line Calculation Formula
The exact reversion depth is calculated dynamically as a function of the current debugging iteration $i$ [124]:
$$R = L - 4(i - 1)$$
where:
- $L$ represents the 1-indexed line number of the error identified by parsing the compiler `.log` file [124].
- $i$ represents the current debugging iteration step [124].
- By incrementally backing up further (e.g., deleting 0 lines on step 1, 4 lines on step 2, 8 lines on step 3), the system dynamically searches for the logical origin of the syntax mistake (such as an unclosed bracket or unescaped macro) without discarding the entire valid prefix [124].

---

## 4. TikZ Vector Graphics Extraction
Scientific drawings and flowcharts are extracted from paper LaTeX sources using regular expression parsing and preamble matching [122]:
- **Environment Mining**: The system searches LaTeX files for `\begin{tikzpicture}` and `\end{tikzpicture}` blocks [122].
- **Preamble Re-assembly**: Because TikZ drawings rely on macros and package imports declared in the paper's main preamble, the extractor must parse macro definitions (`\newcommand`) and retain required packages (`\usetikzlibrary`) [122].
- **Compilability Filter**: TikZ blocks are rendered as standalone images in a secure sandbox; any drawing failing standalone compilation (due to missing dependencies) is automatically excluded from the reference library [122].
