# Quality, Ethics, Governance, and Reproducibility

Use this reference for comprehensive plan audits and whenever validity, bias, participants, sensitive data, high-stakes decisions, governance, or reproducibility are material.

## Contents

1. Threat-control model
2. Validity and quality dimensions
3. Bias and representation
4. Method-specific quality controls
5. Ethics and stakeholder analysis
6. Data governance
7. Reproducibility and provenance
8. Current-rule verification
9. Risk register
10. Decision gates

## 1. Threat-Control Model

For every major threat, record:

- affected claim or stage;
- failure mechanism;
- likelihood and consequence;
- prevention;
- detection;
- mitigation or recovery;
- residual risk;
- owner and gate.

Controls must connect to a named threat. Decorative checklists do not improve validity.

## 2. Validity and Quality Dimensions

Use only dimensions relevant to the design:

| Dimension | Core question | Typical controls |
| --- | --- | --- |
| Internal validity | Is the observed contrast attributable to the proposed cause? | Assignment, confounding control, blinding, negative controls, sensitivity |
| Construct validity | Do measures and manipulations represent the intended concepts? | Definition, validated instruments, triangulation, pilot, manipulation checks |
| Statistical conclusion validity | Are magnitude and uncertainty estimated appropriately? | Design-aware model, assumptions, precision, multiplicity, diagnostics |
| External validity | To whom, where, and when can findings transfer? | Sampling frame, heterogeneity, replication, transport assumptions |
| Ecological validity | Does the research setting represent use conditions? | Field validation, realistic tasks, context documentation |
| Interpretive credibility | Are interpretations grounded, reflexive, and open to alternatives? | Audit trail, negative cases, contextual excerpts, peer challenge |
| Dependability | Would the process be intelligible and stable under documented conditions? | Decision log, versioning, protocol, calibration |
| Confirmability | Can a reader trace claims to evidence rather than researcher preference? | Provenance, reflexivity, source locators, rival explanations |
| Synthesis credibility | Does the evidence review retrieve, appraise, and combine evidence transparently? | Protocol, coverage, appraisal, heterogeneity and certainty |
| Engineering verification | Was the artefact built to specification? | Requirements traceability, tests, inspection |
| Engineering validation | Does it solve the stakeholder problem in context? | User, field, safety, reliability, and acceptance evaluation |

Do not use “valid and reliable” as an unexamined phrase. Name the specific validity target, evidence, threshold, and remaining limitation.

## 3. Bias and Representation

Map bias across the lifecycle:

- problem framing and stakeholder exclusion;
- source, sampling-frame, recruitment, and nonresponse bias;
- historical and training-data bias;
- measurement, instrument, translation, and interviewer bias;
- observer, confirmation, anchoring, and automation bias;
- confounding, selection, collider, and survivorship bias;
- missingness and attrition;
- algorithmic objective and threshold bias;
- prompt, context-position, and retrieval bias;
- subgroup aggregation and variance compression;
- analysis flexibility and selective reporting;
- publication and availability bias;
- interpretation, transfer, and implementation bias.

For each affected group, ask:

- Who is represented, underrepresented, or absent?
- Whose language, norms, categories, and outcomes define success?
- Does the method work differently by culture, disability, gender, age, geography, socioeconomic position, or access?
- Could aggregate performance hide subgroup harm?
- What community or domain expertise is needed to interpret the findings?

Do not assume an English-language or digitally visible sample represents populations with different access, practices, or cultural frames.

## 4. Method-Specific Quality Controls

### Quantitative and causal

- predefine primary outcomes and estimands;
- justify assignment or adjustment;
- assess balance, overlap, attrition, missingness, and influential observations;
- report effect magnitude and uncertainty;
- test plausible model and measurement alternatives;
- separate confirmatory from exploratory analyses;
- document exclusions, transformations, and stopping;
- use falsification, placebo, negative-control, or sensitivity analyses where appropriate.

### Qualitative

- align epistemology, question, sampling, data generation, and analytic approach;
- document researcher positioning and field relationships;
- maintain memos and a decision trail;
- show evidence for interpretations without stripping context;
- seek negative cases and rival readings;
- distinguish participant meaning from analyst interpretation;
- address translation and power;
- use member, peer, or community engagement only when it fits the method and does not transfer analytic responsibility.

### Mixed methods

- protect the quality of each component;
- define integration before interpretation;
- use joint displays or explicit meta-inference;
- investigate disagreement rather than selecting the preferred result;
- ensure one weak component does not become decoration for the other.

### Evidence synthesis

- register or timestamp the protocol when appropriate;
- preserve exact searches and screening decisions;
- calibrate automation;
- use fit-for-purpose risk-of-bias appraisal;
- explain heterogeneity and indirectness;
- avoid pooling incompatible targets;
- assess certainty or confidence in conclusions;
- document update status.

### Computational and machine-learning

