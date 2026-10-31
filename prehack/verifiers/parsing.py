"""Extract the final answer from free text, with explicit failure modes.

Rules (documented in docs/methodology.md):
  * Candidates are numbers after \\boxed{...} or after a marker word
    ("final answer", "answer", "result"). Numbers elsewhere are ignored.
  * No candidate  -> status 'none'      (we never guess from stray numbers)
  * Conflicting candidate values -> status 'ambiguous'
  * One distinct value -> status 'ok'; span points at the LAST candidate.
"""
import re
from dataclasses import dataclass

_NUM = r'-?\d{1,3}(?:,\d{3})+|-?\d+'
_TAIL = r'(?!\d|\.\d)'          # reject partial matches such as 47 in 47.5
_BOXED = re.compile(r'\\boxed\{[\s*_]*(' + _NUM + r')' + _TAIL)
_MARKER = re.compile(r'\b(?:final\s+answer|answer|result)\b\s*(?:is|:|=)?\s*[*_`$(\s]*('
                     + _NUM + r')' + _TAIL, re.IGNORECASE)


@dataclass(frozen=True)
class ParseResult:
    status: str                      # 'ok' | 'ambiguous' | 'none'
    value: int | None = None
    span: tuple[int, int] | None = None   # character span of the number in the text
    method: str | None = None             # 'boxed' | 'marker'

    @property
    def ok(self) -> bool:
        return self.status == 'ok'


def _to_int(token: str) -> int:
    return int(token.replace(',', ''))


def parse_final_answer(text: str) -> ParseResult:
    boxed = list(_BOXED.finditer(text))
    marked = list(_MARKER.finditer(text))
    if not boxed and not marked:
        return ParseResult('none')
    values = {_to_int(m.group(1)) for m in boxed + marked}
    if len(values) > 1:
        return ParseResult('ambiguous')
    method, match = ('boxed', boxed[-1]) if boxed else ('marker', marked[-1])
    return ParseResult('ok', _to_int(match.group(1)), match.span(1), method)
