# 4. Survey Research with AI Checklist

> **Runtime use condition:** Read when AI supports questionnaire design, conversational interviewing, survey administration, or respondent-integrity controls.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.

This checklist details the standards for using AI in questionnaire design, chatbot-based interviewing, automated question validation, and addressing the **respondent AI-use problem** [77, 446, 450].

## Section 1: Questionnaire Design & Automated Appraisal
- [ ] **AGIL-Based Question Appraisal**: Evaluate draft survey questions against the rigorous AGIL framework criteria [450, 457]:
  - **Factual recall and alignment**: Ensure the question matches real-world constructs [447, 450].
  - **Correct answer and precision**: Verify there is only one unambiguously correct or non-conflicting interpretation [457].
  - **Avoidance of controversy**: Ensure that option scales align with current academic consensus and avoid contentious topics [457].
- [ ] **Prompt-Driven Personalization**: Establish conversational dialogue structures to iteratively refine question wording based on target participant demographics and literacy constraints [343].
- [ ] **Pydantic Schema Serialization**: Use Pydantic objects to serialize survey configurations and question properties into standardized JSON structures, ensuring robust machine readability [263, 266].

## Section 2: Conversational Chatbot-Based Interviewing
- [ ] **ReAct Dialogue Modeling**: Implement a ReAct (Thought-Action-Observation) framework to manage the conversational interviewing agent, allowing it to adaptively probe respondents' answers based on their previous remarks [125, 262].
- [ ] **Ethical Consent & Transparent Instructions**: Include a mandatory first turn in all chatbot interviews displaying a clear consent form specifying the purpose, procedures, duration, compensation, risk assessment, and institutional affiliations [20, 21, 77, 536].
- [ ] **Fidelity and Relationship Constraints**: Instruct the interview bot to maintain a polite, neutral, and helpful tone while strictly prohibiting it from building personal relationships, claiming human identities, or expressing ungrounded personal opinions [43, 222].

## Section 3: The Respondent AI-Use Problem & Fraud Defense
- [ ] **Multi-Stage Screening and Catch Trials**: Implement a three-stage participant screening pipeline to catch uncooperative, bot-simulated, or AI-assisted human respondents [77]:
  - *Stage 1 (Practice Task)*: Ensure the participant understands the interface mechanics [77].
  - *Stage 2 (Instruction Check)*: Test comprehension of the provided guidelines [77].
  - *Stage 3 (Catch Trial)*: Intersperse a "reservoir catch trial" where an obvious, previously answered question is re-asked. Exclude any respondent who fails the catch trial [77].
- [ ] **AI-Generated Text Detection**: For open-text responses, deploy high-performance detection tools (e.g., Fast-DetectGPT) to classify whether the respondent's comments are machine-generated, filtering out unauthorized bot responses [382, 387].
