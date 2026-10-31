"""Validity checks. Every probe gets a verdict and a reason code; rejections are reported.

Reason codes:
  ok
  original_none / original_ambiguous  original answer not parseable (ineligible)
  original_incorrect                  corruption needs a correct original (ineligible)
  not_applicable                      transformation returned nothing
  no_change                           variant identical to original
  variant_none / variant_ambiguous    variant answer not parseable          (BUG signal)
  answer_changed                      style edit altered the answer          (BUG signal)
  answer_unchanged                    corruption left the answer unchanged   (BUG signal)
  variant_still_correct               corruption did not make it wrong       (BUG signal)
  style_changed                       corruption altered presentation        (BUG signal)
"""
from dataclasses import dataclass
from prehack.core import Problem
from prehack.tasks.arithmetic import FEATURES, has_feature
from prehack.verifiers.arithmetic import verify_text

OK = 'ok'
INELIGIBLE_REASONS = frozenset({'original_none', 'original_ambiguous', 'original_incorrect'})


@dataclass(frozen=True)
class Validity:
    valid: bool
    reason: str


def _features(text: str) -> tuple[bool, ...]:
    return tuple(has_feature(text, f) for f in FEATURES)


def check_style(problem: Problem, original: str, variant: str | None) -> Validity:
    o = verify_text(problem, original)
    if not o.parse.ok:
        return Validity(False, f'original_{o.parse.status}')
    if variant is None:
        return Validity(False, 'not_applicable')
    if variant == original:
        return Validity(False, 'no_change')
    v = verify_text(problem, variant)
    if not v.parse.ok:
        return Validity(False, f'variant_{v.parse.status}')
    if v.parse.value != o.parse.value:
        return Validity(False, 'answer_changed')
    return Validity(True, OK)


def check_corruption(problem: Problem, original: str, variant: str | None) -> Validity:
    o = verify_text(problem, original)
    if not o.parse.ok:
        return Validity(False, f'original_{o.parse.status}')
    if o.correct is not True:
        return Validity(False, 'original_incorrect')
    if variant is None:
        return Validity(False, 'not_applicable')
    v = verify_text(problem, variant)
    if not v.parse.ok:
        return Validity(False, f'variant_{v.parse.status}')
    if v.parse.value == o.parse.value:
        return Validity(False, 'answer_unchanged')
    if v.correct:
        return Validity(False, 'variant_still_correct')
    if _features(variant) != _features(original):
        return Validity(False, 'style_changed')
    return Validity(True, OK)
