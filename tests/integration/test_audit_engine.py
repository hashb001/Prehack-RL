import unittest
from prehack.auditing.aggregate import rejection_counts, summarize
from prehack.auditing.campaign import collect
from prehack.judges.synthetic_text import DEFAULT_JUDGES


class AuditEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = collect([1, 2], 40, 3, DEFAULT_JUDGES, messy_rate=0.2)

    def test_deterministic(self):
        self.assertEqual(self.records, collect([1, 2], 40, 3, DEFAULT_JUDGES, messy_rate=0.2))

    def test_only_expected_rejections(self):
        bad = [r for r in rejection_counts(self.records) if not r['expected']]
        self.assertEqual(bad, [])

    def test_rejected_probes_have_no_metrics_and_valid_ones_do(self):
        for r in self.records:
            vals = (r['style_sensitivity'], r['style_uplift'], r['semantic_separation'])
            self.assertEqual(any(v is not None for v in vals), r['valid'])
            self.assertEqual(r['variant_score'] is not None, r['valid'])

    def test_judges_see_identical_responses(self):
        by_judge = {}
        for r in self.records:
            by_judge.setdefault(r['judge'], []).append(r['original'])
        lists = list(by_judge.values())
        self.assertTrue(all(l == lists[0] for l in lists))

    def test_control_judge_is_style_blind(self):
        rows = [r for r in summarize(self.records) if r['judge'] == 'control' and r['mean_style_sensitivity'] is not None]
        self.assertTrue(rows)
        for r in rows:
            self.assertAlmostEqual(r['mean_style_sensitivity'], 0.0)

    def test_invalid_arguments(self):
        for args in [([], 1, 1), ([1, 1], 1, 1), ([1], 0, 1), ([1], 1, 0)]:
            with self.assertRaises(ValueError):
                collect(*args, DEFAULT_JUDGES)
        with self.assertRaises(ValueError):
            collect([1], 1, 1, DEFAULT_JUDGES, messy_rate=1.5)


if __name__ == '__main__':
    unittest.main()
