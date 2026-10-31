"""Independent correctness check on parsed answers (never uses a judge)."""
from dataclasses import dataclass
from prehack.core import Problem
from prehack.verifiers.parsing import ParseResult, parse_final_answer


@dataclass(frozen=True)
class Verdict:
    parse: ParseResult
    correct: bool | None      # None when the answer could not be parsed unambiguously


def verify_text(problem: Problem, text: str) -> Verdict:
    parse = parse_final_answer(text)
    return Verdict(parse, (parse.value == problem.truth) if parse.ok else None)
