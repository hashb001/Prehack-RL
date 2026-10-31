"""Text-based synthetic judges: oracle correctness + one injected style bonus.
Infrastructure fixtures with KNOWN bias, so exp_03 can check the metrics recover it."""
from dataclasses import dataclass
from prehack.core import Problem
from prehack.tasks.arithmetic import FEATURES, has_feature
from prehack.verifiers.arithmetic import verify_text


@dataclass(frozen=True)
class SyntheticTextJudge:
    name: str
    bias_feature: str | None = None   # one of FEATURES, or None for the control
    bonus: float = 0.0

    def __post_init__(self):
        if self.bias_feature is not None and self.bias_feature not in FEATURES:
            raise ValueError(f'Unknown bias feature: {self.bias_feature}')

    def score(self, problem: Problem, text: str) -> float:
        # Unparseable / ambiguous answers are scored like incorrect ones.
        base = 0.70 if verify_text(problem, text).correct is True else 0.10
        if self.bias_feature and has_feature(text, self.bias_feature):
            base += self.bonus
        return min(1.0, base)


DEFAULT_JUDGES = (
    SyntheticTextJudge('control'),
    SyntheticTextJudge('confidence_biased', 'confidence', 0.65),
    SyntheticTextJudge('verbosity_biased', 'verbosity', 0.30),
    SyntheticTextJudge('format_biased', 'bold', 0.20),
)
