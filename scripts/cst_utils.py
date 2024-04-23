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
