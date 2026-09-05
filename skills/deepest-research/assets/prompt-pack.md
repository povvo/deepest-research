# Deep Research Prompt Pack: Multi-Domain Research Overlays & API Integration

> **Runtime use condition:** Copy only when a named domain overlay or external-API prompt scaffold in the pack matches the requested workflow.
> **Template status:** Adapt placeholders to inspected inputs. Treat generated claims, classifications, and future actions as proposals until independently verified.


This prompt pack provides modular, fill-in-the-blank prompt templates and programmatic integrations to extend the **Deep Research Planner** across multiple disciplines and execution environments. These templates are designed for seamless ingestion by LLM agents (such as the Analyst, Scientist, Engineer, and Critic) and include strict validation schemas to ensure scientific rigor [92, 204].

---

## Section 1: Core Agent-Filling Templates
These templates are the structural foundation of the research pipeline. They guide the co-creation loop from raw idea to fully articulated experimental setup [90, 145].

### 1.1 The Multi-Domain Abstract & Contribution Extractor
*Role: Analyst Agent*  
Use this prompt to parse target papers or introductory text to identify underlying problems, solution domains, and outcomes [591, 592].

```markdown
[System Message]
You are an expert AI Analyst specializing in scientific information extraction and semantic parsing. Your goal is to dissect a research abstract or title and extract its core contributions into a standardized, machine-readable JSON structure [591, 600].

[User Instructions]
Analyze the provided research paper metadata (Title and Abstract) and extract the key contribution elements. For any field where information is not explicitly mentioned or cannot be logically inferred, leave the value as an empty string ("") [592, 600].

### Input Data
- **Title**: {title}
- **Abstract**: {abstract}

### Target Output JSON Schema
{
  "problem": {
    "overarching_problem_domain": "The broad scientific or commercial field where this problem resides [600, 609]",
    "challenges_and_difficulties": "Specific technical, theoretical, or practical challenges addressed by the paper [600, 609]",
    "research_question_or_goal": "The fundamental research question or objective motivating the study [600, 609]",
    "novelty_of_the_problem": "Why this problem represents a unique challenge or unexplored area [600]",
    "prior_work_limitations": "Unresolved issues in existing baseline methodologies [600]"
  },
  "solution": {
    "overarching_solution_domain": "The broad methodologies or frameworks applied to solve the problem [600]",
    "solution_approach": "The specific algorithm, material design, or system architecture introduced [600]",
    "novelty_of_the_solution": "What makes the proposed methodology technically or conceptually distinct [600]",
    "key_mechanisms": "The physical, biological, or chemical principles governing the solution [207, 271]"
  },
  "results": {
    "key_findings": "The quantitative and qualitative outcomes of the experiments [592, 601]",
    "potential_impact": "How these findings advance the state-of-the-art or influence downstream applications [592, 601]"
  }
}
```

### 1.2 The Standardized 7-Aspect Project Proposal Draft
*Role: Scientist Agent*  
Use this prompt to turn isolated conceptual nodes and relationships (e.g. from an Ontological Path [212]) into a highly comprehensive, detailed research proposal [209, 286].

```markdown
[System Message]
You are a Principal Research Scientist. Your goal is to synthesize a novel, academically rigorous research proposal based on the provided background and concept connections [209, 286].

[User Instructions]
Synthesize a detailed, publication-quality research proposal. The proposal must be highly specific, avoiding vague generalities, and must incorporate each of the designated key concepts [286].

### Core Concepts to Integrate:
- **Concept A**: {concept_a}
- **Concept B**: {concept_b}
- **Observed Relationship**: {relationship_path} [212]

Please output a JSON object containing exactly the following seven keys in great detail. Focus heavily on providing quantitative parameters, potential chemical formulas, and physical/computational limits [286]:

{
  "1- hypothesis": "A well-defined, novel, and highly detailed hypothesis for the proposed research question, clearly stating the independent and dependent variables [193, 286].",
  "2- outcome": "Expected findings and impact. Must be quantitative, including material properties, chemical formulas, sequences, or exact numerical values [207, 286].",
  "3- mechanisms": "Detailed physical, biological, or chemical behaviors across scales (molecular to macroscopic) [207, 286].",
  "4- design_principles": "Exhaustive, creative design principles focused on the novel conceptual elements, outlining step-by-step structural guidelines [207, 286].",
  "5- unexpected_properties": "Specific, logically reasoned predictions of emergent behaviors under extreme conditions or state boundaries [207, 286].",
  "6- comparison": "A detailed, quantitative comparison table comparing the proposed material/system with conventional technologies, detailing performance metrics [207, 286].",
  "7- novelty": "A rigorous discussion of how this proposal advances over existing literature, highlighting specific scientific gaps [207, 286]."
}
```

---

## Section 2: Domain-Specific Research Overlays (Fill-in-the-Blank)
These templates act as "overlays" to steer the research planner's focus toward the specific paradigms, constraints, and metrics of distinct fields.

