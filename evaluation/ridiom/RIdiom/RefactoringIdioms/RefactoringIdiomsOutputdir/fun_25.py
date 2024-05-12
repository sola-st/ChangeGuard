def test_idempotent_any_syntatically_valid_python(
    src_contents, mode
):
    compile(src_contents, "<string>", "exec")  
    try:
        dst_contents = black.format_str(src_contents, mode=mode)
    except black.InvalidInput:
        return
    except TokenError as e:
        if (  
            e.args[0] == "EOF in multi-line statement"
            and re.search(r"\\($|\r?\n)", src_contents) is not None
        ):
            return
        raise
    black.assert_equivalent(src_contents, dst_contents)
    black.assert_stable(src_contents, dst_contents, mode=mode)
