# Operational Reference: Mixed Information Extraction (Mixed-IE)

> **Runtime use condition:** Read when extracting structured entities, relations, code symbols, or tabular fields from mixed-format inputs.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


## 1. Executive Summary & Purpose
The **Mixed Information Extraction (Mixed-IE)** pipeline is the foundational ingestion phase of the **Text-KG-Table (TKGT)** framework [2, 6, 9]. Standard information extraction pipelines often attempt to extract final data tables directly from raw, long-form text, resulting in high rates of formatting failure, missing attributes, and context loss [2, 384]. Mixed-IE resolves this by utilizing a two-step domain-aware approach: first, it processes raw documents through combined statistical, rule-based, and deep learning filters to isolate high-value keywords [6, 10, 11]. Second, it abstracts these keywords into a set of uninstantiated **"Slack Classes"** (representing role entities and relational actions) [6, 12, 13, 27]. This uninstantiated ontology acts as a highly structured, domain-specific middleware that guides subsequent RAG and tabularization steps [2, 9].

---

## 2. Core Processing Pipeline
Mixed-IE coordinates three specialized extraction layers [6, 10]:

```
  Unstructured Raw Text
           │
           ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 1. RULE-BASED SEGMENTATION                 │
  │ - Section segmentation, sentence splitting                 │
  │ - Part-of-Speech (POS) tagging & NER                       │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │               2. STATISTICS & KEYWORD FILTER               │
  │ - Compile TF and DF frequency distributions                │
  │ - Identify V-shape distribution boundaries                 │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                  3. SLACK CLASS COMPILATION                │
  │ - Abstract concepts into Entity and Relation classes       │
  │ - Edge connection and ontological mapping                  │
  └────────────────────────────────────────────────────────────┘
```

### 2.1 Rule-Based Segmentation & NLP Tagging
Mixed-IE splits raw, complex text into logical chunks (e.g., using HanLP sentence splitters or NLTK tokenizers) and filters out stop words and grammatical classes that do not carry semantic content [27, 28].
- **English stop tags (stop_pos_en)**: `["CC", "DT", "EX", "IN", "MD", "PDT", "POS", "PRP", "RP", "SYM", "TO", "UH", "WDT", "WP"]` [27, 28]
- **Chinese active tags (used_pos_zh)**: `["NR", "NN", "CD", "VV", "NT", "FW", "AD", "JJ"]` [27, 28]

This filtering isolates core content-carrying words, significantly reducing subsequent LLM token processing costs [7].

### 2.2 Statistics & V-Shape Keyword Filtering [8, 11]
To ensure the completeness of information extraction and minimize semantic losses, the system compiles Term Frequency (TF) and Document Frequency (DF) lists [10, 11]. It calculates the semantic cosine similarity between the filtered vocabulary and a reference set of target fields [8].
- **The V-Shape Phenomenon**: When sorted in descending order of frequency, documents with tabulation potential exhibit a clear V-shape pattern [11]. The first 1% of the front part of the list contains almost all domain-specific high-value keywords (e.g., "interest rate", "guarantor"), while the bottom contains general structural terms [8, 11]. The V-shape's trough represents non-informative connector words [8, 11]. By focusing strictly on the top 1% of the statistical frequency distribution, the pipeline reduces noise and guarantees complete coverage of domain terms [11].

### 2.3 Slack Class Generation [6, 12, 13]
The final step abstracts the filtered keywords into uninstantiated **"Slack Classes"** (representing entities and events) with two core types [13, 27]:
1. **Role Entity Classes**: Abstract representations of actors, materials, or instruments (e.g., "Lender", "Borrower", "Catalyst") [27].
2. **Relation/Action Classes**: Abstract behaviors, transitions, or events requiring multi-party participation (e.g., "Calcination", "Lending behavior", "Repayment") [27].

---

## 3. Production-Ready Prompt Templates [27, 191]

### Template A: Slack Class Ontological Builder Prompt
```markdown
[System Message]
You are a Network Ontology Graph Maker. Your task is to analyze raw scientific or structured text and extract its core domain concepts as uninstantiated "Slack Classes" using category theory.
Do not extract specific data values or instances; focus purely on compiling the abstract classes, attributes, and relationships.

[User Message]
Domain Context Chunk:
```
{raw_context_chunk}
```

Format your output as a structured JSON object adhering exactly to this format:
{
  "role_entities": [
    {
      "class_name": "Unique Name (e.g., Lender, Polymer, Electrode)",
      "attributes": ["attribute_1", "attribute_2"]
    }
  ],
  "relation_actions": [
    {
      "relation_name": "Unique Name (e.g., Repayment, Polymerization)",
      "node_1": "Role Entity Class A",
      "node_2": "Role Entity Class B",
      "governing_properties": ["parameter_1", "parameter_2"]
    }
  ]
}
```
