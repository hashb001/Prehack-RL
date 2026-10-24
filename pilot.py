#!/usr/bin/env python3
"""Run synthetic Best-of-N and counterfactual checks using only Python stdlib."""
import argparse
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
import platform
import random
from statistics import mean
from prehack.core import (Problem, Response, SyntheticJudge, audit, expected_accuracy,
                          sample_candidates, select_best, verify)

NS = [1, 2, 4, 8, 16, 32]
PROJECT_ROOT = Path(__file__).resolve().parent
EXP00 = 'exp_00_synthetic_best_of_n'
EXP01 = 'exp_01_synthetic_counterfactual_audit'

JUDGES = [SyntheticJudge('control'), SyntheticJudge('confidence_biased', 0.65)]

def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(trials: int, seeds: list[int], output: Path,
        results_root: Path | None = None, run_id: str | None = None) -> list[dict]:
    if trials < 1 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Use positive trials and distinct seeds')
    output = Path(output).resolve()
    results_root = Path(results_root or PROJECT_ROOT / 'results').resolve()
    run_id = run_id or output.name
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', run_id):
        raise ValueError('Run ID must contain only letters, numbers, dots, underscores, or hyphens')
    result00 = results_root / EXP00 / run_id
    result01 = results_root / EXP01 / run_id
    destinations = [output, result00, result01]
    for i, path in enumerate(destinations):
        for other in destinations[i + 1:]:
            if path == other or path in other.parents or other in path.parents:
                raise ValueError('Raw and result destinations must be separate, non-nested directories')
    # Preflight all destinations before creating any run directories.
    for path in destinations:
        if path.exists():
            raise FileExistsError(f'Refusing to overwrite existing run: {path}')
    for path in destinations:
        path.mkdir(parents=True, exist_ok=False)
    summaries = []
    audit_summaries = []
    with (output / 'trials.jsonl').open('w') as raw, (output / 'audits.jsonl').open('w') as audits:
        for seed in seeds:
            rng = random.Random(seed)
            audit_buckets = {}
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
                            row = {'seed': seed, **audit(p, response, judge)}
                            audits.write(json.dumps(row) + '\n')
                            audit_buckets.setdefault((judge.name, correct, confident), []).append(row)
                raw.write(json.dumps({'seed': seed, 'problem_id': p.id, 'a': p.a, 'b': p.b,
                                     'truth': p.truth,
                                     'candidates': [r.__dict__ for r in candidates],
                                     'selections': selections}) + '\n')
            for (judge, correct, confident), rows in audit_buckets.items():
                eligible = [r['semantic_separation'] for r in rows if r['semantic_eligible']]
                audit_summaries.append({
                    'seed': seed, 'judge': judge, 'original_correct': correct,
                    'original_confident': confident, 'probe_count': len(rows),
                    'valid_style_count': sum(r['style_valid'] for r in rows),
                    'semantic_eligible_count': len(eligible),
                    'mean_style_sensitivity': mean(r['style_sensitivity'] for r in rows),
                    'mean_style_uplift': mean(r['style_uplift'] for r in rows),
                    'mean_semantic_separation': mean(eligible) if eligible else None,
                })
            for (judge, n), records in buckets.items():
                summaries.append({'seed': seed, 'judge': judge, 'n': n, 'trials': trials,
                                  'accuracy': mean(r['correct'] for r in records),
                                  'proxy_reward': mean(r['proxy_reward'] for r in records),
                                  'confident_fraction': mean(r['confident'] for r in records),
                                  'expected_accuracy': expected_accuracy(n, judge != 'control')})
    write_csv(result00 / 'summary.csv', summaries)
    write_csv(result01 / 'summary.csv', audit_summaries)
    source = Path(__file__).resolve().parent
    hashes = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [source / 'pilot.py', source / 'prehack/core.py']}
    manifest = {'schema_version': 2, 'run_id': run_id, 'experiments': [EXP00, EXP01], 'python': platform.python_version(),
                'trials_per_seed': trials, 'seeds': seeds, 'candidate_counts': NS,
                'response_probabilities': [0.55, 0.35, 0.10], 'confidence_bonus': 0.65,
                'tie_break': 'first maximum', 'paired_candidates': True, 'source_sha256': hashes,
                'limitations': 'Synthetic oracle-based judge; no LLM, RL, or predictive claim.'}
    def relative(target, base):
        return Path(os.path.relpath(target, base)).as_posix()

    manifest['artifacts'] = {
        'trials': 'trials.jsonl', 'audits': 'audits.jsonl',
        'best_of_n_results': relative(result00, output),
        'audit_results': relative(result01, output),
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for folder, experiment, raw_name in ((result00, EXP00, 'trials.jsonl'),
                                         (result01, EXP01, 'audits.jsonl')):
        result_manifest = {**manifest, 'experiment': experiment,
                           'artifacts': {'summary': 'summary.csv', 'report': 'report.md',
                                         'raw_records': relative(output / raw_name, folder),
                                         'raw_manifest': relative(output / 'manifest.json', folder)}}
        (folder / 'manifest.json').write_text(json.dumps(result_manifest, indent=2) + '\n')
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
    lines += ['', 'Synthetic selection only: no policy training or real LLM judge.',
              'The candidate distribution deliberately excludes correct confident answers.']
    report = '\n'.join(lines) + '\n'
    (result00 / 'report.md').write_text(report)
    audit_lines = ['# Experiment 01: synthetic counterfactual audit', '',
                   'Computed from recorded probes; no LLM, prediction, or intervention claim.', '',
                   'Semantic degradation is evaluated only for correct originals. N/A denotes ineligible probes.', '',
                   '| Seed | Judge | Correct | Confident | Probes | Valid style | Semantic eligible | Style sensitivity | Uplift | Semantic separation |',
                   '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for row in audit_summaries:
        separation = row['mean_semantic_separation']
        gap = f'{separation:.4f}' if separation is not None else 'N/A'
        audit_lines.append(
            f"| {row['seed']} | {row['judge']} | {row['original_correct']} | "
            f"{row['original_confident']} | {row['probe_count']} | {row['valid_style_count']} | "
            f"{row['semantic_eligible_count']} | {row['mean_style_sensitivity']:.4f} | "
            f"{row['mean_style_uplift']:.4f} | {gap} |")
    (result01 / 'report.md').write_text('\n'.join(audit_lines) + '\n')
    print(report)
    print(f'Raw records: {output}\nExperiment 00 results: {result00}\nExperiment 01 results: {result01}')
    return summaries

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int, default=2000)
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44])
    parser.add_argument('--run-id', default=None,
                        help='Unique run name; defaults to a UTC timestamp')
    parser.add_argument('--runs-root', type=Path, default=PROJECT_ROOT / 'runs')
    parser.add_argument('--results-root', type=Path, default=PROJECT_ROOT / 'results')
    parser.add_argument('--output', type=Path, default=None,
                        help='Optional explicit raw-run directory (legacy flag)')
    args = parser.parse_args()
    run_id = args.run_id or (args.output.name if args.output else
                            datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    raw_output = args.output if args.output else args.runs_root / run_id
    try:
        run(args.trials, args.seeds, raw_output, args.results_root, run_id)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
