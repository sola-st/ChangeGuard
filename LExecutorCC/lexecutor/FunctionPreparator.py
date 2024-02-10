import libcst as cst
import libcst.matchers as m


class FunctionPreparator(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider, cst.metadata.WhitespaceInclusivePositionProvider)

    def __init__(self, suffix):
        super().__init__()
        self._nb_param_lines = -1
        self.suffix = suffix
        self.params = []
        self.strings = set()
        self.integers = set()
        self.floats = set()
        self.fun_name = ''

    def leave_Integer(self, original_node: cst.Integer, updated_node: cst.Integer):
        self.integers.add(updated_node.evaluated_value)
        return updated_node

    def leave_Float(self, original_node: cst.Float, updated_node: cst.Float):
        self.floats.add(updated_node.evaluated_value)
        return updated_node

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString):
        if (not isinstance(self.get_metadata(cst.metadata.ParentNodeProvider, original_node), cst.Arg) and
                updated_node.prefix not in ["b", "br", "rb"]):  # skip bytes for now
            self.strings.add(updated_node.evaluated_value)
        return updated_node

    def visit_Parameters(self, node: cst.Parameters):
        if self._nb_param_lines >= 0:  # ensure this is only set for outermost function
            return True
        position = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, node)
        self._nb_param_lines = position.end.line - position.start.line

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
        if not isinstance(self.get_metadata(cst.metadata.ParentNodeProvider, original_node), cst.Module):
            return updated_node  # not outermost function
        parameters = updated_node.params
        self.params.extend(map(lambda x: x.name.value, parameters.params))
        self.params.extend(map(lambda x: x.name.value, parameters.kwonly_params))
        self.params.extend(map(lambda x: x.name.value, parameters.posonly_params))
        if isinstance(parameters.star_arg, cst.Param):
            self.params.append(parameters.star_arg.name.value)
        if parameters.star_kwarg is not None:
            self.params.append(parameters.star_kwarg.name.value)

        fun_name = updated_node.name.value + self.suffix
        self.fun_name = fun_name

        # make sure that no lines are removed when deleting parameters
        if self._nb_param_lines > 0:
            if isinstance(original_node.whitespace_before_params, cst.SimpleWhitespace):
                whitespace = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(),
                    empty_lines=[cst.EmptyLine() for _ in range(self._nb_param_lines - 1)],
                    last_line=cst.SimpleWhitespace(value='')
                )
            elif isinstance(original_node.whitespace_before_params, cst.ParenthesizedWhitespace):
                whitespace = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(whitespace=cst.SimpleWhitespace(value=''),
                                                      newline=cst.Newline(value=None)),
                    empty_lines=[cst.EmptyLine() for _ in
                                 range(self._nb_param_lines + len(original_node.whitespace_before_params.empty_lines))],
                    indent=True,
                    last_line=cst.SimpleWhitespace(value='')
                )
            else:  # hopefully does not happen
                whitespace = updated_node.whitespace_before_params
        else:
            whitespace = updated_node.whitespace_before_params

        return updated_node.with_changes(name=updated_node.name.with_changes(value=fun_name),
                                         whitespace_before_params=whitespace,
                                         params=cst.Parameters(params=[], star_arg=cst.MaybeSentinel.DEFAULT,
                                                               kwonly_params=[], star_kwarg=None, posonly_params=[],
                                                               posonly_ind=cst.MaybeSentinel.DEFAULT))



class OffsetProvider(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, *fct_names):
        super().__init__()
        self.fct_names = fct_names
        self.offsets = {}

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
        if original_node.name.value not in self.fct_names:
            return
        position = self.get_metadata(cst.metadata.PositionProvider, original_node)
        self.offsets[original_node.name.value.split('_')[-1]] = position.start.line, position.end.line
