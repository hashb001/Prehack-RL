import unittest
from prehack.core import Problem
from prehack.counterfactuals.validity import check_corruption, check_style
from prehack.tasks.arithmetic import render, render_messy

P = Problem('p', 20, 27)   # truth 47


class ValidityTests(unittest.TestCase):
    def test_style_valid(self):
        self.assertEqual(check_style(P, render(P, 47), render(P, 47, confident=True)).reason, 'ok')
        self.assertTrue(check_style(P, render(P, 45), render(P, 45, bold=True)).valid)  # wrong originals ok

    def test_style_rejections(self):
        orig = render(P, 47)
        self.assertEqual(check_style(P, orig, orig).reason, 'no_change')
        self.assertEqual(check_style(P, orig, None).reason, 'not_applicable')
        self.assertEqual(check_style(P, orig, render(P, 48)).reason, 'answer_changed')
        self.assertEqual(check_style(P, orig, 'I cannot determine the sum.').reason, 'variant_none')
        self.assertEqual(check_style(P, orig, render_messy(47, 1)).reason, 'variant_ambiguous')
        self.assertEqual(check_style(P, render_messy(47, 0), orig).reason, 'original_none')
        self.assertEqual(check_style(P, render_messy(47, 1), orig).reason, 'original_ambiguous')

    def test_corruption_valid(self):
        self.assertTrue(check_corruption(P, render(P, 47, confident=True),
                                         render(P, 48, confident=True)).valid)

    def test_corruption_rejections(self):
        orig = render(P, 47)
        self.assertEqual(check_corruption(P, render(P, 45), render(P, 46)).reason, 'original_incorrect')
        self.assertEqual(check_corruption(P, render_messy(47, 0), orig).reason, 'original_none')
        self.assertEqual(check_corruption(P, orig, None).reason, 'not_applicable')
        self.assertEqual(check_corruption(P, orig, orig).reason, 'answer_unchanged')
        self.assertEqual(check_corruption(P, orig, 'nothing').reason, 'variant_none')
        # a "corruption" that lands on the truth for a different parse path is still caught
        self.assertEqual(check_corruption(P, render(P, 47, template=1),
                                          render(P, 47, template=2)).reason, 'answer_unchanged')
        self.assertEqual(check_corruption(P, orig, render(P, 48, confident=True)).reason, 'style_changed')


if __name__ == '__main__':
    unittest.main()
