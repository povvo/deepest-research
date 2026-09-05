# Operational Reference: Recursive Literature Ranking Loop

> **Runtime use condition:** Read when implementing recursive literature retrieval, reranking, deduplication, query revision, or overlap analysis.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.



## Contents

1. 1. Executive Summary & Purpose
2. 2. Multi-Stage Operational Workflow
3. 3. Production-Ready Prompt Templates [352, 354]

## 1. Executive Summary & Purpose
The **Recursive Literature Ranking Loop** is a single-agent search and refinement pipeline designed to ground research generation, prevent topic drift, and identify candidate literature overlapping with proposed scientific ideas [265, 332, 400]. Standard retrieval pipelines query search databases once using raw topic descriptions, yielding generic or marginally relevant results [364]. This pipeline implements a recursive loop: it summarizes proposed concepts, generates structured query lists, retrieves papers from academic APIs (such as Semantic Scholar or PubMed), and runs a two-stage re-ranking process combining **SPECTER embedding filtering** with **RankGPT list-wise re-ranking** [265, 339, 340]. It then uses a strict deduplication check to eliminate redundant ideas and continuously updates its local knowledge index [267, 367].

---

## 2. Multi-Stage Operational Workflow
The recursive loop coordinates the following execution stages [265, 339, 340, 350]:

```
  ┌────────────────────────────────────────────────────────────┐
  │                 1. KEYWORD EXTRACTION & SEARCH             │
  │ - Extract 3-6 specific keyword phrases from idea           │
  │ - Query Semantic Scholar/PubMed APIs recursively           │
  └──────────────────────────────┬─────────────────────────────┘
                                 │ Target: N = 120 papers
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │              2. STAGE 1: SPECTER EMBEDDING FILTER          │
  │ - Calculate cosine similarity between idea & candidate abstracts│
  │ - Select Top-100 candidate papers                          │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                3. STAGE 2: RankGPT RE-RANKING              │
  │ - Rank candidates based on multi-facet overlap hierarchy   │
  │ - Select Top-10 overlapping papers for assessment          │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │                4. DEDUPLICATION & INTEGRATION              │
  │ - Deduplicate seed ideas using Sentence-Transformers (η=0.8)│
  │ - Summarize selected papers and update local index         │
  └────────────────────────────────────────────────────────────┘
```

### 2.1 Keyword Extraction & Retrieval Action Space [265, 352]
The agent analyzes the proposed idea and extracts 3–6 highly specific keyword phrases (3–6 words each) representing the *purpose, mechanism, and application domain* (avoiding broad terms like "machine learning") [352]. It generates a sequence of API calls [265]:
- `KeywordQuery(keywords)`
- `PaperQuery(paperId)`
- `GetReferences(paperId)`

The agent retrieves up to a maximum of $N = 120$ papers, iteratively shortening search terms if results are thin [265, 335].

### 2.2 Two-Stage Re-ranking [339, 340, 354]
- **Stage 1 (Semantic Filtering)**: Candidate abstracts and the target idea are encoded using SPECTER embeddings [339]. The retriever ranks all candidates by cosine similarity, selecting the top-100 most similar papers [339].
- **Stage 2 (Faceted Re-ranking)**: To locate exact conceptual overlaps, RankGPT ranks the top-100 papers list-wise [340, 354]. It prioritizes papers based on a strict multi-facet hierarchy [340, 354]:
  1. *Score Level 1*: Matches all core facets (Domain + Purpose + Mechanism + Evaluation) [340, 354].
  2. *Score Level 2*: Matches Domain + Purpose but differs in Mechanism [354].
  3. *Score Level 3*: Shares Purpose or Mechanism or Evaluation across domains [354].
  4. *Score Level 4*: Partially matches domain or addresses related topics [354].
  The top-10 ranked papers proceed to the novelty evaluation stage [340].

### 2.3 Semantic Deduplication Check [267]
To prevent model-drift and redundant generations, all proposed seed ideas are compared against previously generated ideas and retrieved abstracts [267]. Ideas are encoded using Sentence-Transformers (`all-MiniLM-L6-v2`) and checked for pairwise cosine similarity [267]. Any idea with similarity exceeding $\gamma = 0.8$ is flagged as a duplicate and discarded [267, 276].

---

## 3. Production-Ready Prompt Templates [352, 354]

### Template A: Keyword Extraction Prompt [352]
```markdown
[System Message]
You are a precise Keyword Extractor. Your task is to analyze the provided research idea and extract 3-6 highly specific keyword phrases (3-6 words each) and compile 4 concise research titles (<= 5 words).
Constraints: Keywords must be specific, capture what sets the idea apart, and reflect the purpose, mechanism, and application domain.

[User Message]
Research Idea: {proposed_research_id}

Format your output exactly as a JSON object:
{
  "keywords": ["keyword phrase 1", "keyword phrase 2", "keyword phrase 3"],
  "suggested_titles": ["Title 1", "Title 2", "Title 3", "Title 4"]
}
```

### Template B: RankGPT Facet-Based Re-ranking Prompt [354]
```markdown
[System Message]
You are RankGPT, an expert scientific citation ranker. Your task is to rank the provided candidate papers based on their multi-facet relevance to the target research idea.
Ranking Priority Hierarchy:
1. Candidate matches ALL key facets (Domain + Purpose + Mechanism + Evaluation).
2. Candidate matches Domain + Purpose but differs in Mechanism.
3. Candidate shares Purpose, Mechanism, or Evaluation across different domains.
4. Candidate matches Domain only or addresses a marginally related topic.

[User Message]
Target Research Idea Facets:
- Application Domain: {target_domain}
- Purpose/Objective: {target_purpose}
- Mechanism/Method: {target_mechanism}
- Evaluation Metric: {target_evaluation}

List of Candidate Papers:
{candidate_papers_list}

Order the candidate papers from most relevant (most overlapping) to least relevant. Format your output strictly as a sorted index list (e.g., [3] > [1] > [5] > [2]). Output ONLY the ranking sequence.
```
