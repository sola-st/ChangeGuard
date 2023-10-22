from typing import Optional

from git import Repo
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
    Transformer for removing type annotations and comments from cst.
    """
    def __init__(self):
        super().__init__()

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        return updated_node.with_changes(returns=None, leading_lines=[])

    def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign):
        if updated_node.value:
            value = updated_node.value
            ws_before = updated_node.equal.whitespace_before
            ws_after = updated_node.equal.whitespace_after
        else:
            return cst.RemoveFromParent()
        return cst.Assign([cst.AssignTarget(updated_node.target, ws_before, ws_after)], value)

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param):
        return updated_node.with_changes(annotation=None)

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment):
        return cst.RemoveFromParent()

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine):
        if _is_multiline_comment(original_node):
            return cst.RemoveFromParent()
        return updated_node


class Extractor(cst.CSTVisitor):
    """
    Class for extracting functions from a module. Extracted functions are stored in self.extracted_functions
    """
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, lines):
        super().__init__()
        self.lines = lines
        self.extracted_functions = set()
        self.inside_function = 0
        self.changes_to_comments = 0

    def visit_FunctionDef(self, node: cst.FunctionDef):
        if self.inside_function > 0:  # ignore nested functions
            return
        position = self.get_metadata(cst.metadata.PositionProvider, node)

        for line_number in self.lines:
            if position.start.line <= line_number[0] and line_number[1] <= position.end.line:  # change happens within function
                self.extracted_functions.add(node)
        self.inside_function += 1

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        self.inside_function -= 1

    def visit_Comment(self, node: cst.Comment):
        position = self.get_metadata(cst.metadata.PositionProvider, node)

        for line_number in self.lines:
            if position.start.line <= line_number[0] and line_number[1] <= position.end.line:  # change happens within comment
                self.changes_to_comments += 1

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine):
        if not _is_multiline_comment(node):
            return
        position = self.get_metadata(cst.metadata.PositionProvider, node)
        for line_number in self.lines:
            if position.start.line <= line_number[0] and line_number[1] <= position.end.line:  # change happens within comment
                self.changes_to_comments += 1


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
