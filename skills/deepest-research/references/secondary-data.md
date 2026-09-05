# 1. Secondary Data Analysis and Sentiment Analysis Checklist

> **Runtime use condition:** Read when planning secondary text-data analysis, sentiment classification, or corpus-based observational research.
> **Evidence status:** Retained project-derived playbook. Verify implementation-critical claims, dependencies, and current product behaviour before use. Bracketed numbers are legacy source-map tokens, not user-ready citations.

This checklist outlines the procedures and rigorous standards for conducting large-scale text analysis, opinion mining, and LLM classification in secondary research, based on established literature and evaluation methodologies [32, 33, 57, 58].

## Section 1: Preprocessing & Corpus Filtering
- [ ] **Boilerplate and Markup Removal**: Implement standard, reproducible algorithms to strip HTML markup, CSS, and navigation headers from scraped or retrieved secondary text, ensuring that only natural language remains [30, 50, 51].
- [ ] **Part-of-Speech (POS) and Stopword Filtering**: Apply POS tagging and stopword filters to select core linguistic features. Document the percentage of text retained (e.g., standard approaches report keeping ~65.6% of words after stop-POS filtering) [2].
- [ ] **Quality Screening ("Written by Humans for Humans")**: Establish language-specific quality thresholds utilizing native speakers to filter out machine-generated boilerplate, search-engine-optimized spam, or low-quality/non-natural language [51].
- [ ] **Contamination Checking**: Perform n-gram filtering and fuzzy deduplication across datasets to ensure that downstream training/evaluation targets are not contaminated with pretraining data or test sets [28].

## Section 2: Opinion Mining & Classification
- [ ] **Faceted Sentiment Classification**: Define the sentiment categories explicitly (e.g., positive, negative, neutral, or fine-grained polarities) and map them to standardized schemas [32, 33].
- [ ] **Few-Shot Demonstration Engineering**: Write a range of manually annotated exemplar delimiters (e.g., "Tweet: {text} Sentiment: {sentiment}") and use randomly sampled demonstrations to anchor the model’s classification baseline [8, 47, 64].
- [ ] **Missing Citation Detection**: Task the LLM to inspect text corpora for missing references by adopting a serious, critical reviewer persona, flagging specific sentences requiring supporting citations [29].
- [ ] **Toxicity and Responsible AI Filtering**: Set up a classifier/discriminator (e.g., based on LaMDA safety annotator UI or Sparrow rules) to detect, rate, and filter out toxic, biased, or adversarial content [15, 31, 37].

## Section 3: Validation, Evaluation, & Metrics
- [ ] **Ground-Truth Comparisons**: Verify LLM classifications against expert human-annotated samples using exact match and F1-score metrics [122, 260].
- [ ] **Agreement Metric Calculations**: For subjective tasks, calculate intercoder agreement using Fleiss' Kappa [556, 561] or Krippendorff's alpha-reliability [42] to validate annotator consensus before using LLM-as-a-judge [453, 556].
- [ ] **Multi-Agent Simulation Loops**: In corporate or administrative text analysis, use multi-agent role-playing (e.g., Program Chair, Senior Area Chair, Area Chair, and Reviewers) to simulate discussion dynamics and reach a balanced, consensus-driven final classification [270, 275, 653].
- [ ] **Uncertainty Quantification (UQ)**: Systematically gauge model confidence on edge cases by measuring verbalized confidence ratings (e.g., a scale of 1-10 or 1-5) and use these metrics to flag high-uncertainty classifications for manual expert auditing [298, 448, 454].
