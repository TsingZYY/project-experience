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

## Multi-Agent Reinforcement Learning | COMP9414 | July–August 2026

**Python, NumPy, IPPO, MAPPO, GAE, PPO**

- Implemented a cooperative grid environment, joint-action handling and a safety shield, with NumPy neural networks, backpropagation, Adam and PPO updates.
- Developed independent IPPO actors/critics and a MAPPO variant with a shared actor and centralized critic.
- Documented saved in-setting evaluations and 400 episodes on unseen random layouts, separating cleaning performance, coordination measures and policy differences.

**Scope:** Coursework with AI-assisted development and learning; one training seed per configuration. Published core definitions are an excerpt, have no pretrained weights and were not executed during this review.  
[Case study](projects/comp9414-marl/README.md)

## TaskTracker Backend and Team Integration | COMP9820 | March–April 2026

**Python, Flask, SQLite, REST APIs, JavaScript**

- Contributed backend implementation and frontend integration to a team task-management application, supported by individual Git commits.
- Implemented validation, keyword-search escaping, server-side sorting, task statuses and compatible SQLite migrations; separated routes, services and database access.
- Contributed iteration documentation and regression coverage, and mapped individual commits to a contribution timeline.

**Scope:** Individual contributions within a team project. Course guidelines prohibit public code repositories, so source remains local. Historical test totals differ by version and were not rerun.  
[Case study](projects/comp9820-tasktracker/README.md)

## PostgreSQL Queries and Business Rules | COMP9311 | April 2026

**PostgreSQL, SQL, PL/pgSQL, joins, aggregation**

- Implemented six SQL views and four PL/pgSQL functions over an academic-records schema using joins, aggregation, correlated subqueries and procedural control flow.
- Expressed program/term conditions, academic-status and weighted-average-mark rules, including input branches and formatted results.
- Documented the query design and schema requirements alongside the student-authored SQL snapshot.

**Scope:** Source snapshot only; the public package excludes university data and checking scripts. No saved passing report or course grade is claimed.  
[Case study](projects/comp9311-database/README.md)

## Text Difference Analyzer | COMP9021 | April 2026

**Python, dynamic programming, LCS, memoized backtracking**

- Implemented difference-command parsing, exception handling and consistency checks against file contents.
- Used LCS dynamic programming and memoized backtracking to enumerate optimal difference descriptions and render changed and unchanged sections.
- Documented O(mn) matrix costs and the additional combinatorial cost of enumerating all optimal descriptions.

**Scope:** Standard-library source and recorded debugging discussion; no new execution or verified course grade.  
[Case study](projects/comp9021-text-diff/README.md)

Further coursework, including card simulation, search/planning and graph algorithms, is indexed in the [coursework collection](COURSEWORK.md).
