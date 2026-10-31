import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(folder, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'experiments' / folder / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXP02 = load('exp_02_transform_validation', 'exp02_run')
EXP03 = load('exp_03_audit_metric_validation', 'exp03_run')


class ExperimentTests(unittest.TestCase):
    def check_experiment(self, module, files):
        with tempfile.TemporaryDirectory() as d, redirect_stdout(io.StringIO()):
            roots = [Path(d) / 'a', Path(d) / 'b']
            outs = [module.run(30, [7, 8], r / 'runs', r / 'results', 'repro') for r in roots]
            for name in files:
                self.assertEqual((roots[0] / name).read_bytes(), (roots[1] / name).read_bytes(), name)
            with self.assertRaises(FileExistsError):
                module.run(30, [7], roots[0] / 'runs', roots[0] / 'results', 'repro')
            return outs[0]

    def test_exp02_reproducible_and_clean(self):
        e = module = EXP02.EXP
        out = self.check_experiment(EXP02, [f'runs/{e}/repro/probes.jsonl', f'results/{e}/repro/summary.csv',
                                            f'results/{e}/repro/rejections.csv', f'results/{e}/repro/report.md',
                                            f'results/{e}/repro/manifest.json'])
        self.assertEqual(out['unexpected'], 0)

    def test_exp03_reproducible_and_all_checks_pass(self):
        e = EXP03.EXP
        out = self.check_experiment(EXP03, [f'runs/{e}/repro/probes.jsonl', f'results/{e}/repro/summary.csv',
                                            f'results/{e}/repro/checks.csv', f'results/{e}/repro/report.md',
                                            f'results/{e}/repro/manifest.json'])
        self.assertEqual(out['failed'], 0, [c for c in out['checks'] if not c['passed']])

    def test_collision_creates_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            taken = root / 'results' / EXP02.EXP / 'x'
            taken.mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                EXP02.run(5, [1], root / 'runs', root / 'results', 'x')
            self.assertFalse((root / 'runs').exists())

    def test_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            for args in [(0, [1]), (1, []), (1, [1, 1])]:
                with self.assertRaises(ValueError):
                    EXP02.run(*args, Path(d) / 'runs', Path(d) / 'results', 'bad')
            with self.assertRaises(ValueError):
                EXP02.run(1, [1], Path(d) / 'runs', Path(d) / 'results', 'bad/id')


if __name__ == '__main__':
    unittest.main()
