import libcst as cst
import libcst.matchers as m


class IsMethodProvider(cst.BatchableMetadataProvider[bool]):
    """
    Metadata provider that identifies whether a function is a method.
    """
    def visit_ClassDef(self, node: cst.ClassDef):
        for statement in node.body.body:
            if m.matches(statement, m.FunctionDef()):
                self.set_metadata(statement, True)

    def visit_FunctionDef(self, node: cst.FunctionDef):
        if not self.get_metadata(type(self), node, False):
            self.set_metadata(node, False)


def _is_multiline_comment(node: cst.SimpleStatementLine):
    return len(node.body) == 1 and m.matches(node.body[0], m.Expr(value=m.SimpleString()))


class CodeCleaner(cst.CSTTransformer):
    """
    Transformer for removing type annotations, decorators, and comments from cst.
    """

    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider, cst.metadata.WhitespaceInclusivePositionProvider)

    def __init__(self):
        super().__init__()
        self.removed_lines = []
        self.start = 0

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        pos = self.get_metadata(cst.metadata.PositionProvider, node)
        self.start = pos.start.line

        for decorator in node.decorators:
            decorator_pos = self.get_metadata(cst.metadata.PositionProvider, decorator)
            self.removed_lines.extend(range(decorator_pos.start.line, decorator_pos.end.line + 1))

        annotation = node.returns
        if annotation:
            annotation_pos = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, annotation)
            self.removed_lines.extend(range(annotation_pos.start.line+1, annotation_pos.end.line + 1))
        return updated_node.with_changes(returns=None, decorators=())

    def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign):
        if updated_node.value:
            value = updated_node.value
            ws_before = updated_node.equal.whitespace_before
            ws_after = updated_node.equal.whitespace_after
            annotation_pos = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, original_node.annotation)
            self.removed_lines.extend(range(annotation_pos.start.line + 1, annotation_pos.end.line + 1))
            return cst.Assign([cst.AssignTarget(updated_node.target, ws_before, ws_after)], value)
        else:
            pos = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, original_node)
            self.removed_lines.extend(range(pos.start.line, pos.end.line+1))
            return cst.RemoveFromParent()

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param):
        annotation = original_node.annotation
        if annotation:
            annotation_pos = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, annotation)
            self.removed_lines.extend(range(annotation_pos.start.line + 1, annotation_pos.end.line + 1))
        return updated_node.with_changes(annotation=None)

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment):
        # INFO: removing the comment leaves the empty line intact
        return cst.RemoveFromParent()

    def leave_EmptyLine(self, original_node: cst.EmptyLine, updated_node: cst.EmptyLine):
        pos = self.get_metadata(cst.metadata.PositionProvider, original_node)
        self.removed_lines.append(pos.start.line)
        return cst.RemoveFromParent()

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine):
        if _is_multiline_comment(original_node):
            pos = self.get_metadata(cst.metadata.PositionProvider, original_node)
            self.removed_lines.extend(range(pos.start.line, pos.end.line+1))
            return cst.RemoveFromParent()
        return updated_node


class Extractor(cst.CSTVisitor):
    """
    Class for extracting functions from a module. Extracted functions are stored in self.extracted_functions
    """
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, lines, max_level):
        super().__init__()
        self.lines = lines
        self.extracted_function = None
        self.level = 0
        self.inside_function = 0
        self.fun_start = 0
        self.max_level = max_level

    def visit_FunctionDef(self, node: cst.FunctionDef):
        self.inside_function += 1
        pos = self.get_metadata(cst.metadata.PositionProvider, node)
        is_within = all(pos.start.line <= line.start and line.end <= pos.end.line for line in self.lines)
        # all changes within function and function is at most `max_level` deeply nested
        if is_within and self.max_level > self.level:
            self.extracted_function = node
            self.level = self.inside_function
            self.fun_start = pos.start.line

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        self.inside_function -= 1


def code_to_node(code):
    try:
        return cst.MetadataWrapper(cst.parse_module(code))
    except cst.ParserSyntaxError:
        pass


