#!/usr/bin/env python3
"""Experiment 02: how often are counterfactual transformations valid, and why do the rest fail?

Pass criterion: every rejection is an *expected ineligibility* (messy original or, for
corruption, an already-incorrect original). Any other reason is a transformation/parser bug.
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from prehack.auditing.aggregate import rejection_counts, summarize        # noqa: E402
from prehack.auditing.campaign import collect                              # noqa: E402
from prehack.auditing.probes import DEFAULT_TRANSFORMS                     # noqa: E402
from prehack.judges.synthetic_text import DEFAULT_JUDGES                   # noqa: E402
from prehack.tracking.outputs import (base_manifest, prepare_dirs, relative, validate_run_id,  # noqa: E402
                                      write_csv, write_json, write_jsonl)

EXP = 'exp_02_transform_validation'
CONTROL = DEFAULT_JUDGES[0]


def run(problems, seeds, runs_root, results_root, run_id, responses=4, messy_rate=0.1) -> dict:
    if problems < 1 or responses < 1 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Use positive counts and distinct seeds')
    if not 0.0 <= messy_rate <= 1.0:
        raise ValueError('messy_rate must be in [0, 1]')
    validate_run_id(run_id)
    raw, res = prepare_dirs([Path(runs_root) / EXP / run_id, Path(results_root) / EXP / run_id])

    records = collect(seeds, problems, responses, [CONTROL], messy_rate)
    write_jsonl(raw / 'probes.jsonl', records)
    summary = summarize(records, ('kind', 'transformation'))
    rejections = rejection_counts(records)
    unexpected = sum(r['count'] for r in rejections if not r['expected'])
    write_csv(res / 'summary.csv', summary)
    write_csv(res / 'rejections.csv', rejections)
    write_json(res / 'manifest.json', base_manifest(
        PROJECT_ROOT, EXP, run_id, __file__, seeds=seeds, problems_per_seed=problems,
        responses_per_problem=responses, messy_rate=messy_rate,
        transformations=[t.name for t in DEFAULT_TRANSFORMS], judge=CONTROL.name,
        unexpected_rejections=unexpected,
        artifacts={'summary': 'summary.csv', 'rejections': 'rejections.csv', 'report': 'report.md',
                   'raw_records': relative(raw / 'probes.jsonl', res)},
        limitations='Synthetic arithmetic text and rule-based transformations; no LLM involved.'))

    lines = [f'# {EXP}', '',
             'Transformation validity on synthetic text (no LLM). '
             f'{problems} problems x {responses} responses per seed; seeds {seeds}; messy rate {messy_rate}.', '',
             '| Kind | Transformation | Probes | Valid | Rejected | Rejection rate |',
             '|---|---|---:|---:|---:|---:|']
    for r in summary:
        lines.append(f"| {r['kind']} | {r['transformation']} | {r['probes']} | {r['valid']} | "
                     f"{r['rejected']} | {r['rejection_rate']:.4f} |")
    lines += ['', '## Rejection reasons', '', '| Transformation | Reason | Count | Expected ineligibility |',
              '|---|---|---:|---|']
    for r in rejections:
        lines.append(f"| {r['transformation']} | {r['reason']} | {r['count']} | {r['expected']} |")
    lines += ['', f'**Unexpected rejections: {unexpected}** '
              '(non-zero means a transformation or parser bug).']
    report = '\n'.join(lines) + '\n'
    (res / 'report.md').write_text(report)
    print(report)
    print(f'Raw records: {raw}\nResults: {res}')
    return {'summary': summary, 'rejections': rejections, 'unexpected': unexpected}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--problems', type=int, default=500, help='problems per seed')
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
    return 1 if out['unexpected'] else 0


if __name__ == '__main__':
    sys.exit(main())
