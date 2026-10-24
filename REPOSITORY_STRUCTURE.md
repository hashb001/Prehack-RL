# Project-wide repository structure

This is the target layout for the entire PreHack-RL project. It is a design plan, not a claim that every listed file already exists. Keep the current `pilot.py`, `prehack/core.py`, and tests working while adding components incrementally.

```text
PreHack-RL/
├── README.md                         # Project overview, roadmap, status, quick start
├── REPOSITORY_STRUCTURE.md           # This layout and organization conventions
├── LICENSE                           # Add after choosing the license
├── .gitignore                        # Environments, secrets, caches, large artifacts
├── pyproject.toml                    # Add when packaging/dependencies are introduced
├── pilot.py                          # Current synthetic experiment entry point
│
├── prehack/                          # Reusable implementation
│   ├── __init__.py
│   ├── core.py                       # Current synthetic components
│   ├── tasks/                        # Task loaders, schemas, split construction
│   ├── policies/                     # Generation and checkpoint adapters
│   ├── judges/                       # Synthetic and real judge adapters
│   ├── verifiers/                    # Independent task correctness checks
│   ├── counterfactuals/              # Transformations and validity checks
│   ├── auditing/                     # Audit measurements and aggregation
│   ├── monitoring/                   # Calibration, warning rules, event definitions
│   ├── interventions/                # Selection, verification, reward handling
│   ├── training/                     # RL integration and callbacks
│   ├── evaluation/                   # Metrics, comparisons, statistical analysis
│   └── tracking/                     # Manifests, usage accounting, structured logging
│
├── experiments/                      # One folder per runnable study
│   ├── exp_00_synthetic_best_of_n/
│   ├── exp_01_synthetic_counterfactual_audit/
│   ├── exp_02_transform_validation/
│   ├── exp_03_audit_metric_validation/
│   ├── exp_04_llm_judge_audit/
│   ├── exp_05_llm_best_of_n/
│   ├── exp_06_grpo_control/
│   ├── exp_07_grpo_imperfect_judge/
│   ├── exp_08_policy_conditioned_vs_static_audit/
│   ├── exp_09_early_warning_prediction/
│   ├── exp_10_audit_guided_verification/
│   ├── exp_11_budget_matched_interventions/
│   ├── exp_12_existing_defense_comparison/
│   ├── exp_13_unseen_bias_and_distribution_shift/
│   ├── exp_14_component_ablations/
│   └── exp_15_cost_performance_analysis/
│
├── configs/                          # Shared configuration; no credentials
│   ├── models/
│   ├── judges/
│   ├── tasks/
│   └── training/
├── prompts/                          # Versioned judge and transformation prompts
├── scripts/                          # Data preparation, batch runs, analysis helpers
├── tests/
│   ├── test_pipeline.py              # Current synthetic tests
│   ├── unit/
│   └── integration/
│
├── data/
│   ├── README.md                     # Sources, licenses, preparation, split rules
│   ├── fixtures/                     # Small redistributable examples for tests
│   ├── raw/                          # Downloaded data; generally ignored
│   └── processed/                    # Generated data; generally ignored
├── runs/                             # Local raw runs; generally ignored
├── checkpoints/                      # Model weights; ignored
├── results/                          # Curated, small version-controlled evidence
│   ├── exp_00_synthetic_best_of_n/
│   └── exp_01_synthetic_counterfactual_audit/
├── figures/                          # Selected figures and generation instructions
│
├── docs/
│   ├── roadmap.md                    # Eight phases and completion gates
│   ├── methodology.md                # Definitions, metrics, access assumptions
│   ├── related_work.md               # Verified sources and comparison matrix
│   ├── reproducibility.md            # Environment, datasets, seeds, exact commands
│   └── decisions.md                  # Important design choices and rationale
├── paper/                            # Manuscript sources when writing begins
└── .github/
    └── workflows/
        └── tests.yml                 # Add CI after choosing supported environments
```

## Experiment folder convention

Add these files when an experiment becomes runnable:

```text
exp_XX_descriptive_name/
├── README.md        # Question, design, command, metrics, limits, interpretation
├── config.json      # Experiment-specific parameters when supported by the runner
└── run.py           # Thin runner importing shared code from prehack/
```

The current CLI does not load configuration files. Until that functionality is added, the first two experiment READMEs should point to `pilot.py` and its supported command-line arguments. Do not duplicate the pilot or change its location without updating imports and tests.

## Phase ownership

| Phase | Experiment IDs | Main modules |
|---|---|---|
| 01 — Controlled Experimental Foundation | 00–01 | core, tests, tracking |
| 02 — Counterfactual Audit Engine | 02–03 | counterfactuals, auditing, verifiers |
| 03 — Real LLM Judge Evaluation | 04–05 | tasks, policies, judges, evaluation |
| 04 — Reinforcement Learning Baseline | 06–07 | training, policies, tracking |
| 05 — Audit Prediction and Monitoring | 08–09 | monitoring, auditing, evaluation |
| 06 — Selective Verification and Intervention | 10–11 | interventions, verifiers, training |
| 07 — Defense Comparison and Generalization | 12–15 | evaluation, configs, relevant defense integrations |
| 08 — Research Synthesis and Release | Uses completed studies | docs, results, figures, paper |

## Results convention

Keep raw runs immutable. Use a distinct directory for each execution, for example:

```text
runs/exp_00_synthetic_best_of_n/2026-10-25_seed42-44/
```

Commit curated summaries, manifests, reports, and small figures under `results/<experiment>/`. Preserve raw artifacts through an appropriate release or data archive when needed for research reproduction. Document their location and checksums.

Do not commit credentials, private data, virtual environments, caches, or model checkpoints. Check redistribution rights before committing third-party datasets. Select a license before adding a LICENSE file or license badge.

## Current files versus future layout

The current implementation remains in `pilot.py`, `prehack/core.py`, and `tests/test_pipeline.py`. Both synthetic studies run together, and their outputs are under `runs/phase1/`. No future module, experiment runner, packaging setup, or CI workflow is implied to be implemented by this document.