def node_to_code(node):
    return cst.Module([node]).code


if __name__ == '__main__':
    repo = Repo(r'..\repos\black')

    old_commit = 'c012c70176e1958d755768893c08f4b0892fb51d'
    new_commit = '3ddf73337d606442069e5608e62a8367fbacdb40'

    file_name = 'black.py'

    old_line = 165
    new_line = 165

    old_code = repo.git.show(f'{old_commit}:{file_name}')
    new_code = repo.git.show(f'{new_commit}:{file_name}')

    old_extractor = Extractor([old_line])
    new_extractor = Extractor([new_line])

    old_cst = cst.MetadataWrapper(cst.parse_module(old_code))
    new_cst = cst.MetadataWrapper(cst.parse_module(new_code))

    is_method_old = old_cst.resolve(IsMethodProvider)
    is_method_new = new_cst.resolve(IsMethodProvider)

    old_cst.visit(old_extractor)
    new_cst.visit(new_extractor)

    cleaner = CodeCleaner()

    old_function_node = old_extractor.extracted_functions[0][1]
    new_function_node = new_extractor.extracted_functions[0][1]
    old_function: cst.FunctionDef = old_function_node.visit(cleaner)
    old_args = []
    if is_method_old[old_function_node]:
        for param in old_function.params.params[1:]:
            old_args.append(cst.Arg(cst.Name(param.name.value)))
        function_name = old_function.name.value
        old_function: cst.ClassDef = cst.ClassDef(name=cst.Name(value='Old'), body=cst.IndentedBlock([old_function]))
        old_function_call = cst.Call(cst.Attribute(cst.Call(cst.Name(value='Old')), cst.Name(function_name)), old_args)
    else:
        for param in old_function.params.params:
            old_args.append(cst.Arg(cst.Name(param.name.value)))
        old_function = old_function.with_changes(name=cst.Name(old_function.name.value + '_old'))
        old_function_call = cst.Call(cst.Name(old_function.name.value), old_args)

    new_function: cst.FunctionDef = new_function_node.visit(cleaner)
    new_args = []
    if is_method_new[new_function_node]:
        for param in new_function.params.params[1:]:
            new_args.append(cst.Arg(cst.Name(param.name.value)))
        function_name = new_function.name.value
        new_function: cst.ClassDef = cst.ClassDef(name=cst.Name(value='New'), body=cst.IndentedBlock([new_function]))
        new_function_call = cst.Call(cst.Attribute(cst.Call(cst.Name(value='New')), cst.Name(function_name)), old_args)
    else:
        for param in new_function.params.params:
            new_args.append(cst.Arg(cst.Name(param.name.value)))
        new_function = new_function.with_changes(name=cst.Name(new_function.name.value + '_new'))
        new_function_call = cst.Call(cst.Name(old_function.name.value), old_args)

    old_assignment = cst.Assign([cst.AssignTarget(cst.Name('old_return_value'))], old_function_call)
    new_assignment = cst.Assign([cst.AssignTarget(cst.Name('new_return_value'))], new_function_call)
    with open('old_function.py', 'w', encoding="utf-8") as f:
        f.write(cst.Module([old_function], header=[cst.EmptyLine(comment=cst.Comment('#test comment'))]).code)
    with open('new_function.py', 'w', encoding="utf-8") as f:
        f.write(cst.Module([new_function], header=[cst.EmptyLine(comment=cst.Comment('#test comment'))]).code)
    with open('compare.py', 'w', encoding="utf-8") as f:
        print_call = cst.SimpleStatementLine([cst.Expr(cst.Call(cst.Name('print'), [cst.Arg(cst.Comparison(cst.Name('old_return_value'), [cst.ComparisonTarget(cst.Equal(), cst.Name('new_return_value'))]))]))])
        f.write(cst.Module([old_function, cst.SimpleStatementLine([old_assignment]), new_function, cst.SimpleStatementLine([new_assignment]), print_call]).code)
