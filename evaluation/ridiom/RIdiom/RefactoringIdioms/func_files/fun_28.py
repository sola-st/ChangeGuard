def transform_line(
    line, mode, features = ()
):
    if line.is_comment:
        yield line
        return
    line_str = line_to_string(line)
    def init_st(ST):
        return ST(mode.line_length, mode.string_normalization)
    string_merge = init_st(StringMerger)
    string_paren_strip = init_st(StringParenStripper)
    string_split = init_st(StringSplitter)
    string_paren_wrap = init_st(StringParenWrapper)
    if (
        not line.contains_uncollapsable_type_comments()
        and not line.should_split
        and not line.magic_trailing_comma
        and (
            is_line_short_enough(line, line_length=mode.line_length, line_str=line_str)
            or line.contains_unsplittable_type_ignore()
        )
        and not (line.inside_brackets and line.contains_standalone_comments())
    ):
        if mode.experimental_string_processing:
            transformers = [string_merge, string_paren_strip]
        else:
            transformers = []
    elif line.is_def:
        transformers = [left_hand_split]
    else:
        def rhs(line, features):
            for omit in generate_trailers_to_omit(line, mode.line_length):
                lines = list(
                    right_hand_split(line, mode.line_length, features, omit=omit)
                )
                if is_line_short_enough(lines[0], line_length=mode.line_length):
                    yield from lines
                    return
            yield from right_hand_split(
                line, line_length=mode.line_length, features=features
            )
        if mode.experimental_string_processing:
            if line.inside_brackets:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    delimiter_split,
                    standalone_comment_split,
                    string_paren_wrap,
                    rhs,
                ]
            else:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    string_paren_wrap,
                    rhs,
                ]
        else:
            if line.inside_brackets:
                transformers = [delimiter_split, standalone_comment_split, rhs]
            else:
                transformers = [rhs]
    for transform in transformers:
        try:
            result = run_transformer(line, transform, mode, features, line_str=line_str)
        except CannotTransform:
            continue
        else:
            yield from result
            break
    else:
        yield line
