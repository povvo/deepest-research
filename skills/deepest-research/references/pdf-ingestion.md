# Playbook: Scientific PDF Ingestion, Layout Parsing, and Normalization

> **Runtime use condition:** Read when building a corpus from scholarly PDFs with layout, equation, table, or chunking requirements.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.


Scholarly publications are predominantly distributed as PDF documents [65, 376]. Because PDFs are visual-first vector layouts rather than structured text files, converting them into structured, machine-readable markup for Retrieval-Augmented Generation (RAG) is a critical prerequisite for deep research planning [166, 376].

---

## 1. Advanced Conversion and Parsing Engines
The document intake system employs three complementary parsing architectures depending on the visual and mathematical complexity of the target paper [71, 167, 476]:

### 1.1 GROBID (Bibliographic and Structure Parsing)
For bulk conversion and citation network mapping, the framework utilizes **GROBID** (Genealogy Relation Finder for Document Bibliographies) [71]:
- **Metadata Extraction**: GROBID automatically extracts high-level metadata, including paper title, authors, affiliations, publication date, and abstract [71].
- **Citation Linking**: It maps in-text citation markers (e.g., `\cite{wang2025}`) directly to the bibliography references, linking each bibliography item to its unique Semantic Scholar identifier [307, 317].
- **Structure-Aware Segmentation**: Text is segmented into logical nodes, including sections, subsections, table cells, and caption strings, stripping out headers, footers, and page numbers [71].

### 1.2 Nougat (LaTeX and Math Markup Extraction)
For papers rich in dense mathematical notation, the system routes PDFs through the **Nougat** neural OCR model [167]:
- **Equation Conversion**: Nougat converts raw PDF pixel layouts directly into structured Markdown combined with mathematical LaTeX equations [71, 167]:
  $$\text{PDF Image} \xrightarrow{\text{Nougat}} \text{Markdown + LaTeX Source}$$
- **Blending Normalization**: Markdown is used as the universal representation format to support seamless knowledge blending across disparate document sources [71].

### 1.3 SciPDF Parser (Section and Coreference Resolution)
For entity normalization and deep linguistic analysis, **SciPDF Parser** extracts the raw JSON text outline [476]:
- **Entity Normalization**: Integrates with coreference resolution libraries (e.g., **SciCo** and **ScispaCy**) to replace abbreviations with their fully expanded long-forms [116].
- **Highly Cited Reference Identification**: Computes internal citation density to extract and summarize the 10 most highly cited reference papers mentioned within the target text, ensuring the agent's RAG prompt is focused on the most influential prior works [476].

---

## 2. Text Chunking and Token Budget Management
Once a PDF is parsed into structured Markdown, it must be segmented into indexable chunks to fit within LLM context windows [119, 467]:
- **Chunk Size**: The raw paper text is segmented into overlapping chunks with a mean length of 1,000 tokens [119].
- **Batched Schema Refinement**: During large-scale database schema extraction, documents are batched into chunks (e.g., 4 papers per batch) to fit the token budget [459].
- **Information Omission Validation**: If a section is missing specific empirical data, the extraction prompt must instruct the agent to output explicit blank fields (e.g., `"NaN"` or empty strings) rather than hallucinating plausible placeholders [468, 474].

---

## 3. PDF Ingestion and Retrieval Pipeline Schema

```
 ┌──────────────┐      ┌─────────────┐      ┌───────────────┐
 │  Target PDF  │ ───> │ GROBID Engine│ ───> │ Structured XML│
 └──────────────┘      └─────────────┘      └───────┬───────┘
                                                    │
                                                    ▼
 ┌──────────────┐      ┌─────────────┐      ┌───────────────┐
 │ Nougat OCR   │ ───> │ Math Parser │ ───> │ Unified MD/TeX│
 └──────────────┘      └─────────────┘      └───────┬───────┘
                                                    │
                                                    ▼
 ┌──────────────┐      ┌─────────────┐      ┌───────────────┐
 │  SciPDF JSON │ ───> │ SciSpacy    │ ───> │   Tokenized   │
 └──────────────┘      │ Abbrev Map  │      │  RAG Chunks   │
                       └─────────────┘      └───────────────┘
```
