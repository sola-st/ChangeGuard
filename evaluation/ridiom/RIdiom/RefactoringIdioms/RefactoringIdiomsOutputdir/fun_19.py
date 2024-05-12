def assert_equivalent(src, dst, *, pass_num = 1):
    try:
        src_ast = parse_ast(src)
    except Exception as exc:
        raise AssertionError(
            f"cannot use --safe with this file; failed to parse source file AST: "
            f"{exc}\n"
            f"This could be caused by running Black with an older Python version "
            f"that does not support new syntax used in your source file."
        ) from exc
    try:
        dst_ast = parse_ast(dst)
    except Exception as exc:
        log = dump_to_file("".join(traceback.format_tb(exc.__traceback__)), dst)
        raise AssertionError(
            f"INTERNAL ERROR: Black produced invalid code on pass {pass_num}: {exc}. "
            "Please report a bug on https://github.com/psf/black/issues.  "
            f"This invalid output might be helpful: {log}"
        ) from None
    src_ast_str , dst_ast_str  = '\n'.join(stringify_ast(src_ast)), '\n'.join(stringify_ast(dst_ast))
    if src_ast_str != dst_ast_str:
        log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
        raise AssertionError(
            "INTERNAL ERROR: Black produced code that is not equivalent to the"
            f" source on pass {pass_num}.  Please report a bug on "
            f"https://github.com/psf/black/issues.  This diff might be helpful: {log}"
        ) from None
