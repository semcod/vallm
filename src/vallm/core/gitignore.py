def _pattern_to_regex(self, pattern: str) -> str:
    """Convert a gitignore pattern to a regex pattern."""
    def _classify_char(i: int) -> tuple[str, int]:
        c = pattern[i]

        if c == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                return ".*", 2
            return "[^/]*", 1

        if c == "?":
            return "[^/]", 1

        if c == "[":
            end = pattern.find("]", i + 1)
            if end == -1:
                return re.escape(c), 1

            char_class = pattern[i + 1:end]
            if char_class.startswith("!") or char_class.startswith("^"):
                char_class = "^" + char_class[1:]
            return f"[{char_class}]", end - i + 1

        if c == "/":
            return "/", 1

        return re.escape(c), 1

    result = []
    i = 0

    while i < len(pattern):
        token, step = _classify_char(i)
        result.append(token)
        i += step

    return "^" + "".join(result) + "$"