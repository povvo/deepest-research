# Evidence Strategy, Search, and Novelty Discipline

Use this reference when planning or auditing source retrieval, literature reviews, evidence maps, current claims, gap analyses, or novelty assessments.

## Contents

1. Evidence states
2. Claim-driven evidence planning
3. Source selection
4. Reproducible search protocol
5. Screening and extraction
6. Appraisal and applicability
7. Contradictions and synthesis
8. Saturation and stopping
9. Novelty assessment
10. Current and unstable claims
11. Evidence ledger contract
12. Failure and recovery rules

## 1. Evidence States

Never collapse these states:

- **Inspected evidence:** content was actually opened or provided, with a locator.
- **Named source:** a citation or URL is known but content was not inspected.
- **Retrieved candidate:** found by a search but not yet screened or appraised.
- **Proposed search:** query or source class is planned but not run.
- **Inference:** interpretation derived from inspected evidence.
- **Unknown:** no adequate evidence yet.

A source title, abstract, snippet, model memory, or citation list is not equivalent to inspecting the supporting passage.

## 2. Claim-Driven Evidence Planning

Start with a claim inventory, not a database list. For each planned conclusion, record:

- exact claim or decision;
- evidence type needed;
- target population, setting, jurisdiction, language, and period;
- acceptable design and source quality;
- recency or update requirement;
- likely disagreement or bias;
- consequence if wrong;
- planned verification.

High-consequence claims require stronger and more directly applicable evidence. Definitions, mechanisms, prevalence, intervention effects, implementation conditions, ethics requirements, and novelty each need different source strategies.

## 3. Source Selection

Prefer source classes according to the question:

- **Current rules or product behaviour:** first-party regulations, institutional policy, standards, official documentation, release notes, or source code.
- **Effects and diagnostic performance:** systematic reviews, trials, strong quasi-experiments, prospective validation, benchmark datasets with transparent methods.
- **Mechanisms:** theory, process studies, experiments, triangulated case evidence.
- **Experiences and meanings:** primary qualitative studies with contextual detail.
- **Prevalence and distributions:** representative surveys, censuses, registries, transparent administrative sources.
- **Emerging methods:** primary papers, preprints clearly labelled, replication evidence, and critical commentary.
- **Implementation:** field evaluations, technical reports, practitioner evidence, and context-specific guidance.
- **Novelty or competitive landscape:** scholarly databases, citation networks, registries, patents where relevant, standards, repositories, and grey literature.

Do not use a generic hierarchy that treats one design as universally superior. Judge directness, credibility, applicability, and transparency.

## 4. Reproducible Search Protocol

Specify before or while searching:

1. review purpose and target questions;
2. source classes, databases, websites, registries, and repositories;
3. concept blocks, synonyms, controlled vocabulary, identifiers, and exclusions;
4. exact query strings per source where possible;
5. date searched and coverage period;
6. language, geography, population, design, publication-type, and status limits;
7. citation chasing, related-record searching, expert input, and grey literature;
8. deduplication method;
9. screening and conflict-resolution process;
10. update or rerun trigger.

Search breadth should reflect the claim. A proposal scan may be structured but bounded; a systematic review needs reproducible coverage and defensible completeness.

When using live tools, save query, timestamp, result count, source, and export. When no live search is available, return the search plan as `Proposal`, never as completed coverage.

## 5. Screening and Extraction

Define inclusion and exclusion criteria in operational terms. Test them on a small diverse sample and refine before full screening.

Record for each item:

- stable identifier and full citation;
- retrieval source and date;
- screening stage and decision;
- exclusion reason;
- study context, population, method, data, and timeframe;
- relevant claim and exact locator;
- result or finding with uncertainty;
- limitations and conflicts of interest;
- appraisal result;
- applicability to the target question;
- verification status and reviewer.

For consequential evidence synthesis, use independent or calibrated verification proportionate to error cost. Automation may prioritize or extract, but sample and audit it against human judgments before relying on it.

## 6. Appraisal and Applicability

Appraise four dimensions separately:

1. **Credibility** — Is the design and reporting trustworthy?
2. **Directness** — Does it address the same target, intervention, construct, outcome, and decision?
3. **Applicability** — Does it transfer across population, culture, language, place, time, system, and implementation conditions?
4. **Precision and stability** — How uncertain, heterogeneous, or update-sensitive is it?

A strong study in a distant context may be less useful than a moderate but directly applicable study. Record both source quality and transfer assumptions.

