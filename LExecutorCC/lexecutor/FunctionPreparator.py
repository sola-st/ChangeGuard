import libcst as cst
import libcst.matchers as m


def __unfold_attribute_name(attribute_node: cst.Attribute):
    names = []
    # unfolding x.y.z.Exception
    base = attribute_node.value
    while not isinstance(base, cst.Name):
        names.append(base.attr.value)
        base = base.value
    names.append(base.value)
    names.reverse()
    names.append(attribute_node.attr.value)
    return '.'.join(names)


def compare_exceptions(raised_exc, caught_exc):
    if isinstance(raised_exc, cst.Name) and isinstance(caught_exc, cst.Name) and raised_exc.value == caught_exc.value:
        return True
    elif isinstance(raised_exc, cst.Attribute) and isinstance(caught_exc,
                                                              cst.Attribute) and __unfold_attribute_name(
            raised_exc) == __unfold_attribute_name(caught_exc):
        return True
    elif isinstance(raised_exc, cst.Call):
        if isinstance(raised_exc.func, cst.Name) and isinstance(caught_exc,
                                                                cst.Name) and raised_exc.func.value == caught_exc.value:
            return True
        elif isinstance(raised_exc.func, cst.Attribute) and isinstance(caught_exc,
                                                                       cst.Attribute) and __unfold_attribute_name(
                raised_exc.func) == __unfold_attribute_name(caught_exc):
            return True
    return False

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
        self.func_to_exc = {}
        self.found_classes = {'None'}

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

    def visit_Try(self, node: cst.Try):
        call_statements = m.findall(node.body, m.Call())
        raise_statements = m.findall(node.body, m.Raise())
        caught_types = set()
        for handler in node.handlers:
            if isinstance(handler.type, cst.Tuple):
                for element in handler.type.elements:
                    if not any(compare_exceptions(raise_statement.exc, element.value) for raise_statement in raise_statements):
                        caught_types.add(cst.helpers.get_full_name_for_node(element.value))
            else:
                if not any(compare_exceptions(raise_statement.exc, handler.type) for raise_statement in raise_statements):
                    caught_types.add(cst.helpers.get_full_name_for_node(handler.type))
        for call_statement in call_statements:
            if isinstance(self.get_metadata(cst.metadata.ParentNodeProvider, call_statement), cst.Raise):
                continue
            name = cst.helpers.get_full_name_for_node(call_statement)
            if not name:
                continue
            already_found_types = self.func_to_exc.get(name, set())
            already_found_types.update(caught_types)
            self.func_to_exc[name] = already_found_types

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

    def leave_Call(self, node: cst.Call, updated_node: cst.Call):
        if not m.matches(node.func, m.Name(value='isinstance')):
            return updated_node
        try:
            classes_to_look_at = [node.args[1].value]
            while len(classes_to_look_at) > 0:
                cur_class = classes_to_look_at.pop()
                if isinstance(cur_class, cst.Tuple):
                    classes_to_look_at.extend(map(lambda x: x.value, cur_class.elements))
                if isinstance(cur_class, cst.Name):
                    self.found_classes.add(cur_class.value)
                if isinstance(cur_class, cst.Attribute):
                    self.found_classes.add(cst.helpers.get_full_name_for_node(cur_class))
        except (IndexError, AttributeError):
            pass
        return updated_node


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
