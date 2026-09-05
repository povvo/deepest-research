# Supplied Scientific Provenance Map

## Contents

- [Read This Reference When](#read-this-reference-when)
- [Provenance Status](#provenance-status)
- [Core Alignment and Operational Gating Frameworks](#i-core-alignment--operational-gating-frameworks)
- [Advanced Research, Codebase Search, and Simulation Playbooks](#ii-advanced-research-codebase-search-and-simulation-playbooks)
- [Document-Type Optimization and Compilation Guides](#iii-document-type-optimization--compilation-guides)
- [Retrieval, Extraction, and Grounding Infrastructure](#iv-retrieval-extraction--grounding-infrastructure)
- [Methodological and Domain-Specific Modules](#v-methodological--domain-specific-modules)
- [Evaluation, Verification, and Reliability](#vi-evaluation-verification--reliability)
- [Agentic Orchestration and Research Intelligence](#vii-agentic-orchestration--research-intelligence)
- [Closing Synthesis](#closing-synthesis)

## Read This Reference When

Read this file when tracing any retained component to the scientific sources and architectural rationale supplied by the researcher. Use it for provenance discovery; inspect the cited paper or official implementation before changing an implementation-critical equation, model, threshold, dataset, or evaluation claim.

## Provenance Status

This map is supplied project knowledge. Its numbered source tokens are preserved as internal project locators rather than treated as automatically resolved user-facing citations. The component rationales establish design intent; `references/source-grounding.md` defines how to turn that intent into an executable contract.

---

### The Scientific Blueprint: Comprehensive Ingestion, Grounding, and Rationale Log

### I. Core Alignment & Operational Gating Frameworks

#### 1\. meta-prompt-compiler.md

* **Grounded Scientific Sources**:  
* *"Principle-Driven Self-Alignment of Language Models from Scratch with Minimal Human Supervision"* 1, 2  
* *"Solving Quantitative Reasoning Problems with Language Models"* 3, 4  
* *"Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing"* 5-7  
* **Architectural Operational Rationale**: Created to serve as a **meta-compiler and parser** for agent skills. Basic prompting fails to preserve structural constraints over long contexts. This compiler uses **spatial attention zoning** (Primacy, Middle, and Recency Zones) to maximize model focus and enforces **progressive disclosure** by partitioning complex prompts into distinct files (references/ and assets/), ensuring that downstream reasoning agents do not suffer from context-window degradation or attention drift.

#### 2\. knowledge-boundary-prompting.md

* **Grounded Scientific Sources**:  
* *"Know What You Don’t Know: Unanswerable Questions for SQuAD"* 8, 9  
* *"True Few-Shot Learning with Language Models"* 10  
* *"Siren’s Song in the AI Ocean: A Survey on Hallucination in Large Language Models"* 11, 12  
* **Architectural Operational Rationale**: Engineered to address the critical failure of **hallucinated out-of-distribution (OOD) knowledge**. By structuring a 3-step validation pipeline—comprising self-evaluation, explicit knowledge-boundary refusal mapping, and calibrated uncertainty expressions—this file forces the agent to explicitly state its epistemic limits and refuse queries rather than generating speculative answers when requested details are missing from pre-trained parameters or retrieved chunks.

#### 3\. principle-driven-gating.md

* **Grounded Scientific Sources**:  
* *"Principle-Driven Self-Alignment of Language Models from Scratch with Minimal Human Supervision"* 1, 2  
* *"Constitutional AI: Harmlessness from AI Feedback"* 13-15  
* **Architectural Operational Rationale**: Replaces subjective alignment metrics with invariant physical and logical laws (e.g., *Conservation of Energy, Variable Isolation, Statistical Power*). Subjective system rules allow models to easily slip into sycophancy or formatting-only compliance. By setting up a rigid **Principles Audit Engine** alongside a **Gradio UI schema**, this file ensures that proposed research steps must strictly satisfy scientific principles before entering the execution queue.

#### 4\. topic-guided-augmentation.md

* **Grounded Scientific Sources**:  
* *"LiveIdeaBench: Evaluating LLMs’ Divergent Thinking for Scientific Idea"* 16  
* *"Using Large Language Models for Idea Generation in Innovation"* 17, 18  
* **Architectural Operational Rationale**: Developed to combat the **homogenization and semantic clustering** that occurs when language models generate scientific ideas. Left unconstrained, models repetitively output incremental variations of their seed prompts. This playbook uses pairwise **ROUGE-L similarity gates** and **single-keyword stimulus prompts** to force the model to generate highly divergent, interdisciplinary, and non-redundant research hypotheses.

### II. Advanced Research, Codebase Search, and Simulation Playbooks

#### 5\. research-playbook-codebase-analysis.md

* **Grounded Scientific Sources**:  
* *"ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code"* 19  
* *"Sci-Reproducer: Automated Algorithm Understanding and Code Replication"* 20  
* **Architectural Operational Rationale**: Standardizes how an agent analyzes, maps, and comprehends complex, multi-file software repositories. It establishes the **Paper Agent** and **Code Agent** dual-loop architecture to translate mathematical LaTeX specifications into fully functional, local implementations, utilizing **Reasoning Graphs** (directed acyclic graphs of algorithmic steps) to ensure alignment between theory and code.

#### 6\. research-playbook-code-space-search.md

* **Grounded Scientific Sources**:  
* *"AIDE: ai-driven exploration in the space of code"* 19, 21  
* *"MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation"* 22-25  
* **Architectural Operational Rationale**: Machine learning and algorithmic engineering are highly non-linear, stateful development tasks. Rather than attempting all-at-once code generation, this playbook models coding as an **iterative tree-search in code-space**. It defines mutually exclusive states—Drafting, Debugging, and Improving (where only *one* atomic modification is tested at a time)—and integrates a **Summarization Operator** to compress previous execution history, preventing token overflow.

#### 7\. research-spec-skill-valuation.md

* **Grounded Scientific Sources**:  
* *"Skillopt: Executive strategy for self-evolving agent skills"* 26  
* *"Trace2skill: Distill trajectory-local lessons into transferable agent skills"* 26  
* **Architectural Operational Rationale**: Formulates **SkillSV (Skill Shapley Valuation)** to programmatically calculate the mathematical contribution and utility of individual prompt instructions, system cards, or tools. It isolates an instruction's *Content Value* from its *Context-Occupancy Cost* using dual counterfactual rendering operators (Deconstructive Deletion and Neutral Padding), providing a clear mathematical guide to prune bloated, redundant agent instructions.

### III. Document-Type Optimization & Compilation Guides

#### 8\. latex-compilation.md

* **Grounded Scientific Sources**:  
* *"CycleResearcher: Improving Automated Research via Automated Review"* 27-29  
* *"Paper2Code: Automating Code Generation from Scientific Papers in Machine Learning"* 30, 31  
* **Architectural Operational Rationale**: Created to automate the formatting, macro-resolution, and compiling of publication-ready scientific manuscripts. It establishes the **Iterative Resampling Backtracking** debugging loop—which systematically scales backward from the compiler .log error line using a sliding line formula—to automatically resolve unescaped characters, missing brackets, or TikZ visualization errors on the fly.

#### 9\. notebook-engineering.md

* **Grounded Scientific Sources**:  
* *"A large-scale study about quality and reproducibility of Jupyter notebooks"* 32  
* *"Natural language to code generation in interactive data science notebooks"* 33, 34  
* **Architectural Operational Rationale**: Standardizes how agents interact with, modify, and verify interactive computational notebooks (.ipynb). Unlike static scripts, notebooks maintain live execution states across non-sequential cells. This playbook details state tracking, cell-dependency tree parsing, and **fuzzy output canonicalization** to reliably assess code execution accuracy without relying on fragile literal assertions.

#### 10\. pdf-ingestion.md

* **Grounded Scientific Sources**:  
* *"Galactica: A Large Language Model for Science"* 35, 36  
* *"S2ORC: The Semantic Scholar Open Research Corpus"* 37  
* **Architectural Operational Rationale**: Details the multi-stage ingestion pipeline required to parse unstructured PDF layouts into structured, machine-readable formats. It synthesizes rules for **GROBID bibliographic mapping**, **Nougat mathematical OCR translation**, and **SciPDF reference citation extraction** to convert visual documents into clean Markdown contexts while enforcing strict "NaN" handling for missing variables.

#### 11\. LLM Mindmap

* **Grounded Scientific Sources**:  
* *"Mindmap: Knowledge graph prompting sparks graph of thoughts in large language models"* 38  
* *"Graph of thoughts: Solving elaborate problems with large language models"* 39  
* **Architectural Operational Rationale**: Designed to provide a visual, structured overview of all the interdisciplinary AI concepts explored during your research. It maps the complex associations and dependencies between different training and evaluation methodologies to give the user a clear, intuitive map of the system's conceptual terrain.

### IV. Highly Granular Ingestion, Mapping, and Validation Playbooks

#### 12\. mixed-ie.md

* **Grounded Scientific Sources**:  
* *"Text-to-table: A new way of information extraction"* 40  
* *"Text-tuple-table: Towards information integration in text-to-table generation via global tuple extraction"* 41  
* **Architectural Operational Rationale**: Standardizes **Stage 1 (Mixed-IE)** of text-to-table extraction. It uses bilingual tokenization, POS tagging, and NER filtering to parse raw texts into empty **"Slack Classes"** representing uninstantiated entities, attributes, and relationships. Extracting this structural graph skeleton *prior* to data-cell retrieval prevents schema formatting errors and eliminates the high information loss common in one-shot table extraction.

#### 13\. hybrid-rag.md

* **Grounded Scientific Sources**:  
* *"Table meets llm: Can large language models understand structured table data?"* 42, 43  
* *"gtbls: Generating tables from text by conditional question answering"* 42-44  
* **Architectural Operational Rationale**: Establishes **Stage 2 (Hybrid-RAG)** of structured data extraction. It details the **KG Object Label Filling Algorithm**, which iteratively tracks empty attributes in the schema, rewrites prompts using adjacent entity values to narrow the search, and retrieves cell values backed exclusively by exact, byte-identity textual excerpts to prevent hallucinations.

#### 14\. self-consistency.md

* **Grounded Scientific Sources**:  
* *"Self-Consistency Improves Chain of Thought Reasoning in Language Models"* 45-47  
* *"Solving Quantitative Reasoning Problems with Language Models"* 3, 4, 48  
* **Architectural Operational Rationale**: Codifies the mathematical optimization of reasoning paths. Instead of relying on greedy decoding (which often fails on complex math), it samples \\\\(N \\ge 10\\\\) independent paths using temperature scaling, constructs a **"Resonance Graph"** (where nodes are solutions and edges are SBERT cosine similarities), and computes network centrality to output the mathematically optimal, highly calibrated consensus answer.

#### 15\. machine-symbiosis.md

* **Grounded Scientific Sources**:  
* *"Show Your Work: Scratchpads for Intermediate Computation with Language Models"* 49-52  
* *"ReAct: Synergizing Reasoning and Acting in Language Models"* 34, 53-60  
* **Architectural Operational Rationale**: Sets up the **Pre-Commitment Verification contract** that bridges the model's textual outputs with deterministic code execution environments. To block the model from declaring unverified progress, it mandates that any claim can only enter the agent's active memory state if a prediction committed to a log *prior* to acting matches the raw terminal stdout after running the script.

#### 16\. literature-ranking-recursive-loop.md

* **Grounded Scientific Sources**:  
* *"Zero-shot listwise document reranking with a large language model"* 61  
* *"Rankzephyr: Effective and Robust Zeroshot Listwise Reranking Is a Breeze\!"* 62  
* **Architectural Operational Rationale**: Establishes a highly controlled, single-agent literature discovery loop. It extracts purpose, mechanism, and domain keywords from a target idea, queries academic databases using API commands (GetReferences, KeywordQuery), uses **SPECTER embeddings** to filter the candidate pool to the top-100, and executes a list-wise **RankGPT re-ranking** to identify the top-10 papers while pruning duplicates using an all-MiniLM-L6-v2 cosine gate.

### V. Executable Python Validation Tools & Bash Orchestrator

#### 17\. tool-literature-explorer.py

* **Grounded Scientific Sources**:  
* *"LitSearch: A Retrieval Benchmark for Scientific Literature Search"* 63  
* *"S2ORC: The Semantic Scholar Open Research Corpus"* 37  
* **Architectural Operational Rationale**: A concrete, zero-dependency Python script created to execute the discovery loops defined in literature-ranking-recursive-loop.md. It queries the public arXiv database via Atom XML, parses metadata, and applies a list-wise keyword frequency score to filter and output a clean bibliography without requiring external APIs or API keys.

#### 18\. tool-mixed-ie-parser.py

* **Grounded Scientific Sources**:  
* *"Text-to-table: A new way of information extraction"* 40  
* *"Text-tuple-table: Towards information integration in text-to-table generation via global tuple extraction"* 41  
* **Architectural Operational Rationale**: An AST-based repository code analyzer and entity-relationship extraction script. It parses local files and text corpora on the fly to construct semantic relation graphs of your active workspace concepts, serving as the active pipeline engine for the Mixed-IE stage.

#### 19\. tool-hybrid-rag-verifier.py

* **Grounded Scientific Sources**:  
* *"Arxivdigestables: Synthesizing Scientific Literature into Tables Using Language Models"* 64  
* *"Attributed Text Generation via Post-Hoc Research and Revision"* 65, 66  
* **Architectural Operational Rationale**: An executable verifier that performs character-by-character exact substring scans over source text to check the validity of generated tables. It outputs starting and ending byte offsets to prove that extracted data cells are grounded, automatically replacing ungrounded cells with "N/A" to prevent fabricated metrics.

#### 20\. tool-self-consistency-voting.py

* **Grounded Scientific Sources**:  
* *"Self-Consistency Improves Chain of Thought Reasoning in Language Models"* 45-47  
* **Architectural Operational Rationale**: Implements the mathematical consensus voting model. It processes a JSON array of stochastic reasoning pathways, constructs a Jaccard similarity resonance matrix, and selects the solution that exhibits the highest structural consensus.

#### 21\. tool-curie-rigor-monitor.py

* **Grounded Scientific Sources**:  
* *"Curie: Toward Rigorous and Automated Scientific Experimentation with AI Agents"* 67-69  
* **Architectural Operational Rationale**: An automated code auditor that enforces the *Curie Rigor Engine*. It parses Python files to detect and block unseeded random blocks, hardcoded accuracy metrics, or mock mock generators, compiling a clean **Variable Isolation Map** to verify that control variables are strictly isolated.

#### 22\. execute-research-pipeline.sh

* **Grounded Scientific Sources**:  
* *"Building Applied Natural Language Generation Systems"* 70  
* *"Toolformer: Language Models Can Teach Themselves to Use Tools"* 71-76  
* **Architectural Operational Rationale**: A production-ready bash orchestrator designed to chain all five custom Python tools. It automates the transition of the research workspace from paper crawling to parsing, exact-match validation, consensus voting, and rigor-compliance checkups in a unified, non-interactive shell loop.

#### 23\. scan.py

* **Grounded Scientific Sources**:  
* *"The Pile: An 800GB Dataset of Diverse Text for Language Modeling"* 77  
* *"Deduplicating Training Data Makes Language Models Better"* 78  
* *"Documenting the English Colossal Clean Crawled Corpus"* 79  
* **Architectural Operational Rationale**: An executable OSINT scraper designed to ingest public web text. It applies a **minimum karma gate (\\\\(\\ge 3\\\\))** as an objective popularity heuristic and runs a sliding **n-gram repetition filter** to reject boilerplates and automated spam before merging findings into the local index.

#### 24\. hypothetically\_popular.py

* **Grounded Scientific Sources**:  
* *"The Language That Drives Engagement: A Systematic Large-Scale Analysis of Headline Experiments"* 80  
* *"The Upworthy Research Archive, a Time Series of 32,487 Experiments in U.S. Media"* 81  
* **Architectural Operational Rationale**: Analyzes text attributes (word count, urgent terminology, CTAs, specific numbers, KOL mentions) to predict social media virality. It compares two post variations covering identical scientific facts and predicts the higher-engagement wording, formatting its decision strictly as the first tweet or the second tweet to allow automated agent scheduling.

#### 25\. probability\_curvature.py

* **Grounded Scientific Sources**:  
* *"Fast-detectgpt: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature"* 82  
* **Architectural Operational Rationale**: An executable zero-shot text classifier that evaluates whether a scientific or social submission is human-written or synthetic. It applies random semantic perturbations, measures the log-probability curvature difference, and utilizes a mathematical threshold (\\\\(\\epsilon \= 0.50\\\\)) to classify text without requiring training data or model weights.

#### 26\. hierarchography.py

* **Grounded Scientific Sources**:  
* *"Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM"* 25, 83  
* *"Surveyforge: On the Outline Heuristics, Memory-Driven Generation, and Multi-Dimensional Evaluation for Automated Survey Writing"* 84  
* **Architectural Operational Rationale**: An active Python engine that groups unstructured scientific data. It executes the **SCYCHIC (Clustered Taxonomy Induction)** algorithm, performing top-down KMeans partitioning over TF-IDF vectors, followed by a bottom-up summarization to output structured nested JSON hierarchies and clean Markdown reports.

#### 27\. byte-Identity.py

* **Grounded Scientific Sources**:  
* *"Arxivdigestables: Synthesizing Scientific Literature into Tables Using Language Models"* 64  
* *"Schema-driven information extraction from heterogeneous tables"* 85  
* **Architectural Operational Rationale**: The executable cell-level grounding validator designed to implement **DIGESTables** standards. It verifies every field in a generated table against original background papers using character-matching offsets, and automatically prunes ungrounded parameters to guarantee complete integrity.

#### 28\. grading-rubric.md

* **Grounded Scientific Sources**:  
* *"Can Large Language Models Provide Useful Feedback on Research Papers? A Large-Scale Empirical Analysis"* 86-92  
* *"G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment"* 93  
* **Architectural Operational Rationale**: Standardizes evaluations for research agent outputs. Subjective scoring of complex scientific work results in uniformly high ratings. This rubric establishes strict 5-point Likert criteria across Novelty, Feasibility, and Significance, and integrates **sub-tree pruning** to evaluate taxonomy nodes efficiently without wasting token costs.

### VI. Multi-Domain Prompt Packages & Specialized Guides

#### 29\. deep-research-prompt-pack.md

* **Grounded Scientific Sources**:  
* *"Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing"* 5-7  
* *"Principles of Research Design: Qualitative, Quantitative, and Mixed Methods Approaches"* 94  
* **Architectural Operational Rationale**: A modular library containing task-specific, validated prompt templates designed to adapt the Deep Research Planner across three distinct scientific domains: **Engineering** (focusing on materials chemistry and DFT parameters), **Marketing** (addressing behavioral segmentation and decision-heuristics), and **Operations** (solving mathematical linear programming models).

#### 30\. deep-research-planner-skill-v2.md

* **Grounded Scientific Sources**:  
* *"Moose: Multi-Module Framework for Open-Domain Hypothesis Generation"* 95-97  
* *"Curie: Toward Rigorous and Automated Scientific Experimentation with AI Agents"* 67-69  
* **Architectural Operational Rationale**: The primary, executable skill specification (playbook) orchestrating the complete Deep Research Planner workflow. It unifies all 5 strategic steps—Intake, Pathfinding, Debate, Verification, and Scaffolding—into an interactive, human-in-the-loop co-creation environment with a strict progress-validation contract.

#### 31\. references-research-architectures-v2.md

* **Grounded Scientific Sources**:  
* *"SciAgents: Automating scientific discovery through multi-agent intelligent graph reasoning"* 17, 68, 98-101  
* *"Nova: An iterative planning and search approach to enhance novelty and diversity of LLM generated ideas"* 102-105  
* *"CycleResearcher: Improving Automated Research via Automated Review"* 27-29  
* **Architectural Operational Rationale**: Houses the decoupled technical and mathematical references of the deep research architectures. It details the randomized Dijkstra pathfinding heuristics, RankGPT re-ranking algorithms, and controllable RL optimization formulas to keep the main skill manifest lean and focused on execution steps.

#### 32\. assets-research-templates-v2.md

* **Grounded Scientific Sources**:  
* *"Text-tuple-table: Towards information integration in text-to-table generation via global tuple extraction"* 41  
* *"SciAgents: Automating scientific discovery through multi-agent intelligent graph reasoning"* 98  
* **Architectural Operational Rationale**: A static repository hosting the exact copy-pasteable JSON schemas, prompt specifications, and questionnaires used by the research agents. This progressive disclosure design prevents the main playbook from becoming bloated with static text blocks.

#### 33\. mixed-ie-preprocessor.py

* **Grounded Scientific Sources**:  
* *"Text-to-table: A new way of information extraction"* 40  
* *"Text-tuple-table: Towards information integration in text-to-table generation via global tuple extraction"* 41  
* **Architectural Operational Rationale**: A programmatic text preprocessor designed to clean raw scientific literature files prior to AST analysis. It handles paragraph segmentation, strips LaTeX syntax comments (%), and formats sections to ensure clean token boundaries for the Mixed-IE parsing tools.

#### 34\. ie-prompt-template.md

* **Grounded Scientific Sources**:  
* *"Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing"* 5-7  
* **Architectural Operational Rationale**: A dedicated prompting asset that defines the exact linguistic instructions and output boundaries required for named entity extraction. It ensures that variables, units, and conditions extracted from raw text conform strictly to schema types without downstream model distortion.

#### 35\. query-rewrite-template.md

* **Grounded Scientific Sources**:  
* *"Table meets llm: Can large language models understand structured table data?"* 42, 43  
* *"gtbls: Generating tables from text by conditional question answering"* 42-44  
* **Architectural Operational Rationale**: Codifies the conditional question-answering query rewriting technique. It contains prompt instructions that teach the retriever agent how to use partially populated table columns to construct highly targeted Semantic Scholar API queries, maximizing information retrieval precision.

#### 36\. lora-fine-tuning.md

* **Grounded Scientific Sources**:  
* *"Lora: Low-rank adaptation of large language models"* 106  
* *"Llamafactory: Unified efficient fine-tuning of 100+ language models"* 40  
* **Architectural Operational Rationale**: Details the parameter-efficient Low-Rank Adaptation (LoRA) fine-tuning procedures required to adapt base language models to scientific and coding datasets. It details rank selection (\\\\(r=8\\\\)), target module mapping, and training hyperparameter schedules to support efficient domain transfer.

#### 37\. nlp-processing-spec.md

* **Grounded Scientific Sources**:  
* *"Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing"* 5-7  
* **Architectural Operational Rationale**: A technical specification document that unifies the prompting paradigms, NLP task definitions, and token evaluation metrics used across all generated files. It defines the system's core linguistic conventions to ensure consistency between reasoning agents.

#### 38\. tkgt-skill.md

* **Grounded Scientific Sources**:  
* *"Text-tuple-table: Towards information integration in text-to-table generation via global tuple extraction"* 41  
* *"Table meets llm: Can large language models understand structured table data?"* 42  
* **Architectural Operational Rationale**: A reusable agent skill card that implements the basic TKGT (Text-to-Knowledge-Graph-to-Table) extraction protocol. It serves as the foundational, non-interactive predecessor to the advanced Deep Research Planner Playbook (v2).

### VII. Research Checklists & Methodological Decision Trees

#### 39\. research-checklist-secondary-data.md

* **Grounded Scientific Sources**:  
* *"The Pile: An 800GB Dataset of Diverse Text for Language Modeling"* 77  
* *"Deduplicating Training Data Makes Language Models Better"* 78  
* **Architectural Operational Rationale**: A detailed checklist that guides social and computational scientists through processing secondary text data. It maps out n-gram deduplication schedules, PII redaction, few-shot sentiment classification, and toxicity/safety scanning to ensure clean dataset curation.

#### 40\. research-checklist-systematic-reviews.md

* **Grounded Scientific Sources**:  
* *"LitSearch: A Retrieval Benchmark for Scientific Literature Search"* 63  
* *"LitLLM: A Toolkit for Scientific Literature Review"* 107, 108  
* **Architectural Operational Rationale**: Details how to execute systematic literature screening and evidence synthesis using AI. It integrates the **RAISE guidelines** and **PRISMA-trAIce** reporting standards with multi-facet re-ranking and strict, citation-grounded extraction rules.

#### 41\. research-checklist-qualitative-ai.md

* **Grounded Scientific Sources**:  
* *"Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM"* 25, 83  
* **Architectural Operational Rationale**: A deep-treatment checklist covering qualitative analysis with AI. It details transcription quality standards, viewpoint decomposition, and deductive coding under the **LATA (Languages, Algorithms, Taxonomy, Annotations) framework**, helping social researchers organize inductive and deductive transcript analysis.

#### 42\. research-checklist-survey-ai.md

* **Grounded Scientific Sources**:  
* *"AI-augmented surveys: Leveraging large language models and surveys for opinion prediction"* 109  
* *"Evaluating Large Language Models in Generating Synthetic HCI Research Data"* 110  
* **Architectural Operational Rationale**: Formulates an active checklist for survey research. It addresses questionnaire design, ReAct-based chatbot interviewing, survey item appraisal, and active fraud detection to counter the **respondent AI-use problem** (where participants complete surveys using automated scripts).

#### 43\. research-checklist-methodology-tools.md

* **Grounded Scientific Sources**:  
* *"A coefficient of agreement for nominal scales"* 111  
* *"Systematic mapping studies in software engineering"* 112  
* **Architectural Operational Rationale**: A unified master tool index. It groups the entire prompt template library, decision trees, and validation calculators into a single reference guide, allowing researchers to quickly find and deploy the optimal validation tool for their specific research design.

### VIII. Task-Specific Validated Prompts

#### 44\. prompt-systematic-screening.md

* **Grounded Scientific Sources**:  
* *"The Life Cycle of Knowledge in Big Language Models: A Survey"* 113  
* **Architectural Operational Rationale**: A Title- and Abstract-Screening prompt based on **Cao et al.** It guides the model through systematic, multi-stage inclusion/exclusion audits during systematic reviews, using active-learning criteria to minimize false negatives.

#### 45\. prompt-thematic-modular.md

* **Grounded Scientific Sources**:  
* *"Scideator: Human-LLM Scientific Idea Generation Grounded in Research-Paper Facet Recombination"* 104, 114  
* **Architectural Operational Rationale**: A five-component modular prompt for reflexive thematic analysis based on **arXiv:2511.14528v1**. It breaks prompts down into Persona, Context, Task, Procedural Constraints, and Output Schema to produce deep, traceable conceptual codes.

#### 46\. prompt-deductive-coding.md

* **Grounded Scientific Sources**:  
* *"Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM"* 25, 83  
* **Architectural Operational Rationale**: Implements deductive qualitative analysis. It takes raw text segments and maps them strictly onto a predefined, structured JSON codebook, enforcing exclusion rules and boundaries to prevent coding overlaps.

#### 47\. prompt-inductive-themes.md

* **Grounded Scientific Sources**:  
* *"Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM"* 25, 83  
* **Architectural Operational Rationale**: Implements inductive qualitative analysis based on grounded theory. It guides the model through line-by-line open coding, constant comparison, and axial theme abstraction, requiring that every generated theme be linked directly to verbatim transcripts.

#### 48\. prompt-survey-appraisal.md

* **Grounded Scientific Sources**:  
* *"AI-augmented surveys: Leveraging large language models and surveys for opinion prediction"* 109  
* **Architectural Operational Rationale**: Evaluates survey questions for psychometric soundness, auditing items across 5 core dimensions: double-barreled questions, leading phrasing, cognitive load, scale mismatch, and social desirability bias.

#### 49\. prompt-json-extraction.md

* **Grounded Scientific Sources**:  
* *"Structured information extraction from complex scientific text with fine-tuned large language models"* 115  
* **Architectural Operational Rationale**: Employs Pydantic-style validation constraints to extract complex, nested data points (scientific, clinical, or geospatial constants) from unstructured academic articles, outputting strict, schema-compliant JSON objects.

#### 50\. prompt-cross-verification.md

* **Grounded Scientific Sources**:  
* *"Can We Automate Scientific Reviewing?"* 116, 117  
* **Architectural Operational Rationale**: Configures a dual-agent adversarial loop where **Agent A (Proposer)** extracts findings, and **Agent B (Examiner)** audits every extracted claim and citation back to original source texts, weeding out hallucinations before delivery.

#### 51\. prompt-causal-elicitation.md

* **Grounded Scientific Sources**:  
* *"Causality: Models, Reasoning and Inference"* 118  
* *"Causal reasoning and large language models: Opening a new frontier for causality"* 119, 120  
* **Architectural Operational Rationale**: Extracts formal causal ordering from raw qualitative descriptions. It applies Pearlian causal frameworks to isolate directed causal pathways, verify temporal precedence, and identify potential confounding variables (\\\\(Z\\\\)).

#### 52\. prompt-dialectical-synthesis.md

* **Grounded Scientific Sources**:  
* *"Argument Mining Driven Analysis of Peer-Reviews"* 121, 122  
* **Architectural Operational Rationale**: Designed to resolve conflicting, inconsistent qualitative findings. It identifies opposing claims (Thesis and Antithesis) across source texts and synthesizes them into a higher-level, context-calibrated conceptual framework (Synthesis).

#### 53\. prompt-boundary-testing.md

* **Grounded Scientific Sources**:  
* *"The logic of scientific discovery"* 123  
* **Architectural Operational Rationale**: Implements a Popperian falsificationist framework. It systematically evaluates generated findings or scientific hypotheses to identify their limits, testing temporal, scale, demographic, and environmental boundaries.

### IX. Methodological Decision Trees

#### 54\. decision-tree-method-selection.md

* **Grounded Scientific Sources**:  
* *"Research Design: Qualitative, Quantitative, and Mixed Methods Approaches"* 94  
* **Architectural Operational Rationale**: A step-by-step decision tree that guides researchers through selecting a Qualitative, Quantitative, or Mixed-Methods pathway based on their core research questions, epistemological stances, and sample scales (\\\\(N\\\\)).

#### 55\. decision-tree-disclosure.md

* **Grounded Scientific Sources**:  
* *"Show Your Work: Improved Reporting of Experimental Results"* 79  
* **Architectural Operational Rationale**: Standardizes reporting and disclosure for papers utilizing generative AI. It maps out exactly what prompts, architectures, model weights, and system logs must be published in a paper's appendix to ensure academic transparency.

#### 56\. decision-tree-tool-selection.md

* **Grounded Scientific Sources**:  
* *"Automating scientific discovery: From equation discovery to autonomous discovery systems"* 124, 125  
* **Architectural Operational Rationale**: Directs the selection of scientific software tools. It links specific analytical tasks (e.g., *structural OCR, bibliographic mapping, symbolic regression, text clustering*) to the optimal open-source libraries (e.g., *Nougat, GROBID, PySR, SCYCHIC*).

#### 57\. decision-tree-ethics.md

* **Grounded Scientific Sources**:  
* *"Ethics of emerging technologies"* 126  
* **Architectural Operational Rationale**: Guides researchers through Institutional Review Board (IRB) ethical navigation. It covers ZDR (Zero-Data-Retention) APIs, de-identification of transcripts, conversational safety, and the ethics of silicon sampling.

### X. Intercoder Agreement & Statistical Calculators

#### 58\. validation-calculator-intercoder.py

* **Grounded Scientific Sources**:  
* *"A coefficient of agreement for nominal scales"* 111  
* **Architectural Operational Rationale**: An executable Python utility that calculates Cohen's Kappa (for 2 coders) and Fleiss' Kappa (for multiple coders) to statistically validate intercoder agreement over categorical coding assignments.

#### 59\. validation-calculator-context-window.py

* **Grounded Scientific Sources**:  
* *"Lost in the middle: How language models use long contexts"* 89  
* **Architectural Operational Rationale**: Computes token usage and configures sliding windows with adjustable overlaps, ensuring that large-scale transcript text files can be processed sequentially without losing contextual theme boundaries.

#### 60\. validation-calculator-sample-size.py

* **Grounded Scientific Sources**:  
* *"Evaluating Large Language Models in Generating Synthetic HCI Research Data"* 110  
* **Architectural Operational Rationale**: Provides the statistical foundation for **silicon sampling validation** (using LLMs as synthetic respondents). It computes the minimum synthetic sample size required based on confidence levels, margins of error, and model-level design effects.

### XI. Codebase Preprocessing Utilities

#### **61\. mixed-ie-preprocessor.py** (Original)

* **Grounded Scientific Sources**:  
* *"Text-to-table: A new way of information extraction"* 40  
* **Architectural Operational Rationale**: Initial, single-module script developed to parse and preprocess academic texts, segmenting files prior to running entity extractions. (Replaced and upgraded by tool-mixed-ie-parser.py).

#### 62\. validation-calculator-repository-parser.py

* **Grounded Scientific Sources**:  
* *"ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code"* 19  
* **Architectural Operational Rationale**: An executable Python utility that performs Abstract Syntax Tree (AST) scanning. It maps local Python files, traces package imports, isolates function signatures, and compiles a clean, structured repository dependency graph to automate code analysis.

### System Integration Summary

By separating static prompts, programmatic calculators, decision trees, and orchestrating shell scripts, this **progressive disclosure layout** ensures that each tool remains atomic, testable, and completely traceable to your scientific sources.  
