"""Run transformations on one response, validate each variant, score valid ones."""
from prehack.auditing.metrics import probe_metrics
from prehack.counterfactuals.base import STYLE
from prehack.counterfactuals.corruption import DEFAULT_CORRUPTIONS
from prehack.counterfactuals.style import STYLE_TRANSFORMS
from prehack.counterfactuals.validity import check_corruption, check_style
from prehack.verifiers.arithmetic import verify_text

DEFAULT_TRANSFORMS = tuple(STYLE_TRANSFORMS) + tuple(DEFAULT_CORRUPTIONS)


def run_probes(problem, original: str, judge, transformations=None) -> list[dict]:
    transformations = DEFAULT_TRANSFORMS if transformations is None else transformations
    original_score = judge.score(problem, original)
    original_correct = verify_text(problem, original).correct
    records = []
    for t in transformations:
        variant = t.apply(original)
        check = check_style if t.kind == STYLE else check_corruption
        validity = check(problem, original, variant)
        variant_score = judge.score(problem, variant) if validity.valid else None
        records.append({
            'problem_id': problem.id, 'judge': judge.name,
            'transformation': t.name, 'kind': t.kind,
            'original': original, 'variant': variant,
            'original_correct': original_correct, 'original_score': original_score,
            'variant_score': variant_score,
            'valid': validity.valid, 'reason': validity.reason,
            **probe_metrics(t.kind, original_score, variant_score),
        })
    return records
