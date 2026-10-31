import unittest
from prehack.verifiers.parsing import parse_final_answer


class ParsingTests(unittest.TestCase):
    def ok(self, text, value):
        r = parse_final_answer(text)
        self.assertEqual((r.status, r.value), ('ok', value), text)
        return r

    def test_common_formats(self):
        for text in ('Final answer: 47', 'The answer is 47.', 'Answer: **47**',
                     r'Therefore, the result is \boxed{47}.', r'\boxed{**47**}', 'answer = 47',
                     'FINAL ANSWER: 47'):
            self.ok(text, 47)

    def test_span_points_at_digits(self):
        for text in ('Final answer: 47', r'\boxed{**47**}', 'Answer: **47**'):
            r = parse_final_answer(text)
            self.assertEqual(text[r.span[0]:r.span[1]], '47')

    def test_stray_numbers_ignored(self):
        self.ok('Adding 5 and 6 gives 12. Final answer: 11', 11)

    def test_negative_and_commas(self):
        self.ok('Answer: -3', -3)
        self.ok('Answer: 1,234', 1234)

    def test_repeated_same_answer_is_ok(self):
        self.ok('Answer: 47. Double-checking, the answer is 47.', 47)

    def test_failures_are_explicit(self):
        self.assertEqual(parse_final_answer('I cannot determine the sum.').status, 'none')
        self.assertEqual(parse_final_answer('I think it is around 47.').status, 'none')
        self.assertEqual(parse_final_answer('Answer: 47.5').status, 'none')
        self.assertEqual(parse_final_answer('Final answer: 47. Actually, wait. Final answer: 48.').status,
                         'ambiguous')
        self.assertEqual(parse_final_answer(r'Answer: 5 \boxed{6}').status, 'ambiguous')
        self.assertIsNone(parse_final_answer('nothing').value)


if __name__ == '__main__':
    unittest.main()
