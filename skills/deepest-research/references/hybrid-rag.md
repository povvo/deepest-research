# Operational Reference: Structure-Aware Hybrid RAG

> **Runtime use condition:** Read when designing structure-aware retrieval, claim extraction, table filling, or source-grounding workflows.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.



## Contents

1. 1. Executive Summary & Purpose
2. 2. Core Algorithmic Workflow
3. 3. Production-Ready Prompt Templates [28, 29, 388]

## 1. Executive Summary & Purpose
**Structure-Aware Hybrid RAG** is the second stage of the **Text-KG-Table (TKGT)** pipeline [2, 6, 9]. Standard Retrieval-Augmented Generation (RAG) models retrieve unstructured text chunks based purely on embedding cosine similarity [24, 407]. However, for multi-entity, high-dimensional tabular extraction tasks, vanilla RAG fails to capture the precise data dependencies and spatial-temporal relationships between adjacent attributes, leading to incomplete or mismatched tables [12, 407]. Hybrid RAG resolves this by using the uninstantiated **Slack Knowledge Graphs (KGs)** generated in the first stage to dynamically rewrite queries, schedule retrieval priorities, and iteratively fill empty data labels [6, 9, 13, 14, 15].

---

## 2. Core Algorithmic Workflow
Hybrid RAG implements a formal **KG Object Label Filling Algorithm** and query-rewriting pipeline [14, 15]:

```
  ┌────────────────────────────────────────────────────────────┐
  │               1. INITIALIZE EMPTY KG OBJECT                │
  │ - Load empty Slack Classes (Entities & Relations)          │
  └──────────────────────────────┬─────────────────────────────┘
                                 │ While labels are empty
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 2. PRIORITY ENTITY SELECTION               │
  │ - If first run: select entity with highest centrality      │
  │ - Else: select entity with highest ratio of unfilled labels│
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                3. DYNAMIC QUERY REWRITING                  │
  │ - Rewrite query using adjacent entity values as context    │
  │ - Execute hybrid retriever (sparse BM25 + dense embedding) │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                  4. EXCERPT VALUE EXTRACTION               │
  │ - Prompt LLM to extract value + exact textual excerpts     │
  │ - If found: fill label. Else: fill "Bad Information"       │
  └────────────────────────────────────────────────────────────┘
```

### 2.1 The KG Object Label Filling Algorithm [14, 15]
```
Input: Uninstantiated KG Classes G_classes, Target Text Documents D
Output: Fully Instantiated Tabular Database T

1: Initialize an empty KG object
2: while the KG object contains empty labels do
3:     if no entity in KG has filled labels then
4:         Select the entity with highest centrality
5:     else
6:         Calculate the ratio: Count(Label|Unfilled) / Count(Label) for each entity
7:         Select the entity with the highest ratio of unfilled labels
8:     end if
9:     if the selected entity's name label is not filled then
10:        Search and extract the entity name
11:    else
12:        Randomly select one unfilled label
13:        Search and extract information for the unfilled label using Dynamic Query Rewriting
14:    end if
15:    if the information is found in retrieved documents then
16:        Fill the searched information to the label
17:    else
18:        Fill "Bad Information" to the label (ensures no infinite loops)
19:    end if
20: end while
```

### 2.2 Dynamic Query Rewriting [15, 16]
To retrieve precise cell values, the system does not query the database using the raw question. Instead, a query-rewriting model dynamically reformulates the query by prepending the known, already-filled values of adjacent entities [15, 16].
- **Example**: If extracting "interest rate" for "Lender A" who is linked to "Borrower B (John Doe)", the query is rewritten as: `"Search for the interest rate specified in the agreement between John Doe and Lender A"` [15, 16].

### 2.3 Excerpt-Grounded Value Extraction [28, 388]
To completely eliminate hallucinated extraction, the extraction prompt forces the model to output two components [28, 388]:
1. **Value**: The specific, canonicalized data cell value.
2. **Excerpts**: A list of one or more *exact, byte-identity* text spans extracted from the paper that support the value [388]. If no direct excerpt exists, the model must return `"Bad Information"` [15, 18, 28].

---

## 3. Production-Ready Prompt Templates [28, 29, 388]

### Template A: Dynamic Query Rewriter [16]
```markdown
[System Message]
You are a Query Rewriter. Your goal is to generate a highly specific, URL-encoded search query for academic or database retrieval by utilizing adjacent entity-attribute connections.

[User Message]
Target Entity: {target_entity}
Target Attribute to Extract: {target_attribute}
Adjacent Entity Values (Context): {adjacent_context}

Generate a concise search query (maximum 6 words) focused strictly on locating this relationship. Output ONLY the query.
```

### Template B: Excerpt-Grounded Information Extraction [28, 29, 388]
```markdown
[System Message]
You are a precise Information Extraction assistant. Your objective is to extract the value of the specified attribute for the given role.
Rules:
1. Only provide values that are objectively supported by the provided Text.
2. You MUST return a JSON object containing the 'answer' and a list of 'excerpts' containing the EXACT text spans from the text.
3. If the text does not contain the answer, return an empty dictionary '{}'. Do not guess or substitute.

[User Message]
Text:
"""
{retrieved_document_text}
"""

Task:
Role: {selected_entity_role}
Attribute: {selected_attribute}
Value Scope: {attribute_value_scope}

Extract the value. Output format:
{{
  "answer": "Concise extracted value",
  "excerpts": ["Exact supporting text span 1", "Exact supporting text span 2"]
}}
```
