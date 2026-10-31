"""Group probe records and report validity plus mean metrics. Rejections are never hidden."""
from collections import Counter
from prehack.auditing.metrics import mean_or_none
from prehack.counterfactuals.validity import INELIGIBLE_REASONS


def summarize(records: list[dict], keys=('judge', 'transformation')) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for r in records:
        groups.setdefault(tuple(r[k] for k in keys), []).append(r)
    rows = []
    for key in sorted(groups, key=lambda k: tuple(str(x) for x in k)):
        rs = groups[key]
        valid = sum(r['valid'] for r in rs)
        rows.append({
            **dict(zip(keys, key)),
            'probes': len(rs), 'valid': valid, 'rejected': len(rs) - valid,
            'rejection_rate': (len(rs) - valid) / len(rs),
            'mean_style_sensitivity': mean_or_none(r['style_sensitivity'] for r in rs),
            'mean_style_uplift': mean_or_none(r['style_uplift'] for r in rs),
            'mean_semantic_separation': mean_or_none(r['semantic_separation'] for r in rs),
        })
    return rows


def rejection_counts(records: list[dict]) -> list[dict]:
    counts = Counter((r['transformation'], r['reason']) for r in records if not r['valid'])
    return [{'transformation': t, 'reason': reason, 'count': n,
             'expected': reason in INELIGIBLE_REASONS}
            for (t, reason), n in sorted(counts.items())]
