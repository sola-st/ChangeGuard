def _maybe_empty_lines(self, current_line):
    max_allowed = 1
    if not current_line.depth:
        max_allowed = 1 if self.mode.is_pyi else 2
    if current_line.leaves:
        first_leaf = current_line.leaves[0]
        before = first_leaf.prefix.count("\n")
        before , first_leaf.prefix  = min(before, max_allowed), ''
    else:
        before = 0
    depth = current_line.depth
    while self.previous_defs and self.previous_defs[-1].depth >= depth:
        if self.mode.is_pyi:
            assert self.previous_line is not None
            if depth and not current_line.is_def and self.previous_line.is_def:
                before = min(1, before)
            elif (
                Preview.blank_line_after_nested_stub_class in self.mode
                and self.previous_defs[-1].is_class
                and not self.previous_defs[-1].is_stub_class
            ):
                before = 1
            elif depth:
                before = 0
            else:
                before = 1
        else:
            if depth:
                before = 1
            elif (
                not depth
                and self.previous_defs[-1].depth
                and current_line.leaves[-1].type == token.COLON
                and (
                    current_line.leaves[0].value
                    not in ("with", "try", "for", "while", "if", "match")
                )
            ):
                before = 1
            else:
                before = 2
        self.previous_defs.pop()
    if current_line.is_decorator or current_line.is_def or current_line.is_class:
        return self._maybe_empty_lines_for_class_or_def(current_line, before)
    if (
        self.previous_line
        and self.previous_line.is_import
        and not current_line.is_import
        and not current_line.is_fmt_pass_converted(first_leaf_matches=is_import)
        and depth == self.previous_line.depth
    ):
        return (before or 1), 0
    if (
        self.previous_line
        and self.previous_line.is_class
        and current_line.is_triple_quoted_string
    ):
        return before, 1
    if self.previous_line and self.previous_line.opens_block:
        return 0, 0
    return before, 0
