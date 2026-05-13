import fnmatch
import re
from typing import NamedTuple


class CompiledPatterns(NamedTuple):
    exact: frozenset[str]
    regex: re.Pattern | None
    is_empty: bool


def compile_patterns(raw: list[str]) -> CompiledPatterns:
    if not raw:
        return CompiledPatterns(frozenset(), None, True)
    exact = set()
    regex_parts = []
    for pat in dict.fromkeys(raw):
        if any(c in pat for c in ("*", "?", "[", "]")):
            regex_parts.append(fnmatch.translate(pat))
        else:
            exact.add(pat)
    compiled_re = re.compile("|".join(regex_parts)) if regex_parts else None
    return CompiledPatterns(frozenset(exact), compiled_re, False)
