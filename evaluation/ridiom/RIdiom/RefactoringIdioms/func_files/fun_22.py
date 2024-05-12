def visit_Assign(self, node):
    if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
        args = _get_str_args(node.value.args)
        if node.value.func.attr == "getoutput":
            src = f"!{args[0]}"
        elif node.value.func.attr == "run_line_magic":
            src = f"%{args[0]}"
            if args[1]:
                src += f" {args[1]}"
        else:
            raise AssertionError(
                f"Unexpected IPython magic {node.value.func.attr!r} found. "
                "Please report a bug on https://github.com/psf/black/issues."
            ) from None
        self.magics[node.value.lineno].append(
            OffsetAndMagic(node.value.col_offset, src)
        )
    self.generic_visit(node)
