"""Correctness-changing transformation: shift the final answer, keep presentation."""
import re
from prehack.counterfactuals.base import CORRUPTION
from prehack.verifiers.parsing import parse_final_answer


class NumericCorruption:
    kind = CORRUPTION

    def __init__(self, delta: int = 1):
        if delta == 0:
            raise ValueError('delta must be non-zero')
        self.delta = delta
        self.name = f'numeric_corruption_{delta:+d}'

    def apply(self, text: str) -> str | None:
        parse = parse_final_answer(text)
        if not parse.ok:
            return None
        old, new = str(parse.value), str(parse.value + self.delta)
        # Replace every standalone occurrence so the reasoning stays consistent.
        pattern = r'(?<![\d,.])' + re.escape(old) + r'(?!\d|,\d|\.\d)'
        return re.sub(pattern, new, text)


DEFAULT_CORRUPTIONS = (NumericCorruption(1),)
