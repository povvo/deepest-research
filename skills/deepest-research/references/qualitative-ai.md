# 3. Qualitative Research with AI Checklist

> **Runtime use condition:** Read when AI assists transcript processing, coding, thematic analysis, or qualitative synthesis.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.

This deep-treatment checklist provides social science and qualitative researchers with a rigorous operational pipeline for transcription, coding, and thematic analysis using Large Language Models, standardizing workflows under the **LATA framework** (Languages, Algorithms, Taxonomy, and Annotations) [472, 630, 631].

## Section 1: Raw Transcript Processing & Viewpoint Extraction
- [ ] **Boilerplate and OCR Error Cleaning**: Clean raw transcripts of verbal fillers, transcription artifacts, and OCR errors while maintaining original semantic meaning [50, 507, 659].
- [ ] **Granular Viewpoint Decomposition**: Ingest raw transcripts sentence-by-sentence and extract semantically independent, granular "viewpoints" (ideas, arguments, or facts). Replace pronouns with their referent nouns and complete missing sentence components to ensure the independence of each viewpoint [462, 463, 472].
- [ ] **Anonymization and Sterilization**: Meticulously remove or redact all personally identifiable information (PII) from transcript segments before sending them to third-party APIs or external environments [200, 509].

## Section 2: Deductive Coding with Predefined Codebooks
- [ ] **Predefined Codebook Integration**: Construct a robust JSON-Schema representing the deductive codebook, defining each code category, inclusion criteria, and exemplar snippets [263, 472, 483].
- [ ] **Two-Stage Multi-Prompt Evaluation**:
  - *Stage 1 (Labeling-All)*: Provide the LLM with the list of indexed transcript segments and require it to output a complete JSON mapping of `(segment_id, code_label, explanation)` [206].
  - *Stage 2 (Select-Deficient)*: Run a validation agent to selectively parse only the segments tagged under a specific category, outputting tuples of `(segment_id, justification)` to ensure deep reasoning alignment [206, 210].
- [ ] **Semantic Equivalence Alignment**: Use an LLM-based semantic evaluator (e.g., GPT-4o) to check whether the LLM's applied codes match human-assigned definitions, mapping diverse word choices to canonical aliases [259, 260].

## Section 3: Inductive Theme Generation & Taxonomy Merging
- [ ] **Local Concept Graph Construction**: Map relations between disjoint concepts in transcripts using triple formats (concept-relation-concept) [150, 197].
- [ ] **Parallel Taxonomy Expansion (FLMSCI)**: Group transcript topic chunks, compile a "seed taxonomy", and run parallel LLM threads to incrementally insert new concepts, optimizing for logical hierarchy and appropriate levels of abstraction [588, 589].
- [ ] **Taxonomy Edge Mapping Heuristics**: Direct the model to prioritize hierarchical transitions using three main actions:
  - `go_down`: If the new concept is a specific subtype of an existing category [590].
  - `make_parent`: If multiple existing concepts can be grouped under a new, broader category [590].
  - `add_sibling`: Only if the concept is fundamentally distinct from existing nodes [590].
- [ ] **Iterative Batch-Based Refinement**: Run multiple iterations of paper selection and schema refinement (e.g., 5 randomized batches) to continuously merge similar themes, resolve Composition conflicts, and re-verify cell contents [550, 557, 558, 559].
