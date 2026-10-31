# exp_02_transform_validation

Transformation validity on synthetic text (no LLM). 500 problems x 4 responses per seed; seeds [42, 43, 44]; messy rate 0.1.

| Kind | Transformation | Probes | Valid | Rejected | Rejection rate |
|---|---|---:|---:|---:|---:|
| corruption | numeric_corruption_+1 | 6000 | 2645 | 3355 | 0.5592 |
| style | bold_answer | 6000 | 5367 | 633 | 0.1055 |
| style | confidence_toggle | 6000 | 5367 | 633 | 0.1055 |
| style | verbosity_toggle | 6000 | 5367 | 633 | 0.1055 |

## Rejection reasons

| Transformation | Reason | Count | Expected ineligibility |
|---|---|---:|---|
| bold_answer | original_ambiguous | 228 | True |
| bold_answer | original_none | 405 | True |
| confidence_toggle | original_ambiguous | 228 | True |
| confidence_toggle | original_none | 405 | True |
| numeric_corruption_+1 | original_ambiguous | 228 | True |
| numeric_corruption_+1 | original_incorrect | 2722 | True |
| numeric_corruption_+1 | original_none | 405 | True |
| verbosity_toggle | original_ambiguous | 228 | True |
| verbosity_toggle | original_none | 405 | True |

**Unexpected rejections: 0** (non-zero means a transformation or parser bug).
