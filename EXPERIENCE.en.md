# Selected Project Experience

Evidence reviewed on 30 September 2026. These entries describe separate projects developed with AI assistance. Select two or three to match the role; source ownership, experimental scope and verification limits are documented in the linked case studies.

## LLM Prompt Regression Evaluation Pipeline | July 2026

**Python, JSONL, YAML, model APIs, LLM-as-judge, statistical analysis**

- Implemented a configuration-driven pipeline for batch generation, structured grading, bidirectional A/B comparison and automated reports.
- Organized 40 evaluation cases across four input categories; aggregated repeated runs by case before applying a sign test to avoid pseudoreplication.
- Implemented retry and backoff, task hashing and resume mechanisms, together with blind annotation and Cohen’s kappa analysis tools.

**Scope:** Core workflow has a source repository. Current saved results are mock outputs; completed human agreement measurements were not found.  
[Case study](projects/llm-evaluation.md)

## Atlassian Support Analytics and Evidence Review Prototype | September 2026

**Python, pandas, NumPy, bootstrap, permutation tests, multiple-testing correction**

- Audited joins and data quality across 8,320 customer records, 8,469 support tickets and 42,210 usage records in a synthetic competition dataset.
- Reframed product-month observations at customer level; quantified approximately 87.93% of integration-usage variance explained by plan category, with approximately 87.26% on 1,666 held-out customers.
- Implemented a traceable review-rule prototype and used negative controls, stratified comparisons and Holm correction to evaluate operational hypotheses.

**Scope:** Offline analysis and implemented rules; no verified customer intervention, revenue uplift or improvement in ticket resolution.  
[Case study](projects/atlassian-analytics.md)

## Kaggriculture Decision Agent and Evaluation Workflow | August 2026

**Python, state-based decision policies, baseline comparison, reproducible packaging**

- Iterated a competition decision agent with targeted policy branches and explicit fallback to the baseline.
- Evaluated candidate and control policies across 100 seeds, six opponents and both seat positions, producing 2,400 local games.
- Checked action parity between the source implementation and submission package and retained evaluation and packaging records.

**Scope:** Local environment results; official submission and leaderboard performance were not verified.  
[Case study](projects/kaggriculture.md)

## Algothon Strategy Research and Validation Engineering | July–August 2026

**Python, NumPy, mean reversion, pair trading, replay evaluation**

- Iterated multi-asset strategy variants and documented their hypotheses, parameters and evaluation windows.
- Aligned local replay with the evaluator’s scoring conventions and separated public model-selection results from hidden-data claims.
- Maintained packaging and release checks; organized research notes and subsequently published them alongside a final-candidate source snapshot.

**Scope:** Research and local replay; no claim of live trading profitability or verified hidden-test performance.  
[Case study](projects/algothon.md)

## Titanic Tabular ML Workflow | August–September 2026

**Python, pandas, scikit-learn, Pipeline, Jupyter**

- Implemented data checks, exploratory analysis, feature transformations, model comparison, final fitting and submission generation.
- Encapsulated preprocessing inside a scikit-learn Pipeline and used family-disjoint splits to reduce cross-fold family leakage.
- Recorded five-fold cross-validation accuracy of approximately 83.45% and family-disjoint holdout accuracy of approximately 78.7% in the current notebook.

**Scope:** Saved local outputs, not rerun in this review. Older documentation and the validator still need alignment with the newer split protocol.  
[Case study](projects/titanic.md)

## RLVR Verifier Error Structure: Protocol and Evidence Audit | July–August 2026

**Python, experimental design, mechanism diagnostics, evidence manifests**

- Developed frozen protocols and evidence records for investigating verifier-error structure and cross-task risk.
- Used model-free diagnostics to reject an earlier mechanism explanation and revise subsequent experimental controls.
- Separated engineering canary execution from scientific completion and preserved unsuccessful or incomplete outcomes.

**Scope:** Research engineering; zero of eight R13 scientific runs completed in the reviewed status snapshot.  
[Case study](projects/rlvr-audit.md)
