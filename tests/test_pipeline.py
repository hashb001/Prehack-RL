import io
import json
import random
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from prehack.core import *
from pilot import run, EXP00, EXP01

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.p = Problem('example', 6, 4)
        self.control = SyntheticJudge('control')
        self.biased = SyntheticJudge('confidence_biased', .65)

    def test_rank_reversal(self):
        choices = [Response(10), Response(11, True)]
        self.assertTrue(verify(self.p, select_best(self.p, choices, self.control)))
        self.assertFalse(verify(self.p, select_best(self.p, choices, self.biased)))
        self.assertAlmostEqual(self.biased.score(self.p, choices[1]), .75)

    def test_probe_validity(self):
        for judge in (self.control, self.biased):
            for answer in (10, 11):
                for confident in (True, False):
                    row = audit(self.p, Response(answer, confident), judge)
                    self.assertTrue(row['style_valid'])
                    self.assertEqual(row['semantic_eligible'], answer == 10)
                    if answer != 10:
                        self.assertIsNone(row['semantic_separation'])
                        self.assertIsNone(row['corrupted_variant'])
        self.assertAlmostEqual(audit(self.p, Response(10, True), self.biased)['semantic_separation'], .25)
        self.assertEqual(audit(self.p, Response(10, True), self.biased)['style_uplift'], 0)
        self.assertAlmostEqual(audit(self.p, Response(11), self.biased)['style_uplift'], .65)

    def test_sampling_matches_exact_probabilities(self):
        rng = random.Random(123)
        for n in (1, 2, 8):
            counts = [0, 0]
            for _ in range(10000):
                candidates = sample_candidates(self.p, n, rng)
                for i, judge in enumerate((self.control, self.biased)):
                    counts[i] += verify(self.p, select_best(self.p, candidates, judge))
            for i in (0, 1):
                self.assertAlmostEqual(counts[i] / 10000, expected_accuracy(n, bool(i)), delta=.025)

    def test_results_replay_and_reproduce(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            paths = [Path(directory) / name for name in ('a', 'b')]
            for path in paths:
                run(12, [7, 8], path / 'runs/repro', path / 'results')
            for name in ('runs/repro/trials.jsonl', 'runs/repro/audits.jsonl', 'runs/repro/manifest.json',
                         f'results/{EXP00}/repro/summary.csv', f'results/{EXP01}/repro/summary.csv',
                         f'results/{EXP00}/repro/manifest.json', f'results/{EXP01}/repro/manifest.json',
                         f'results/{EXP00}/repro/report.md', f'results/{EXP01}/repro/report.md'):
                self.assertEqual((paths[0] / name).read_bytes(), (paths[1] / name).read_bytes())
            for line in (paths[0] / 'runs/repro/trials.jsonl').read_text().splitlines():
                record = json.loads(line)
                problem = Problem(record['problem_id'], record['a'], record['b'])
                candidates = [Response(**r) for r in record['candidates']]
                for selected in record['selections']:
                    judge = self.control if selected['judge'] == 'control' else self.biased
                    actual = select_best(problem, candidates[:selected['n']], judge)
                    self.assertEqual(actual.answer, selected['answer'])
                    self.assertEqual(actual.confident, selected['confident'])
                    self.assertEqual(judge.score(problem, actual), selected['proxy_reward'])
            with self.assertRaises(FileExistsError):
                run(12, [7], paths[0] / 'runs/repro', paths[0] / 'results')

    def test_exported_audit_matches_raw_and_manifest_links(self):
        import csv
        from statistics import mean
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            root = Path(directory)
            raw = root / 'runs/check'
            results = root / 'results'
            run(7, [11], raw, results)
            self.assertEqual({p.name for p in raw.iterdir()},
                             {'trials.jsonl', 'audits.jsonl', 'manifest.json'})
            records = [json.loads(line) for line in (raw / 'audits.jsonl').read_text().splitlines()]
            folder = results / EXP01 / 'check'
            with (folder / 'summary.csv').open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 8)
            for row in rows:
                selected = [r for r in records if r['judge'] == row['judge']
                            and r['original_correct'] == (row['original_correct'] == 'True')
                            and r['original'].startswith('I am absolutely certain.') ==
                            (row['original_confident'] == 'True')]
                self.assertEqual(len(selected), int(row['probe_count']))
                self.assertAlmostEqual(float(row['mean_style_sensitivity']),
                                       mean(r['style_sensitivity'] for r in selected))
                gaps = [r['semantic_separation'] for r in selected if r['semantic_eligible']]
                if gaps:
                    self.assertAlmostEqual(float(row['mean_semantic_separation']), mean(gaps))
                else:
                    self.assertEqual(row['mean_semantic_separation'], '')
            for experiment in (EXP00, EXP01):
                folder = results / experiment / 'check'
                metadata = json.loads((folder / 'manifest.json').read_text())
                for target in metadata['artifacts'].values():
                    self.assertTrue((folder / target).is_file())

    def test_result_collision_does_not_create_raw_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / 'results' / EXP01 / 'taken'
            existing.mkdir(parents=True)
            (existing / 'keep.txt').write_text('preserve')
            with self.assertRaises(FileExistsError):
                run(2, [1], root / 'runs/taken', root / 'results')
            self.assertFalse((root / 'runs/taken').exists())
            self.assertFalse((root / 'results' / EXP00 / 'taken').exists())
            self.assertEqual((existing / 'keep.txt').read_text(), 'preserve')

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            select_best(self.p, [], self.control)
        with tempfile.TemporaryDirectory() as directory:
            for trials, seeds in [(0, [1]), (1, []), (1, [1, 1])]:
                with self.assertRaises(ValueError):
                    run(trials, seeds, Path(directory) / 'invalid')

if __name__ == '__main__':
    unittest.main()
