from typing import Optional

from git import Repo
import libcst as cst
import libcst.matchers as m

repo = Repo(r'C:\Users\Lars\Uni\Master\Masterarbeit\Repos\Python')

old_commit = '0b0214c42f563e7af885058c0e3a32d292f7f1da'
new_commit = '90a8e6e0d210a5c526c8f485fa825e1649d217e2'

file_name = 'sorts/bubble_sort.py'

line_number = 31

old_code = repo.git.show(f'{old_commit}:{file_name}')
new_code = repo.git.show(f'{new_commit}:{file_name}')

class CodeCleaner(cst.CSTTransformer):
    """
    Transformer for removing type annotations and comments from cst.
    """

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
        print(original_node.value)
        return cst.RemoveFromParent()

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine):
        if len(original_node.body) == 1 and m.matches(original_node.body[0], m.Expr(value=m.SimpleString())):
            return cst.RemoveFromParent()
        return updated_node


old_cst = cst.MetadataWrapper(cst.parse_module(old_code))
new_cst = cst.MetadataWrapper(cst.parse_module(new_code))


class Extractor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self):
        super().__init__()
        self.extracted_functions = []

    def visit_FunctionDef(self, node: cst.FunctionDef):
        lines = self.get_metadata(cst.metadata.PositionProvider, node)
        if lines.start.line <= line_number <= lines.end.line:  # change happens within function
            self.extracted_functions.append(node)


old_extractor = Extractor()
new_extractor = Extractor()
old_cst.visit(old_extractor)
new_cst.visit(new_extractor)

cleaner = CodeCleaner()

# TODO find matching pairs

old_function: cst.FunctionDef = old_extractor.extracted_functions[0].visit(cleaner)
new_function: cst.FunctionDef = new_extractor.extracted_functions[0].visit(cleaner)
args = []
for param in old_function.params.params:
    args.append(cst.Arg(cst.Name(param.name.value)))
function_call = cst.SimpleStatementLine([cst.Expr(cst.Call(cst.Name(old_function.name.value), args))])
module = cst.Module([old_function, function_call], header=[cst.EmptyLine(comment=cst.Comment('#test comment'))])
# print(module.code)
with open('old_function.py', 'w') as f:
    f.write(module.code)
with open('new_function.py', 'w') as f:
    f.write(cst.Module([new_function], header=[cst.EmptyLine(comment=cst.Comment('#test comment'))]).code.lstrip())
# print(new_function)
