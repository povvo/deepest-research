# Specification: Structure-Aware Shapley Valuation of Agent Skills (SkillSV)

> **Runtime use condition:** Copy only when the user asks to value, prune, or compare skill components using the retained SkillSV specification.
> **Template status:** Adapt placeholders to inspected inputs. Treat generated claims, classifications, and future actions as proposals until independently verified.


## Overview
You are a Principal Prompt Architect specializing in Codex-compatible Agent Skill engineering. This specification defines **SkillSV (Skill Shapley Valuation)**, a deterministic and mathematical control plane designed to compile, audit, and quantitatively value the individual components, prompts, and code blocks of AI Agent Skills [1017, 1018]. By modeling skills as restricted-cooperation games, SkillSV evaluates the marginal performance contribution of each skill unit under strict structural and dependency constraints, preventing length-based biases and identifying targets for compression or deletion [1017, 1018, 1021].

---

## 1. Skill Compilation Architecture
The SkillSV compiler $C$ maps a raw Markdown skill file and its associated resource files to a triple [1018]:
$$G = (N, D, H)$$
where:
*   $N$ is the set of **Valuation Units (Players)** [1018].
*   $D$ is the Directed Acyclic Graph of **Dependency Constraints** among units [1018, 1030].
*   $H$ is the **Document Hierarchy** constraining the permutation and rendering order of the text [1018].

```
               [m: Frontmatter Unit] (Trigger)
                        ▲
                        │ (Trigger Edge)
               [n1: Instruction Unit]
               /                           (Def-Use Edge)               (Link Edge)
             ▼                             ▼
    [s: Resource Unit]            [r: Related Work]
```

### 1.1 Valuation Units (N)
*   **Markdown Body Units**: Each top-level Markdown list item (such as a step definition or prompt instruction) opens a separate unit $n_i$ [1018]. Indented continuations stay grouped with their parent [1018].
*   **Resource Units**: Auxiliary codebase files (e.g., Python scripts, JSON schemas, or reference templates) are compiled as independent resource units [1018].
*   **Frontmatter Unit ($m$)**: The metadata block containing the skill's name and trigger description [1021].

### 1.2 Dependency Edges (D)
An edge $u 
ightarrow v \in D$ indicates that unit $u$ requires unit $v$; therefore, a coalition of units is feasible if and only if it is downward closed under these edges [1019]. The compiler extracts nine families of dependency edges, including [1019, 1031]:
*   `LINK` (R1): Markdown hyperlinks pointing to specific sections [1031].
*   `PATH` (R2): Verbatim file-path tokens pointing to auxiliary resources [1031].
*   `HEADING-REF` (R3): Verbatim heading mentions [1031].
*   `DEF-USE` (R4): Verbatim code symbols in unit $u$ that are defined in resource unit $v$ [1032].
*   `TRIGGER` (R6): Connects every execution unit to the frontmatter unit ($m$) [1021, 1032].
*   `TABLE-CONT` (R7): Headerless table rows pointing to the parent unit containing the table header [1032].
*   `LIST-CONT` (R8): Unordered bullet points refining preceding ordered list items [1032].

---

## 2. Counterfactual Rendering Operators
To evaluate a coalition of units $S \subseteq N$, define two counterfactual rendering operators to construct the executable skill artifact [1029]:

1.  **Deconstructive Deletion ($
ho_{del}(S)$)**: Completely deletes all absent units $N \setminus S$ from the skill file, resulting in a physically shorter prompt or script [1020, 1029].
2.  **Neutral Padding ($
ho_{pad}(S)$)**: Replaces the text spans of all absent units $N \setminus S$ with length-matched neutral characters or whitespace placeholders [1020, 1029, 1034].

### 2.1 Context-Occupancy Cost Estimation
By comparing the performance of the agent under both operators, SkillSV isolates the true **Content Value** of a prompt block from its **Context-Occupancy Cost** (the performance degradation or gain caused purely by changes in prompt token length) [1020, 1021]:
$$	ext{Content Value} = \phi_{i, 
ho_{pad}}$$
$$	ext{Context Cost} = \phi_{i, 
ho_{pad}} - \phi_{i, 
ho_{del}}$$
$$	ext{Net Effect} = \phi_{i, 
ho_{del}}$$
A unit with high Content Value but a large negative Context Cost represents an ideal candidate for **Compression** (restructuring the prompt to convey the same meaning with fewer tokens) rather than deletion [1021].

---

## 3. Chain-Coupled Task Windows
To reduce evaluation noise across diverse tasks without escalating API call costs, implement the **Chain-Coupled Task Window** estimator [1022, 1023]:

1.  For each sampled feasible order of units $\pi$ (respecting DAG dependencies $D$ and document hierarchy $H$), draw a small, stratified task window $B_k$ of size $b \ll M$ tasks [1022, 1029].
2.  Maintain a strict **Task-Pairing Rule**: Evaluate every prefix of the permutation order $\pi$ on the identical task window $B_k$ [1022, 1023]. This cancels out task-level difficulty variations, allowing precise estimation of the marginal unit value [1022]:
    $$\hat{\phi}_{i, 
ho} = 
rac{1}{K} \sum_{k=1}^{K} \left[ ar{v}_{
ho}(S_{\pi_k}^i \cup \{i\}, B_k) - ar{v}_{
ho}(S_{\pi_k}^i, B_k) 
ight]$$
    where $S_{\pi_k}^i$ is the set of units preceding $i$ in permutation $\pi_k$ [1023, 1029].
3.  **Noise-Gated Truncation**: Terminate the evaluation of a permutation prefix chain early if the running prefix score matches the grand coalition score within a pre-registered noise threshold, saving computational resources [1023].
