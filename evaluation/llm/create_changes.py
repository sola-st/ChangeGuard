import subprocess
import re
import json
from collections import namedtuple
import libcst as cst
import libcst.matchers as m
import ast

Position = namedtuple('Position', 'start end')


# copied from fetch_commits.py
def _extract_line_numbers(diff_line):
    old_line_pos = re.search('-([0-9]+)(?:,([0-9]+))?', diff_line)
    new_line_pos = re.search('\+([0-9]+)(?:,([0-9]+))?', diff_line)
    if not (old_line_pos and new_line_pos):
        return None
    old_line_start = int(old_line_pos.group(1))
    old_line_end = old_line_start if not old_line_pos.group(2) else old_line_start + max(int(old_line_pos.group(2)) - 1, 0)
    new_line_start = int(new_line_pos.group(1))
    new_line_end = new_line_start if not new_line_pos.group(2) else new_line_start + max(int(new_line_pos.group(2)) - 1, 0)
    return {'old': Position(old_line_start, old_line_end), 'new': Position(new_line_start, new_line_end)}

# copied from cst_utils.py
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


def same_ast(old, new):
    try:
        code = cst.MetadataWrapper(cst.parse_module(new))
        cleaner = CodeCleaner()
        cleaned_code = code.visit(cleaner).code
        old_tree = ast.parse(old)
        new_tree = ast.parse(cleaned_code)
    except Exception:
        print('Invalid Python')
        return True
    return ast.dump(old_tree) == ast.dump(new_tree)


with open('responses.json', 'r', encoding='utf-8') as f:
    responses = json.load(f)

changes = []

for idx, response in enumerate(responses):
    old = response['old']
    new = response['new'] if response['new'][-1] == '\n' else response['new'] + '\n'
    changed_lines_old = []
    changed_lines_new = []
    if same_ast(old, new):
        print('Skipped because same AST')
        continue
    with open('old.py', 'w', encoding='utf-8') as f:
        f.write(old)
    with open('new.py', 'w', encoding='utf-8') as f:
        f.write(new)
    process = subprocess.run(f'git diff --no-index --unified=0 -p old.py new.py', capture_output=True)
    diffs = process.stdout.decode('utf-8')
    # print(diffs)
    diff_lines = [line for line in diffs.splitlines() if '@@' in line]
    for diff_line in diff_lines:
        line = _extract_line_numbers(diff_line)
        if line:
            changed_lines_old.append(line['old'])
            changed_lines_new.append(line['new'])

    changes.append({
        'repo': 'llm',
        'old_commit': 0,
        'new_commit': idx,
        'old_clean_function': old,
        'new_clean_function': new,
        'old_changed_lines': changed_lines_old,
        'new_changed_lines': changed_lines_new
    })

with open('llm_changes.json', 'w', encoding='utf-8') as f:
    json.dump(changes, f, indent=2)