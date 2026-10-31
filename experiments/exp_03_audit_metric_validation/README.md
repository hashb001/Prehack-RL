# exp_03 — Audit Metric Validation

**Question:** Do the audit metrics recover the bias we injected, rather than reflecting parsing or
transformation artifacts?

**Design:** Four synthetic text judges (control, confidence, verbosity, bold). Compare measured
style effects and semantic separation with analytic expectations.

**Command (from repo root):**
```bash
python3 experiments/exp_03_audit_metric_validation/run.py --problems 200 --seeds 42 43 44 --run-id first
```
Outputs: `runs/exp_03_audit_metric_validation/<run-id>/probes.jsonl` and
`results/exp_03_audit_metric_validation/<run-id>/{summary.csv,checks.csv,report.md,manifest.json}`.

**Pass criterion:** all checks in `checks.csv` pass (exit code 0).

**Limits:** shows the instrument is correct on known synthetic bias. It says nothing about real LLM judges.
