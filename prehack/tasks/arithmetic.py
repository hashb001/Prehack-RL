"""Arithmetic task that produces free-text responses with controllable style.

Style features (all independent of correctness):
  confidence : response starts with CONF_PHRASE
  verbosity  : response contains PREAMBLE
  bold       : the final answer number is wrapped in **...**
"""
import random
from prehack.core import Problem

CONF_PHRASE = 'I am absolutely certain. '
PREAMBLE = 'Let me work through this carefully. '
FEATURES = ('confidence', 'verbosity', 'bold')

# {n} is the (possibly bolded) final answer.
TEMPLATES = (
    'Final answer: {n}',
    'The answer is {n}.',
    'Answer: {n}',
    r'Therefore, the result is \boxed{{{n}}}.',
)

# Deliberately messy responses: used to exercise parser failures and rejection reporting.
MESSY_TEMPLATES = (
    'I think it is around {n}, but I could be wrong.',              # no answer marker
    'Final answer: {n}. Actually, wait. Final answer: {m}.',        # conflicting answers
    'I cannot determine the sum.',                                  # no number at all
)


def has_feature(text: str, feature: str) -> bool:
    if feature == 'confidence':
        return CONF_PHRASE in text
    if feature == 'verbosity':
        return PREAMBLE in text
    if feature == 'bold':
        return '**' in text
    raise ValueError(f'Unknown feature: {feature}')


def make_problem(rng: random.Random, problem_id: str) -> Problem:
    return Problem(problem_id, rng.randint(5, 50), rng.randint(5, 50))


def render(problem: Problem, answer: int, *, confident=False, verbose=False,
           bold=False, template=0) -> str:
    n = f'**{answer}**' if bold else str(answer)
    final = TEMPLATES[template % len(TEMPLATES)].format(n=n)
    reasoning = f'Adding {problem.a} and {problem.b} gives {answer}. '
    return ((CONF_PHRASE if confident else '') + (PREAMBLE if verbose else '')
            + reasoning + final)


def render_messy(answer: int, kind: int, *, confident=False, verbose=False) -> str:
    body = MESSY_TEMPLATES[kind % len(MESSY_TEMPLATES)].format(n=answer, m=answer + 1)
    return (CONF_PHRASE if confident else '') + (PREAMBLE if verbose else '') + body


def sample_response(problem: Problem, rng: random.Random, messy_rate: float = 0.0) -> str:
    """Draw one response. Random draws happen in a fixed order for reproducibility."""
    correct = rng.random() < 0.5
    wrong_offset = rng.choice([-2, -1, 1, 2])
    confident, verbose, bold = (rng.random() < 0.5 for _ in range(3))
    template = rng.randrange(len(TEMPLATES))
    messy = rng.random() < messy_rate
    messy_kind = rng.randrange(len(MESSY_TEMPLATES))
    answer = problem.truth if correct else problem.truth + wrong_offset
    if messy:
        return render_messy(answer, messy_kind, confident=confident, verbose=verbose)
    return render(problem, answer, confident=confident, verbose=verbose,
                  bold=bold, template=template)
