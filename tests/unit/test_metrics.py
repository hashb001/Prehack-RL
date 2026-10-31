import unittest
from prehack.auditing.aggregate import rejection_counts, summarize
from prehack.auditing.metrics import mean_or_none, probe_metrics
from prehack.auditing.probes import run_probes
from prehack.core import Problem
from prehack.judges.synthetic_text import DEFAULT_JUDGES, SyntheticTextJudge
from prehack.tasks.arithmetic import render, render_messy

P = Problem('p', 20, 27)
CONTROL, CONF = DEFAULT_JUDGES[0], DEFAULT_JUDGES[1]


class MetricTests(unittest.TestCase):
    def test_probe_metrics(self):
        m = probe_metrics('style', 0.10, 0.75)
        self.assertAlmostEqual(m['style_sensitivity'], 0.65)
        self.assertAlmostEqual(m['style_uplift'], 0.65)
        m = probe_metrics('style', 0.75, 0.10)
        self.assertAlmostEqual(m['style_sensitivity'], 0.65)
        self.assertEqual(m['style_uplift'], 0.0)
        self.assertAlmostEqual(probe_metrics('corruption', 0.7, 0.1)['semantic_separation'], 0.6)
        self.assertLess(probe_metrics('corruption', 0.1, 0.75)['semantic_separation'], 0)  # not clipped
        self.assertEqual(set(probe_metrics('style', 0.1, None).values()), {None})
        with self.assertRaises(ValueError):
            probe_metrics('other', 0.1, 0.2)

    def test_mean_or_none(self):
        self.assertIsNone(mean_or_none([None, None]))
        self.assertEqual(mean_or_none([1.0, None, 3.0]), 2.0)

    def test_judge_scores_and_rank_reversal(self):
        right, wrong = render(P, 47), render(P, 48, confident=True)
        self.assertGreater(CONTROL.score(P, right), CONTROL.score(P, wrong))
        self.assertAlmostEqual(CONF.score(P, wrong), 0.75)
        self.assertGreater(CONF.score(P, wrong), CONF.score(P, right))
        self.assertEqual(CONF.score(P, render(P, 47, confident=True)), 1.0)       # capped
        self.assertEqual(CONTROL.score(P, render_messy(47, 0)), 0.10)             # unparseable
        with self.assertRaises(ValueError):
            SyntheticTextJudge('bad', 'nonsense', 0.1)

    def test_probes_on_known_case(self):
        rows = {r['transformation']: r for r in run_probes(P, render(P, 48), CONF)}   # wrong, concise
        self.assertAlmostEqual(rows['confidence_toggle']['style_uplift'], 0.65)
        self.assertEqual(rows['verbosity_toggle']['style_sensitivity'], 0)
        self.assertEqual(rows['numeric_corruption_+1']['reason'], 'original_incorrect')
        self.assertIsNone(rows['numeric_corruption_+1']['semantic_separation'])
        rows = {r['transformation']: r for r in run_probes(P, render(P, 47, confident=True), CONF)}
        self.assertAlmostEqual(rows['numeric_corruption_+1']['semantic_separation'], 0.25)

    def test_aggregate(self):
        recs = (run_probes(P, render(P, 47), CONTROL) + run_probes(P, render_messy(47, 0), CONTROL))
        rows = summarize(recs, ('transformation',))
        by = {r['transformation']: r for r in rows}
        self.assertEqual(by['confidence_toggle']['probes'], 2)
        self.assertEqual(by['confidence_toggle']['valid'], 1)
        self.assertAlmostEqual(by['confidence_toggle']['rejection_rate'], 0.5)
        self.assertAlmostEqual(by['numeric_corruption_+1']['mean_semantic_separation'], 0.6)
        self.assertEqual(sum(r['count'] for r in rejection_counts(recs)), sum(not r['valid'] for r in recs))
        self.assertTrue(all(r['expected'] for r in rejection_counts(recs)))


if __name__ == '__main__':
    unittest.main()
