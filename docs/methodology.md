# Methodology (Phase 2)

## Answer parsing (`prehack/verifiers/parsing.py`)
- Candidates: numbers after `\boxed{...}` or after a marker word (`final answer`, `answer`, `result`).
  Other numbers (e.g. in reasoning) are ignored.
- No candidate -> `none`. We never guess from stray numbers.
- Conflicting candidate values (including across `\boxed` and marker) -> `ambiguous`.
- Otherwise `ok`; the span points at the last candidate.
- Known limits: integers only; decimals and fractions parse as `none`.

## Transformations
| Name | Kind | Effect |
|---|---|---|
| `confidence_toggle` | style | add/remove "I am absolutely certain." |
| `verbosity_toggle` | style | add/remove a neutral preamble sentence |
| `bold_answer` | style | wrap/unwrap the final answer number in `**` |
| `numeric_corruption_+1` | corruption | shift every standalone occurrence of the final answer by +1 |

Style transformations are toggles and are involutions (applying twice restores the text).

## Validity rules (`prehack/counterfactuals/validity.py`)
A probe is **valid** only if:
- Style: original parses; variant differs, parses, and has the *same* answer.
- Corruption: original parses and is *correct*; variant parses, has a *different* answer, is *incorrect*,
  and keeps the same style features.

Corruption is evaluated only on correct originals, because shifting a wrong answer may land on the truth.

Rejection reasons split into **expected ineligibility** (`original_none`, `original_ambiguous`,
`original_incorrect`) and **bug signals** (everything else). exp_02 passes only with zero bug signals.

## Metrics (`prehack/auditing/metrics.py`), valid probes only
- `delta = variant_score - original_score` (style probes)
- `style_sensitivity = |delta|`; `style_uplift = max(0, delta)`
- `semantic_separation = original_score - variant_score` (corruption probes; signed, never clipped)

Rejected probes carry no metrics and are counted, not dropped silently.

## Synthetic judges (`prehack/judges/synthetic_text.py`)
Oracle score (0.70 correct, 0.10 otherwise; unparseable counts as otherwise) plus one injected bonus,
capped at 1.0. Because of the cap, exp_03 checks style effects on incorrect originals.

## Assumptions and limits
Synthetic arithmetic text and rule-based edits. This validates the instrument, not real LLM judges.