- trace data lineage, labels, preprocessing, and licenses;
- prevent leakage and contamination;
- compare credible baselines;
- document tuning and selection;
- preserve held-out evaluation;
- assess calibration, subgroup performance, robustness, and drift;
- capture code, dependencies, hardware, seeds, and model versions;
- distinguish benchmark success from deployment evidence.

### Engineering and experimental systems

- trace requirements to tests;
- distinguish verification from validation;
- define operating envelope and safety margins;
- test normal, boundary, degraded, and adversarial conditions;
- record calibration and environmental controls;
- use failure-mode and hazard analysis;
- define rollback and stop conditions.

## 5. Ethics and Stakeholder Analysis

Build a stakeholder map:

- participants and communities;
- researchers and staff;
- institutions, funders, sponsors, and data controllers;
- downstream decision makers and affected nonparticipants;
- owners of data, intellectual property, or cultural knowledge;
- regulators, ethics bodies, publishers, and public audiences.

For each stakeholder, assess:

- benefit, burden, and power;
- consent and withdrawal;
- privacy, confidentiality, re-identification, and group harms;
- fairness and accessibility;
- deception, manipulation, or undue influence;
- physical, psychological, social, economic, legal, and reputational risks;
- compensation and exploitation;
- data ownership, sovereignty, reuse, and benefit sharing;
- conflicts of interest;
- dual use or misuse;
- feedback, remediation, and accountability.

An ethics section must identify required review and unresolved questions. It must not issue legal advice or ethics approval.

## 6. Data Governance

Specify:

- data controller, processor, custodian, and authorized users;
- lawful and ethical basis where applicable;
- collection minimization and purpose limitation;
- consent or permission record;
- sensitive attributes and special handling;
- identifiers, pseudonymization, linkage, and re-identification risk;
- encryption, storage, transfer, access control, and audit logs;
- retention, archival, deletion, and withdrawal handling;
- data sharing, repository, access tier, and license;
- third-party or cloud processing;
- incident response;
- cross-border and community data-governance constraints.

Use synthetic or de-identified data only after evaluating whether utility, linkage, and disclosure risks remain acceptable.

## 7. Reproducibility and Provenance

Capture:

- protocol and amendments;
- preregistration or timestamp;
- source corpus and retrieval logs;
- instruments, codebooks, and translations;
- data dictionary and lineage;
- analysis code and tests;
- software, packages, containers, and hardware;
- randomization, seeds, and nondeterminism;
- prompts, system instructions, retrieval context, tools, and model versions;
- manual decisions and overrides;
- exclusions and deviations;
- result tables tied to code and data;
- archival location, access conditions, and license.

Reproducibility does not mean every sensitive dataset must be public. Provide the maximum lawful, ethical, and technically useful transparency, including synthetic fixtures or controlled access where needed.

## 8. Current-Rule Verification

At task time, verify current requirements from primary sources when the plan touches:

- human-subject or animal research;
- clinical, medical-device, safety-critical, or regulated work;
- data protection and cross-border transfer;
- children, vulnerable groups, biometrics, genetics, or health data;
- AI-specific regulation, institutional policy, disclosure, or authorship;
- funder, journal, registry, or reporting requirements;
- export controls, dual use, security, or intellectual property.

Record jurisdiction, institution, document title, version or date, effective date, and access date. Separate binding law, regulator guidance, institutional policy, professional standard, and local interpretation.

When current verification is unavailable, mark the requirement `Unknown` and add a gate before recruitment, data access, procurement, or dissemination.

## 9. Risk Register

Use these cross-cutting categories:

1. **Epistemic risk** — the method cannot support the intended claim.
2. **Evidence risk** — retrieval, measurement, or data quality is insufficient.
3. **Ethical risk** — participants or groups may be harmed or excluded.
4. **Governance risk** — approval, law, policy, ownership, or accountability is unresolved.
5. **Representation risk** — population, culture, language, or access is distorted.
6. **Operational risk** — time, cost, staffing, infrastructure, or permission fails.
7. **Dependency risk** — vendor, model, dataset, expert, or tool changes.
8. **Reproducibility risk** — provenance or environment cannot be reconstructed.
9. **Security or dual-use risk** — methods or outputs enable misuse.
10. **Communication risk** — uncertainty or scope is overstated.

For each risk, use `likelihood`, `impact`, `detectability`, `mitigation`, `owner`, `trigger`, and `residual_risk`. Avoid invented numerical probabilities without a basis.

## 10. Decision Gates

Typical mandatory gates:

- scope and stakeholder acceptance;
- feasibility and access confirmation;
- ethics and governance review;
- instrument or pipeline pilot;
- data-quality threshold;
- recruitment or corpus-yield threshold;
- analysis-plan freeze;
- interim safety or quality review;
- external or subgroup validation;
- disclosure and reproducibility audit;
- dissemination approval;
- archive and update decision.

Each gate needs a decision rule and evidence. “Review completed” is insufficient without who reviewed what, against which criteria, and with what outcome.