For AI and computational studies, also inspect:

- dataset provenance and contamination;
- train/test separation and benchmark fit;
- model and version;
- prompt or pipeline disclosure;
- baseline quality;
- subgroup and failure analysis;
- external, temporal, or cross-site validation;
- code, data, and environment availability.

## 7. Contradictions and Synthesis

Do not treat disagreement as noise. Build a contradiction table:

| Claim | Supporting evidence | Counter-evidence | Method/context differences | Possible moderator | Discriminating evidence |
| --- | --- | --- | --- | --- | --- |

Distinguish:

- true empirical conflict;
- different populations or interventions;
- different operational definitions;
- different causal targets;
- methodological quality differences;
- temporal change;
- publication or selection effects;
- apparent contradiction caused by aggregation.

Synthesis may be quantitative, thematic, realist, configurational, narrative, or structured comparative. State why the method fits the evidence and what uncertainty remains.

## 8. Saturation and Stopping

Use a stopping rule appropriate to the task:

- no new implementation-relevant category after successive credible sources;
- no unresolved contradiction changing the design;
- citation and concept coverage reaches diminishing returns;
- predefined database and grey-literature coverage is complete;
- confidence or precision target is met;
- decision deadline requires a transparent rapid-review boundary.

Record what remains unsearched. “No more results were convenient” is not saturation.

For living or time-sensitive evidence, define a calendar, event, or evidence-threshold update trigger.

## 9. Novelty Assessment

Novelty is multidimensional. Compare the proposed work to nearest prior work by:

- problem or purpose;
- theory or conceptual framing;
- population, setting, language, or jurisdiction;
- data or material;
- intervention, mechanism, or architecture;
- method or identification strategy;
- outcome and evaluation;
- integration across fields;
- replication, robustness, or boundary testing;
- implementation, cost, or accessibility.

Use calibrated conclusions:

- **Established overlap** — closely matched prior work was found.
- **Incremental contribution** — changes a meaningful dimension.
- **Contextual extension** — tests transfer to a new population or setting.
- **Methodological contribution** — improves design, measurement, analysis, or validation.
- **Synthetic contribution** — integrates evidence or concepts not previously connected.
- **Candidate gap** — plausible absence, search not yet sufficient.
- **Unresolved** — evidence is contradictory or coverage incomplete.

Never infer novelty from a model’s inability to recall prior work. A top-k list is a prioritization device, not proof of field coverage.

## 10. Current and Unstable Claims

Treat these as update-sensitive:

- laws, regulation, ethics guidance, funder and journal policies;
- current officeholders or institutional roles;
- software, APIs, model behaviour, pricing, availability, and benchmarks;
- clinical, safety, financial, or legal requirements;
- rapidly emerging methods and active controversies.

At task time:

1. search current first-party sources;
2. record publication or update date and access date;
3. separate binding rule, institutional policy, guidance, and interpretation;
4. state jurisdiction and scope;
5. note unresolved conflict;
6. avoid freezing unstable details into a general plan.

## 11. Evidence Ledger Contract

Use `templates/evidence-ledger-template.csv`. Each row represents one source-claim relationship, not merely one document.

Required fields:

- `evidence_id`
- `claim_id`
- `epistemic_status`
- `source_type`
- `citation_or_identifier`
- `source_date`
- `accessed_date`
- `population_setting`
- `method`
- `claim_supported`
- `exact_locator`
- `support_direction`
- `quality`
- `applicability`
- `limitations`
- `verification`
- `notes`

Allowed `epistemic_status` values are `Verified`, `Inference`, `Assumption`, `Proposal`, and `Unknown`. A row marked `Verified` requires an inspected source and exact locator.

## 12. Failure and Recovery Rules

- **Paywall or inaccessible source:** mark uninspected; seek lawful alternatives or author versions.
- **Broken or ambiguous identifier:** verify through another primary index; do not guess.
- **No source supports a claim:** mark `Unknown` or remove the claim.
- **Only indirect evidence:** state transfer assumptions and downgrade confidence.
- **Conflicting evidence:** preserve both sides and identify discriminating evidence.
- **Too many results:** refine by target, design, population, and decision relevance before arbitrary truncation.
- **Too few results:** broaden synonyms, citation chains, adjacent fields, grey literature, language, and date while documenting the expansion.
- **Automation disagreement:** sample errors, recalibrate, and increase human verification.
- **Search unavailable:** return a reproducible proposed search and prohibit novelty or completeness claims.
