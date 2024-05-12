def format_str(src_contents, *, mode):
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents , future_imports  = [], get_future_imports(src_node)
    if mode.target_versions:
        versions = mode.target_versions
    else:
        versions = detect_target_versions(src_node)
    if TargetVersion.PY27 in mode.target_versions or versions == {TargetVersion.PY27}:
        msg = (
            "DEPRECATION: Python 2 support will be removed in the first stable release "
            "expected in January 2022."
        )
        err(msg, fg="yellow", bold=True)
    normalize_fmt_off(src_node)
    lines , elt , empty_line , after , split_line_features  = LineGenerator(mode=mode, remove_u_prefix='unicode_literals' in future_imports or supports_feature(versions, Feature.UNICODE_LITERALS)), EmptyLineTracker(is_pyi=mode.is_pyi), Line(mode=mode), 0, {feature for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF} if supports_feature(versions, feature)}
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode, features=split_line_features
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)