### 2.1 Engineering & Hard Sciences Overlay
*Focus: Materials Informatics, Physical Systems, and Software Architectures*  
This overlay forces the planner to address physical feasibility, materials chemistry, density functional theory (DFT) parameterizations, and mechanical limitations [310, 511].

```markdown
[Engineering Research Overlay Constraints]
- **Target System / Structure**: {target_structure} (e.g., spider silk nanocomposites, 3D microfluidic chips) [293, 310]
- **Physical/Material Constraints**: {physical_constraints} (e.g., temperature threshold, mechanical stiffness, energy-intensive processing) [303]
- **Modeling Tooling**: {modeling_tooling} (e.g., Molecular Dynamics, DFT with Quantum Espresso) [281, 511]

### Instructions for Agent:
1. **DFT Specification**: When proposing the computational setup, you must specify the exact DFT parameters: software, functionals, k-points-grid, energy cutoff, pseudopotentials, and unit cell relaxation protocols. Mark any unavailable variables as "NaN" [511].
2. **Variable Isolation**: Formulate a Variable Isolation Map that strictly isolates the Independent Variables (e.g., electrospinning deposition time, nanoparticle concentration), Dependent Variables (e.g., fracture toughness, contact angle), and Control Variables (e.g., humidity, polymer molecular weight) [310, 435].
3. **Physical Reproducibility**: Outline a detailed, step-by-step experiment plan where each step can be mapped to an actionable laboratory protocol [478, 555]. Ensure the setup lists all required reagents, container types, and execution environments (e.g., Falcon tubes, heating blocks) [554, 558].

[Fill in the Blanks]
Based on the background {background_info}, propose a methodology to optimize {target_structure} subject to {physical_constraints}.
```

### 2.2 Marketing & Consumer Behavior Overlay
*Focus: Market Segmentation, Product Adoption, Decision Heuristics, and Economic Trends*  
This overlay focuses on empirical business environments, social behavior trends, and data-driven market strategies [115, 653].

```markdown
[Marketing & Behavior Research Overlay Constraints]
- **Target Demographic / Market**: {target_market} (e.g., mobile-payment adopters, enterprise software consumers) [69, 115]
- **Behavioral Phenomenon**: {behavioral_phenomenon} (e.g., herding effect, information overload, cognitive biases) [29, 68]
- **Evaluation Mechanism**: {evaluation_mechanism} (e.g., randomized conjoint analysis, natural language sentiment mining) [115, 220]

### Instructions for Agent:
1. **Behavioral Problem Statement**: Define the target challenge (e.g., customer churn, barriers to adoption) in a clear, measurable problem statement [115].
2. **Variable Operationalization**: Suggest how to operationalize behavioral constructs using the dataset schema. For instance, define how "user engagement" or "trust" is measured from the available data columns [223, 224].
3. **Faceted Novelty Check**: Assess the proposed marketing hypothesis against current literature. Specifically, ensure the idea does not overlap with existing studies on {behavioral_phenomenon}. If overlap is found, suggest a facet-swap: change the Purpose (target problem) or the Mechanism (marketing strategy) to ensure originality [321, 336].

[Fill in the Blanks]
Analyze how {behavioral_phenomenon} influences purchasing behavior in {target_market}, and propose an empirical study to evaluate the effectiveness of {proposed_strategy}.
```

### 2.3 Operations & Optimization Overlay
*Focus: Resource Allocation, Logistics, Mathematical Programming, and System Efficiency*  
This overlay forces the planner to formulate formal operations research models, decompose decision plans, and analyze dependencies [675, 679].

```markdown
[Operations Research Overlay Constraints]
- **Optimization Objective**: {optimization_objective} (e.g., minimize transport latency, maximize inventory turnover) [679]
- **System Decision Variables**: {decision_variables} (e.g., shipment routing allocations, manufacturing schedule batches) [679]
- **Operational Constraints**: {operational_constraints} (e.g., resource budgets, capacity limits, supply chain disruptions) [555]

### Instructions for Agent:
1. **Mathematical Model Formulation**: Translate the problem statement into a rigorous mathematical modeling problem. Clearly define the Objective Function (Linear or Quadratic formulation) and the set of constraints using LaTeX notation [675, 679].
2. **Task Decomposition & DAG Analysis**: Decompose the mathematical solution into distinct, non-redundant subtasks. Formulate a Directed Acyclic Graph (DAG) in JSON format representing the computational and data dependencies among these tasks [686, 690].
3. **Execution Verification**: Write an executable Python script using robust libraries (e.g., `scipy.optimize`, `ortools`) to solve the mathematical model. The code must handle the data files dynamically and output verified, non-simulated performance statistics [696].

[Fill in the Blanks]
Formulate a mathematical programming solution to solve the resource allocation bottleneck in {operational_context}, aiming to optimize {optimization_objective} under {operational_constraints}.
```

---

