def generate_trailers_to_omit(line, line_length):
    omit = set()
    if not line.magic_trailing_comma:
        yield omit
    length = 4 * line.depth
    opening_bracket = None
    closing_bracket = None
    inner_brackets = set()
    for index, leaf, leaf_length in enumerate_with_length(line, reversed=True):
        length += leaf_length
        if length > line_length:
            break
        has_inline_comment = leaf_length > len(leaf.value) + len(leaf.prefix)
        if leaf.type == STANDALONE_COMMENT or has_inline_comment:
            break
        if opening_bracket:
            if leaf is opening_bracket:
                opening_bracket = None
            elif leaf.type in CLOSING_BRACKETS:
                prev = line.leaves[index - 1] if index > 0 else None
                if (
                    line.magic_trailing_comma
                    and prev
                    and prev.type == token.COMMA
                    and not is_one_tuple_between(
                        leaf.opening_bracket, leaf, line.leaves
                    )
                ):
                    break
                inner_brackets.add(id(leaf))
        elif leaf.type in CLOSING_BRACKETS:
            prev = line.leaves[index - 1] if index > 0 else None
            if prev and prev.type in OPENING_BRACKETS:
                inner_brackets.add(id(leaf))
                continue
            if closing_bracket:
                omit.add(id(closing_bracket))
                omit.update(inner_brackets)
                inner_brackets.clear()
                yield omit
            if (
                line.magic_trailing_comma
                and prev
                and prev.type == token.COMMA
                and not is_one_tuple_between(leaf.opening_bracket, leaf, line.leaves)
            ):
                break
            if leaf.value:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf
