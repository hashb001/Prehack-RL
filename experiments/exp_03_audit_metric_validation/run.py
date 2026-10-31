#!/usr/bin/env python3
"""Experiment 03: do the audit metrics recover the bias we injected?

Four synthetic text judges with known bias (none / confidence / verbosity / bold).
Checks (all must pass):
  style_effect          mean style sensitivity on valid probes of INCORRECT originals equals the
                        injected bonus for the matching transformation and 0 for the others
                        (incorrect originals avoid the score cap at 1.0)
  semantic_separation   every valid corruption probe equals the analytic expectation
  invalid_have_no_metrics  rejected probes never contribute metric values
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from prehack.auditing.aggregate import summarize                           # noqa: E402
from prehack.auditing.campaign import collect                              # noqa: E402
from prehack.auditing.probes import DEFAULT_TRANSFORMS                     # noqa: E402
from prehack.counterfactuals.base import CORRUPTION, STYLE                 # noqa: E402
from prehack.judges.synthetic_text import DEFAULT_JUDGES                   # noqa: E402
from prehack.tasks.arithmetic import has_feature                           # noqa: E402
from prehack.tracking.outputs import (base_manifest, prepare_dirs, relative, validate_run_id,  # noqa: E402
                                      write_csv, write_json, write_jsonl)

EXP = 'exp_03_audit_metric_validation'
TOL = 1e-9
STYLE_FEATURE = {t.name: t.feature for t in DEFAULT_TRANSFORMS if t.kind == STYLE}


def expected_separation(judge, original: str) -> float:
    """Analytic score(correct) - score(wrong) for a corruption that preserves style."""
    b = judge.bonus if judge.bias_feature and has_feature(original, judge.bias_feature) else 0.0
    return min(1.0, 0.70 + b) - min(1.0, 0.10 + b)


def compute_checks(records, judges) -> list[dict]:
    by_name = {j.name: j for j in judges}
    checks = []
    for judge in judges:
        for name, feature in STYLE_FEATURE.items():
            rs = [r for r in records if r['judge'] == judge.name and r['transformation'] == name
                  and r['kind'] == STYLE and r['valid'] and r['original_correct'] is False]
            expected = judge.bonus if judge.bias_feature == feature else 0.0
            observed = sum(r['style_sensitivity'] for r in rs) / len(rs) if rs else None
            checks.append({'check': 'style_effect', 'judge': judge.name, 'transformation': name,
                           'n': len(rs), 'expected': expected, 'observed': observed,
                           'passed': observed is not None and abs(observed - expected) < TOL})
        rs = [r for r in records if r['judge'] == judge.name and r['kind'] == CORRUPTION and r['valid']]
        err = max((abs(r['semantic_separation'] - expected_separation(by_name[r['judge']], r['original']))
                   for r in rs), default=None)
        checks.append({'check': 'semantic_separation_max_abs_error', 'judge': judge.name,
                       'transformation': 'all_corruptions', 'n': len(rs), 'expected': 0.0,
                       'observed': err, 'passed': err is not None and err < TOL})
    invalid = [r for r in records if not r['valid']]
    leaked = sum(any(r[k] is not None for k in ('style_sensitivity', 'style_uplift', 'semantic_separation'))
                 for r in invalid)
    checks.append({'check': 'invalid_have_no_metrics', 'judge': 'all', 'transformation': 'all',
                   'n': len(invalid), 'expected': 0, 'observed': leaked, 'passed': leaked == 0})
    return checks


def run(problems, seeds, runs_root, results_root, run_id, responses=4, messy_rate=0.1) -> dict:
    if problems < 1 or responses < 1 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Use positive counts and distinct seeds')
    if not 0.0 <= messy_rate <= 1.0:
        raise ValueError('messy_rate must be in [0, 1]')
    validate_run_id(run_id)
    raw, res = prepare_dirs([Path(runs_root) / EXP / run_id, Path(results_root) / EXP / run_id])

    records = collect(seeds, problems, responses, DEFAULT_JUDGES, messy_rate)
    write_jsonl(raw / 'probes.jsonl', records)
    summary = summarize(records, ('judge', 'transformation'))
    checks = compute_checks(records, DEFAULT_JUDGES)
    failed = sum(not c['passed'] for c in checks)
    write_csv(res / 'summary.csv', summary)
    write_csv(res / 'checks.csv', checks)
    write_json(res / 'manifest.json', base_manifest(
        PROJECT_ROOT, EXP, run_id, __file__, seeds=seeds, problems_per_seed=problems,
        responses_per_problem=responses, messy_rate=messy_rate,
        transformations=[t.name for t in DEFAULT_TRANSFORMS],
        judges=[{'name': j.name, 'bias_feature': j.bias_feature, 'bonus': j.bonus} for j in DEFAULT_JUDGES],
        failed_checks=failed,
        artifacts={'summary': 'summary.csv', 'checks': 'checks.csv', 'report': 'report.md',
                   'raw_records': relative(raw / 'probes.jsonl', res)},
        limitations='Synthetic judges with injected bias; shows the metrics are correct, not that '
                    'real LLM judges behave this way.'))

    f = lambda x: 'N/A' if x is None else f'{x:.4f}'
    lines = [f'# {EXP}', '', 'Metric recovery on synthetic text judges with known bias (no LLM).', '',
             f'{problems} problems x {responses} responses per seed; seeds {seeds}; messy rate {messy_rate}.', '',
             '| Check | Judge | Transformation | n | Expected | Observed | Passed |',
             '|---|---|---|---:|---:|---:|---|']
    for c in checks:
        lines.append(f"| {c['check']} | {c['judge']} | {c['transformation']} | {c['n']} | "
                     f"{f(c['expected'])} | {f(c['observed'])} | {c['passed']} |")
    lines += ['', f'**Failed checks: {failed}**']
    report = '\n'.join(lines) + '\n'
    (res / 'report.md').write_text(report)
    print(report)
    print(f'Raw records: {raw}\nResults: {res}')
    return {'summary': summary, 'checks': checks, 'failed': failed}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--problems', type=int, default=200, help='problems per seed')
    p.add_argument('--responses', type=int, default=4, help='responses per problem')
    p.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44])
    p.add_argument('--messy-rate', type=float, default=0.1)
    p.add_argument('--run-id', default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    p.add_argument('--runs-root', type=Path, default=PROJECT_ROOT / 'runs')
    p.add_argument('--results-root', type=Path, default=PROJECT_ROOT / 'results')
    a = p.parse_args(argv)
    try:
        out = run(a.problems, a.seeds, a.runs_root, a.results_root, a.run_id, a.responses, a.messy_rate)
    except (ValueError, FileExistsError) as exc:
        p.error(str(exc))
    return 1 if out['failed'] else 0


if __name__ == '__main__':
    sys.exit(main())
