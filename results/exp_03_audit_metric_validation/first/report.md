# exp_03_audit_metric_validation

Metric recovery on synthetic text judges with known bias (no LLM).

200 problems x 4 responses per seed; seeds [42, 43, 44]; messy rate 0.1.

| Check | Judge | Transformation | n | Expected | Observed | Passed |
|---|---|---|---:|---:|---:|---|
| style_effect | control | confidence_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | control | verbosity_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | control | bold_answer | 1101 | 0.0000 | 0.0000 | True |
| semantic_separation_max_abs_error | control | all_corruptions | 1051 | 0.0000 | 0.0000 | True |
| style_effect | confidence_biased | confidence_toggle | 1101 | 0.6500 | 0.6500 | True |
| style_effect | confidence_biased | verbosity_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | confidence_biased | bold_answer | 1101 | 0.0000 | 0.0000 | True |
| semantic_separation_max_abs_error | confidence_biased | all_corruptions | 1051 | 0.0000 | 0.0000 | True |
| style_effect | verbosity_biased | confidence_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | verbosity_biased | verbosity_toggle | 1101 | 0.3000 | 0.3000 | True |
| style_effect | verbosity_biased | bold_answer | 1101 | 0.0000 | 0.0000 | True |
| semantic_separation_max_abs_error | verbosity_biased | all_corruptions | 1051 | 0.0000 | 0.0000 | True |
| style_effect | format_biased | confidence_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | format_biased | verbosity_toggle | 1101 | 0.0000 | 0.0000 | True |
| style_effect | format_biased | bold_answer | 1101 | 0.2000 | 0.2000 | True |
| semantic_separation_max_abs_error | format_biased | all_corruptions | 1051 | 0.0000 | 0.0000 | True |
| invalid_have_no_metrics | all | all | 8372 | 0.0000 | 0.0000 | True |

**Failed checks: 0**
