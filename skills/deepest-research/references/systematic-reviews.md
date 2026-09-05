# 2. Systematic Reviews and Evidence Synthesis Checklist

> **Runtime use condition:** Read when planning a systematic, scoping, rapid, or living review and AI-assisted screening or extraction.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.

This checklist establishes the standards for employing AI as a systematic screening, extraction, and synthesis copilot, ensuring strict compliance with the **RAISE guidelines** and **PRISMA-trAIce** reporting frameworks [134, 136, 636, 637].

## Section 1: Literature Search & Screening Planning
- [ ] **API Retrieval Constraints**: Utilize academic APIs (e.g., Semantic Scholar, PubMed) to retrieve relevant target publications using query strings generated dynamically from research abstracts or keyword lists [134, 310, 395].
- [ ] **Temporal Boundary Controls**: Restrict search query publication dates strictly before or after specific cutoffs to control the visibility of literature and prevent temporal data contamination during evaluation [102, 105, 237].
- [ ] **SPECTER Semantic Filtering (Stage 1)**: Embed retrieved candidates using a dense transformer model (e.g., SPECTER or Sentence-T5) and rank by cosine similarity against the target abstract to isolate the top-100 most relevant candidates [294, 320, 554, 562].
- [ ] **RankGPT Contextual Re-ranking (Stage 2)**: Apply a listwise re-ranking prompt using RankGPT to narrow the top-100 candidates down to the top-10, sorting specifically by decreasing facet overlap (Purpose, Mechanism, Evaluation) [295, 320, 321].

## Section 2: Rigorous Data Extraction
- [ ] **Source-Grounded Extraction Rules**: Enforce strict extraction guidelines: instruct the LLM to only output values objectively supported by the text, and return a structured JSON dictionary containing both the extracted `answer` and the `excerpts` (exact, verbatim text spans) [369, 492].
- [ ] **YAML Schema Synthesis**: Standardize extraction templates by requiring models to populate strict YAML structures representing technical parameters, material properties, or error-correction thresholds [493].
- [ ] **No-Context Validation Queries**: To prevent model hallucinations or reliance on prior parametric knowledge, run separate validation queries on isolated paragraphs where the context is hidden, forcing the model to reply based solely on the immediate text chunk [292, 370].

## Section 3: Verification & Reporting (PRISMA-trAIce)
- [ ] **Abstract/Intro Claim Verification**: Check if the paper's actual results support the claims made in its abstract and introduction, assessing the generalizability and limitations of the work [540].
- [ ] **NeurIPS Checklist Style Verification**: Implement a closed-ended validation protocol. For every "Yes" answer on the review checklist, run an LLM-as-a-judge agent on the target section to verify that the authors actually completed the requirements (e.g., code URLs, dataset licenses, and compute estimates) [68, 71, 73, 541].
- [ ] **Human-in-the-Loop Consensus Verification**: Conduct pilot screenings where at least two domain-expert scientists independently cross-check the LLM's classification accuracy and establish a ground-truth calibration dataset [245, 255].
- [ ] **Watermarking & Disclosure Transparency**: Embed explicit disclosures in all generated synthesis reports, outlining exactly which sections were AI-assisted and verifying that no fabricated experimental metrics were injected during synthesis [385, 391, 392].
