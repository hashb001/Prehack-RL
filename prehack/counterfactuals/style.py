"""Correctness-preserving transformations. Each is a toggle: it adds the feature if
absent and removes it if present. Validity is checked separately (validity.py)."""
from prehack.counterfactuals.base import STYLE
from prehack.tasks.arithmetic import CONF_PHRASE, PREAMBLE
from prehack.verifiers.parsing import parse_final_answer


class ConfidenceToggle:
    name, kind, feature = 'confidence_toggle', STYLE, 'confidence'

    def apply(self, text: str) -> str | None:
        if CONF_PHRASE in text:
            return text.replace(CONF_PHRASE, '', 1)
        return CONF_PHRASE + text


class VerbosityToggle:
    name, kind, feature = 'verbosity_toggle', STYLE, 'verbosity'

    def apply(self, text: str) -> str | None:
        if PREAMBLE in text:
            return text.replace(PREAMBLE, '', 1)
        if text.startswith(CONF_PHRASE):
            return CONF_PHRASE + PREAMBLE + text[len(CONF_PHRASE):]
        return PREAMBLE + text


class BoldAnswer:
    name, kind, feature = 'bold_answer', STYLE, 'bold'

    def apply(self, text: str) -> str | None:
        parse = parse_final_answer(text)
        if not parse.ok:
            return None
        start, end = parse.span
        if text[max(0, start - 2):start] == '**' and text[end:end + 2] == '**':
            return text[:start - 2] + text[start:end] + text[end + 2:]
        return text[:start] + '**' + text[start:end] + '**' + text[end:]


STYLE_TRANSFORMS = (ConfidenceToggle(), VerbosityToggle(), BoldAnswer())