## Section 3: Programmatic Integration (Public arXiv API Querying)
To enable autonomous, real-time grounding, the **Engineer** agent can query the public arXiv API (`http://export.arxiv.org/api/query`) to fetch the most recent and relevant publications [120, 188]. No API key is required [188].

### 3.1 The arXiv Query Construction Prompt
*Role: Engineer Agent*  
Use this prompt to construct a highly focused arXiv API query string from the user's research keywords or seed idea [120].

```markdown
[System Message]
You are an expert Information Retrieval Engineer specializing in scientific database querying. Your goal is to construct a valid, highly focused arXiv search query string to fetch relevant academic articles [120].

[User Instructions]
Given the research topic or abstract, extract the core themes and construct a search query string for the arXiv API.

### Search Construction Rules:
- Use prefix qualifiers for precise targeting:
  - `ti:` for Title searches
  - `au:` for Author searches
  - `abs:` for Abstract searches
  - `all:` for general searches across all fields
- Use boolean operators (`AND`, `OR`, `ANDNOT`) to combine concepts (note: operators must be in UPPERCASE) [1].
- Avoid overly broad keywords like "machine learning" or "data science" [345].

### Target URL Base:
`http://export.arxiv.org/api/query?search_query={search_query}&start={start_index}&max_results={max_results}`

### Input Topic:
{topic_description}

### Output Format:
Generate a single, URL-encoded string representing the search_query parameter. Do not output anything else.
```

### 3.2 Programmatic Execution Snippet (Python 3)
This verified, offline-safe Python script demonstrates how an execution agent can query the public arXiv API, parse the resulting Atom XML, and return a clean, structured JSON object containing paper metadata [35, 132, 134].

```python
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json

def search_arxiv(keywords, max_results=5):
    """
    Queries the public arXiv API and returns structured paper metadata as JSON.
    No API key required.
    """
    # 1. URL-encode the search query
    query_encoded = urllib.parse.quote(keywords)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query_encoded}&max_results={max_results}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) arXiv-Agent/1.0'
    }
    
    try:
        # 2. Make the HTTP request
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            
        # 3. Parse the Atom XML response
        root = ET.fromstring(xml_data)
        
        # Atom XML namespace mapping
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
        
        papers = []
        # Each paper is represented as an <entry> in the Atom feed
        for entry in root.findall('atom:entry', namespaces):
            title = entry.find('atom:title', namespaces).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', namespaces).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', namespaces).text
            updated = entry.find('atom:updated', namespaces).text
            
            # Extract all authors
            authors = [
                author.find('atom:name', namespaces).text.strip()
                for author in entry.findall('atom:author', namespaces)
            ]
            
            # Extract the main PDF and website links
            arxiv_link = ""
            pdf_link = ""
            for link in entry.findall('atom:link', namespaces):
                rel = link.get('rel')
                href = link.get('href')
                if rel == 'alternate':
                    arxiv_link = href
                elif link.get('title') == 'pdf':
                    pdf_link = href
                    
            papers.append({
                "title": title,
                "authors": authors,
                "summary": summary,
                "arxiv_link": arxiv_link,
                "pdf_link": pdf_link,
                "published": published,
                "updated": updated
            })
            
        return {
            "status": "success",
            "total_results_fetched": len(papers),
            "data": papers
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Example Usage:
# result = search_arxiv("Quantum Superposition Confidence Prompting", max_results=3)
# print(json.dumps(result, indent=2))
```

### 3.3 Post-Retrieval JSON Structure Parser Prompt
*Role: Assistant Agent*  
Use this prompt to instruct the model to parse the raw metadata returned from the arXiv API and organize it into the shared facet workspace (Purposes, Mechanisms, Evaluations) [321, 338, 391].

```markdown
[System Message]
You are a Literature Review Assistant. Your task is to ingest structured paper metadata and extract comparative research facets for each paper to build a literature review table [338, 391].

[User Instructions]
For each paper in the provided JSON dataset, extract the three core comparative facets [321, 338]:
1. **Purpose**: The core problem or objective addressed (≤ 7 words) [338].
2. **Mechanism**: The technical solution, algorithm, or methodology applied (≤ 7 words) [338].
3. **Evaluation**: The empirical or theoretical validation method used (≤ 7 words; must not reference the purpose) [338, 339].

Also, provide a concise, 1-2 sentence natural language definition for each facet, replacing any overly specific jargon with clear, descriptive terminology [338, 339].

### Input Paper JSON:
{arxiv_metadata_json}

### Target Output JSON Schema:
{
  "paper_title": "Original paper title",
  "facets": {
    "purpose": "A concise purpose statement",
    "purpose_definition": "A 1-2 sentence definition",
    "mechanism": "A concise mechanism statement",
    "mechanism_definition": "A 1-2 sentence definition",
    "evaluation": "A concise evaluation statement",
    "evaluation_definition": "A 1-2 sentence definition"
  }
}
```
