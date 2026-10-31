# exp_02 — Transformation Validation

**Question:** How often are counterfactual transformations valid, and why do the rest fail?

**Design:** Synthetic arithmetic responses (including deliberately messy ones) are passed through
3 style transformations and 1 corruption. Each variant is validated; rejections are counted by reason.

**Command (from repo root):**
```bash
python3 experiments/exp_02_transform_validation/run.py --problems 500 --seeds 42 43 44 --run-id first
```
Outputs: `runs/exp_02_transform_validation/<run-id>/probes.jsonl` and
`results/exp_02_transform_validation/<run-id>/{summary.csv,rejections.csv,report.md,manifest.json}`.

**Pass criterion:** zero *unexpected* rejections (exit code 0). Expected ones are messy originals and,
for corruption, already-incorrect originals.

**Limits:** synthetic text, rule-based edits, integer answers only. No LLM involved.
