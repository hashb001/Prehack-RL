#!/usr/bin/env python3
"""Run synthetic Best-of-N and counterfactual checks using only Python stdlib."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import random
from statistics import mean
from prehack.core import (Problem, Response, SyntheticJudge, audit, expected_accuracy,
                          sample_candidates, select_best, verify)

NS = [1, 2, 4, 8, 16, 32]
JUDGES = [SyntheticJudge('control'), SyntheticJudge('confidence_biased', 0.65)]

def run(trials: int, seeds: list[int], output: Path) -> list[dict]:
    if trials < 1 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Use positive trials and distinct seeds')
    # Refuse accidental overwriting of previous experimental records.
    output.mkdir(parents=True, exist_ok=False)
    summaries = []
    with (output / 'trials.jsonl').open('w') as raw, (output / 'audits.jsonl').open('w') as audits:
        for seed in seeds:
            rng = random.Random(seed)
            buckets = {(j.name, n): [] for j in JUDGES for n in NS}
            for index in range(trials):
                p = Problem(f'{seed}-{index}', rng.randint(5, 50), rng.randint(5, 50))
                candidates = sample_candidates(p, max(NS), rng)
                # Same candidate pools across judges and nested prefixes across N.
                selections = []
                for judge in JUDGES:
                    for n in NS:
                        selected = select_best(p, candidates[:n], judge)
                        record = {'judge': judge.name, 'n': n, 'correct': verify(p, selected),
                                  'proxy_reward': judge.score(p, selected),
                                  'answer': selected.answer, 'confident': selected.confident}
                        selections.append(record)
                        buckets[(judge.name, n)].append(record)
                    # Balanced factorial audit probes, separate from selection distribution.
                    for correct in (True, False):
                        for confident in (False, True):
                            response = Response(p.truth if correct else p.truth + 1, confident)
                            audits.write(json.dumps({'seed': seed, **audit(p, response, judge)}) + '\n')
                raw.write(json.dumps({'seed': seed, 'problem_id': p.id, 'a': p.a, 'b': p.b,
                                     'truth': p.truth,
                                     'candidates': [r.__dict__ for r in candidates],
                                     'selections': selections}) + '\n')
            for (judge, n), records in buckets.items():
                summaries.append({'seed': seed, 'judge': judge, 'n': n, 'trials': trials,
                                  'accuracy': mean(r['correct'] for r in records),
                                  'proxy_reward': mean(r['proxy_reward'] for r in records),
                                  'confident_fraction': mean(r['confident'] for r in records),
                                  'expected_accuracy': expected_accuracy(n, judge != 'control')})
    with (output / 'summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    source = Path(__file__).resolve().parent
    hashes = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [source / 'pilot.py', source / 'prehack/core.py']}
    manifest = {'schema_version': 1, 'experiment': 'synthetic_best_of_n', 'python': platform.python_version(),
                'trials_per_seed': trials, 'seeds': seeds, 'candidate_counts': NS,
                'response_probabilities': [0.55, 0.35, 0.10], 'confidence_bonus': 0.65,
                'tie_break': 'first maximum', 'paired_candidates': True, 'source_sha256': hashes,
                'limitations': 'Synthetic oracle-based judge; no LLM, RL, or predictive claim.'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Phase 1: synthetic infrastructure check', '',
             'These results are from a deliberately constructed toy distribution. No LLM or RL training occurred.', '',
             f'{trials} trials per seed; seeds: {seeds}. Judges share candidate pools; N uses nested prefixes.', '',
             '| Judge | N | Mean accuracy | Mean proxy reward | Exact expected accuracy |',
             '|---|---:|---:|---:|---:|']
    for judge in JUDGES:
        for n in NS:
            rows = [r for r in summaries if r['judge'] == judge.name and r['n'] == n]
            lines.append(f"| {judge.name} | {n} | {mean(r['accuracy'] for r in rows):.4f} | "
                         f"{mean(r['proxy_reward'] for r in rows):.4f} | {rows[0]['expected_accuracy']:.4f} |")
    lines += ['', '## Counterfactual sanity checks', '',
              'The control judge has zero style sensitivity and a 0.60 correct–incorrect score gap.',
              'The biased judge gives a wrong confident answer 0.75 versus 0.70 for a correct concise answer.',
              'Style uplift is 0.65 for wrong concise responses and 0.30 for correct concise responses (score clipping).',
              'Matched semantic gaps remain positive: 0.60 for concise and 0.25 for confident responses.',
              'Thus a judge can detect correctness within a style while still misranking answers across styles.', '',
              'Audits include correct/incorrect × confident/concise probes. Incorrect originals are ineligible for semantic degradation.', '',
              '## Next phase', '',
              'Introduce text answer parsing and real policy/judge adapters. Validate transformations and measure natural judge failures.',
              'Then test real Best-of-N and small RL before making claims about prevention or early warning.']
    report = '\n'.join(lines) + '\n'
    (output / 'report.md').write_text(report)
    print(report)
    return summaries

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int, default=2000)
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44])
    parser.add_argument('--output', type=Path, default=Path('runs/phase1'))
    args = parser.parse_args()
    run(args.trials, args.seeds, args.output)
