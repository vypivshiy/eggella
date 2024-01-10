import re
from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completion
from prompt_toolkit.completion import FuzzyCompleter as OldFuzzyCompleter
from prompt_toolkit.completion.fuzzy_completer import _FuzzyMatch
from prompt_toolkit.document import Document


class FuzzyCompleter(OldFuzzyCompleter):
    """Patched original FuzzyCompleter for avoid
    AttributeError: 'NoneType' object has no attribute 'text'
    in prompt for next cases:

    1. tap whitespace char only

    2. tap whitespace char + any text
    """

    def _get_fuzzy_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        word_before_cursor = document.get_word_before_cursor(pattern=re.compile(self._get_pattern()))

        # Get completions
        document2 = Document(
            text=document.text[: document.cursor_position - len(word_before_cursor)],
            cursor_position=document.cursor_position - len(word_before_cursor),
        )

        inner_completions = list(self.completer.get_completions(document2, complete_event))

        fuzzy_matches: list[_FuzzyMatch] = []  # type: ignore

        if word_before_cursor == "":
            # If word before the cursor is an empty string, consider all
            # completions, without filtering everything with an empty regex
            # pattern.
            fuzzy_matches = [_FuzzyMatch(0, 0, compl) for compl in inner_completions]
        else:
            pat = ".*?".join(map(re.escape, word_before_cursor))
            pat = f"(?=({pat}))"  # lookahead regex to manage overlapping matches
            regex = re.compile(pat, re.IGNORECASE)
            for compl in inner_completions:
                # first path
                if compl is None:
                    continue
                matches = list(regex.finditer(compl.text))
                if matches:
                    # Prefer the match, closest to the left, then shortest.
                    best = min(matches, key=lambda m: (m.start(), len(m.group(1))))
                    fuzzy_matches.append(_FuzzyMatch(len(best.group(1)), best.start(), compl))

            def sort_key(fuzzy_match: _FuzzyMatch) -> tuple[int, int]:  # type: ignore
                "Sort by start position, then by the length of the match."
                return fuzzy_match.start_pos, fuzzy_match.match_length

            fuzzy_matches = sorted(fuzzy_matches, key=sort_key)

        for match in fuzzy_matches:
            if match.completion is None:
                # second path
                yield Completion("")
            else:
                # Include these completions, but set the correct `display`
                # attribute and `start_position`.
                yield Completion(
                    text=match.completion.text,
                    start_position=match.completion.start_position - len(word_before_cursor),
                    # We access to private `_display_meta` attribute, because that one is lazy.
                    display_meta=match.completion._display_meta,
                    display=self._get_display(match, word_before_cursor),
                    style=match.completion.style,
                )
