def _maybe_empty_lines_for_class_or_def(
    self, current_line, before
):
    if not current_line.is_decorator:
        self.previous_defs.append(current_line.depth)
    if self.previous_line is None:
        return 0, 0
    if self.previous_line.is_decorator:
        if self.is_pyi and current_line.is_stub_class:
            return 0, 1
        return 0, 0
    if self.previous_line.depth < current_line.depth and (
        self.previous_line.is_class or self.previous_line.is_def
    ):
        return 0, 0
    if (
        self.previous_line.is_comment
        and self.previous_line.depth == current_line.depth
        and before == 0
    ):
        return 0, 0
    if self.is_pyi:
        if self.previous_line.depth > current_line.depth:
            newlines = 0 if current_line.depth else 1
        elif current_line.is_class or self.previous_line.is_class:
            if current_line.depth:
                newlines = 0
            elif current_line.is_stub_class and self.previous_line.is_stub_class:
                newlines = 0
            else:
                newlines = 1
        elif (
            current_line.is_def or current_line.is_decorator
        ) and not self.previous_line.is_def:
            if current_line.depth:
                newlines = min(1, before)
            else:
                newlines = 1
        else:
            newlines = 0
    else:
        newlines = 1 if current_line.depth else 2
    return newlines, 0
