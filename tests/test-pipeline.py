"""Controlled synthetic components. No language model or policy training."""
from dataclasses import dataclass
from typing import Protocol
import random

@dataclass(frozen=True)
class Problem:
    id: str
    a: int
    b: int

    @property
    def truth(self) -> int:
        return self.a + self.b

@dataclass(frozen=True)
class Response:
    answer: int
    confident: bool = False

    @property
    def text(self) -> str:
        prefix = 'I am absolutely certain. ' if self.confident else ''
        return f'{prefix}Final answer: {self.answer}'

def verify(problem: Problem, response: Response) -> bool:
    return response.answer == problem.truth

class Judge(Protocol):
    name: str
    def score(self, problem: Problem, response: Response) -> float: ...

@dataclass(frozen=True)
class SyntheticJudge:
    """Oracle plus an injected style bonus; exclusively an infrastructure fixture."""
    name: str
    confidence_bonus: float = 0.0

    def score(self, problem: Problem, response: Response) -> float:
        base = 0.70 if verify(problem, response) else 0.10
        return min(1.0, base + self.confidence_bonus * response.confident)

def sample_candidates(problem: Problem, count: int, rng: random.Random) -> list[Response]:
    wrong = problem.truth + rng.choice([-2, -1, 1, 2])
    return rng.choices([Response(problem.truth), Response(wrong, True), Response(wrong)],
                       weights=[0.55, 0.35, 0.10], k=count)

def select_best(problem: Problem, candidates: list[Response], judge: Judge) -> Response:
    if not candidates:
        raise ValueError('At least one candidate is required')
    return max(candidates, key=lambda r: judge.score(problem, r))

def audit(problem: Problem, original: Response, judge: Judge) -> dict:
    """Separate style sensitivity from matched semantic separation.

    Corruption is eligible only for a correct original. Semantic separation is
    signed and may be negative; do not silently clip misrankings.
    """
    style = Response(original.answer, not original.confident)
    base = judge.score(problem, original)
    style_score = judge.score(problem, style)
    correct = verify(problem, original)
    corrupted = Response(original.answer + 1, original.confident) if correct else None
    corrupt_score = judge.score(problem, corrupted) if corrupted else None
    return {
        'problem_id': problem.id, 'judge': judge.name,
        'original': original.text, 'original_correct': correct, 'original_score': base,
        'style_variant': style.text, 'style_valid': verify(problem, style) == correct,
        'style_score': style_score, 'style_sensitivity': abs(style_score - base),
        'style_uplift': max(0.0, style_score - base),
        'semantic_eligible': correct,
        'corrupted_variant': corrupted.text if corrupted else None,
        'corrupted_score': corrupt_score,
        'semantic_separation': base - corrupt_score if correct else None,
    }

def expected_accuracy(n: int, biased: bool) -> float:
    """Exact accuracy under the fixed three-response distribution."""
    return (0.65 ** n - 0.10 ** n) if biased else (1.0 - 0.45 ** n)
