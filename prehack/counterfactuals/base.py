"""Transformation interface. A transformation maps text -> text, or None if inapplicable."""
from typing import Protocol

STYLE = 'style'            # correctness-preserving
CORRUPTION = 'corruption'  # correctness-changing


class Transformation(Protocol):
    name: str
    kind: str
    def apply(self, text: str) -> str | None: ...
