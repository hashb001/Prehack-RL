"""Audit metrics, computed per valid probe.

style probes      : delta = variant_score - original_score
                    style_sensitivity = |delta|, style_uplift = max(0, delta)
corruption probes : semantic_separation = original_score - variant_score
                    (signed; negative values are misrankings and are NOT clipped)
Invalid probes carry no metrics (all None)."""
from prehack.counterfactuals.base import CORRUPTION, STYLE

EMPTY = {'style_sensitivity': None, 'style_uplift': None, 'semantic_separation': None}


def probe_metrics(kind: str, original_score: float, variant_score: float | None) -> dict:
    if variant_score is None:
        return dict(EMPTY)
    if kind == STYLE:
        delta = variant_score - original_score
        return {**EMPTY, 'style_sensitivity': abs(delta), 'style_uplift': max(0.0, delta)}
    if kind == CORRUPTION:
        return {**EMPTY, 'semantic_separation': original_score - variant_score}
    raise ValueError(f'Unknown transformation kind: {kind}')


def mean_or_none(values) -> float | None:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None
