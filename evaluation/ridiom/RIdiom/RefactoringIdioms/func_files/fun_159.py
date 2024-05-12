def _iter_member_names(klass):
    for node in ast.iter_child_nodes(klass):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            yield node.target.id
        elif isinstance(node, ast.FunctionDef) and _is_property(node):
            yield node.name
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(target := node.targets[0], ast.Name):
                yield target.id
