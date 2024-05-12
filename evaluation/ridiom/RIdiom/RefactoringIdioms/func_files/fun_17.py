def _format_str_once(src_contents, *, mode):
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents = []
    if mode.target_versions:
        versions = mode.target_versions
    else:
        future_imports = get_future_imports(src_node)
        versions = detect_target_versions(src_node, future_imports=future_imports)
    normalize_fmt_off(src_node, preview=mode.preview)
    lines = LineGenerator(mode=mode)
    elt = EmptyLineTracker(is_pyi=mode.is_pyi)
    empty_line = Line(mode=mode)
    after = 0
    split_line_features = {
        feature
        for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF}
        if supports_feature(versions, feature)
    }
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode, features=split_line_features
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)
