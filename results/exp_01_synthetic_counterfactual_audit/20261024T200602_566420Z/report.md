# Experiment 01: synthetic counterfactual audit

Computed from recorded probes; no LLM, prediction, or intervention claim.

Semantic degradation is evaluated only for correct originals. N/A denotes ineligible probes.

| Seed | Judge | Correct | Confident | Probes | Valid style | Semantic eligible | Style sensitivity | Uplift | Semantic separation |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 42 | control | True | False | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 42 | control | True | True | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 42 | control | False | False | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 42 | control | False | True | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 42 | confidence_biased | True | False | 2000 | 2000 | 2000 | 0.3000 | 0.3000 | 0.6000 |
| 42 | confidence_biased | True | True | 2000 | 2000 | 2000 | 0.3000 | 0.0000 | 0.2500 |
| 42 | confidence_biased | False | False | 2000 | 2000 | 0 | 0.6500 | 0.6500 | N/A |
| 42 | confidence_biased | False | True | 2000 | 2000 | 0 | 0.6500 | 0.0000 | N/A |
| 43 | control | True | False | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 43 | control | True | True | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 43 | control | False | False | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 43 | control | False | True | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 43 | confidence_biased | True | False | 2000 | 2000 | 2000 | 0.3000 | 0.3000 | 0.6000 |
| 43 | confidence_biased | True | True | 2000 | 2000 | 2000 | 0.3000 | 0.0000 | 0.2500 |
| 43 | confidence_biased | False | False | 2000 | 2000 | 0 | 0.6500 | 0.6500 | N/A |
| 43 | confidence_biased | False | True | 2000 | 2000 | 0 | 0.6500 | 0.0000 | N/A |
| 44 | control | True | False | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 44 | control | True | True | 2000 | 2000 | 2000 | 0.0000 | 0.0000 | 0.6000 |
| 44 | control | False | False | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 44 | control | False | True | 2000 | 2000 | 0 | 0.0000 | 0.0000 | N/A |
| 44 | confidence_biased | True | False | 2000 | 2000 | 2000 | 0.3000 | 0.3000 | 0.6000 |
| 44 | confidence_biased | True | True | 2000 | 2000 | 2000 | 0.3000 | 0.0000 | 0.2500 |
| 44 | confidence_biased | False | False | 2000 | 2000 | 0 | 0.6500 | 0.6500 | N/A |
| 44 | confidence_biased | False | True | 2000 | 2000 | 0 | 0.6500 | 0.0000 | N/A |
