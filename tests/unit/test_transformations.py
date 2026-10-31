import random
import unittest
from prehack.core import Problem
from prehack.counterfactuals.corruption import NumericCorruption
from prehack.counterfactuals.style import BoldAnswer, ConfidenceToggle, VerbosityToggle
from prehack.tasks.arithmetic import (CONF_PHRASE, PREAMBLE, TEMPLATES, make_problem, render,
                                      sample_response)
from prehack.verifiers.parsing import parse_final_answer

P = Problem('p', 20, 27)


class TransformationTests(unittest.TestCase):
    def test_toggles_are_involutions(self):
        for template in range(len(TEMPLATES)):
            for flags in range(8):
                text = render(P, 47, confident=bool(flags & 1), verbose=bool(flags & 2),
                              bold=bool(flags & 4), template=template)
                for t in (ConfidenceToggle(), VerbosityToggle(), BoldAnswer()):
                    once = t.apply(text)
                    self.assertNotEqual(once, text)
                    self.assertEqual(t.apply(once), text, (t.name, text))

    def test_style_preserves_parsed_answer(self):
        rng = random.Random(1)
        for i in range(300):
            p = make_problem(rng, str(i))
            text = sample_response(p, rng)
            before = parse_final_answer(text)
            for t in (ConfidenceToggle(), VerbosityToggle(), BoldAnswer()):
                after = parse_final_answer(t.apply(text))
                self.assertEqual((before.status, before.value), (after.status, after.value))

    def test_confidence_and_verbosity_order(self):
        text = render(P, 47, confident=True)
        self.assertTrue(VerbosityToggle().apply(text).startswith(CONF_PHRASE + PREAMBLE))

    def test_bold_inapplicable_when_unparseable(self):
        self.assertIsNone(BoldAnswer().apply('I cannot determine the sum.'))

    def test_corruption_changes_all_occurrences(self):
        text = render(P, 47)
        self.assertEqual(NumericCorruption(1).apply(text), render(P, 48))
        self.assertEqual(NumericCorruption(-1).apply(text), render(P, 46))
        self.assertIsNone(NumericCorruption(1).apply('no answer here'))
        with self.assertRaises(ValueError):
            NumericCorruption(0)

    def test_corruption_does_not_touch_partial_numbers(self):
        p = Problem('q', 4, 7)  # truth 11; operands do not collide, digits '1' inside '11' must stay
        text = 'Adding 4 and 7 gives 11. Final answer: 11'
        self.assertEqual(NumericCorruption(1).apply(text), 'Adding 4 and 7 gives 12. Final answer: 12')


if __name__ == '__main__':
    unittest.main()
