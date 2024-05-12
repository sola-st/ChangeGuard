def can_omit_invisible_parens(
    line,
    line_length,
    omit_on_explode = (),
):
    bt = line.bracket_tracker
    if not bt.delimiters:
        return True
    max_priority = bt.max_delimiter_priority()
    if bt.delimiter_count_with_priority(max_priority) > 1:
        return False
    if max_priority == DOT_PRIORITY:
        return True
    assert len(line.leaves) >= 2, "Stranded delimiter"
    first , second  = line.leaves[0], line.leaves[1]
    if first.type in OPENING_BRACKETS and second.type not in CLOSING_BRACKETS:
        if _can_omit_opening_paren(line, first=first, line_length=line_length):
            return True
    penultimate , last  = line.leaves[-2], line.leaves[-1]
    if line.magic_trailing_comma:
        try:
            penultimate, last = last_two_except(line.leaves, omit=omit_on_explode)
        except LookupError:
            return False
    if (
        last.type == token.RPAR
        or last.type == token.RBRACE
        or (
            last.type == token.RSQB
            and last.parent
            and last.parent.type != syms.trailer
        )
    ):
        if penultimate.type in OPENING_BRACKETS:
            return False
        if is_multiline_string(first):
            return True
        if line.magic_trailing_comma and penultimate.type == token.COMMA:
            return True
        if _can_omit_closing_paren(line, last=last, line_length=line_length):
            return True
    return False
