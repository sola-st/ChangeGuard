import libcst as cst
import libcst.matchers as m
from libcst.metadata import ParentNodeProvider, PositionProvider


class CodeRewriter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider,)

    ignored_names = ["True", "False", "None", "isinstance"]
    ignored_calls = ["super"]  # special function names to not instrument

    def __init__(self, file_path, iids, line_coverage_instrumentation, used_names):
        super().__init__()
        self.file_path = file_path
        self.used_names = used_names
        self.iids = iids
        self.line_coverage_instrumentation = line_coverage_instrumentation

        self.instrument = True  # turned off in special cases, e.g., inside nested f-strings

        self.quotation_char = '"'  # flipped to "'" when inside an f-string with double quotes
        self.fstring_stack = []

    def __create_iid(self, node, end_node=None):
        location = self.get_metadata(PositionProvider, node)
        line = location.start.line
        column_start = location.start.column
        column_end = location.end.column
        # only use final line number for SimpleStatementLine because we use this to measure which lines have been
        # executed and block nodes such as FunctionDef would otherwise falsely claim we executed the whole function
        # instead of only the definition
        if end_node is not None:
            line_end = self.get_metadata(PositionProvider, end_node).end.line
        else:
            line_end = location.start.line

        iid = self.iids.new(self.file_path, line, column_start, column_end, line_end)
        return iid

    def __create_name_call(self, node, updated_node):
        callee_name = cst.Name(value="_n_")
        iid = self.__create_iid(node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        name_arg = cst.Arg(cst.SimpleString(
            value=f"{self.quotation_char}{node.value}{self.quotation_char}"))
        lambada = cst.Lambda(params=cst.Parameters(
            params=[]), body=updated_node)
        value_arg = cst.Arg(value=lambada)
        call = cst.Call(func=callee_name, args=[iid_arg, name_arg, value_arg])
        return call

    def __ensure_generator_expr_have_parens(self, args):
        # make sure that generator expressions have parentheses if not the only argument
        updated_args = []
        for arg in args:
            if (isinstance(arg.value, cst.GeneratorExp)
                    and len(arg.value.lpar) == 0
                    and len(arg.value.rpar) == 0):
                g = arg.value
                g_new = cst.GeneratorExp(elt=g.elt,
                                         for_in=g.for_in,
                                         lpar=[cst.LeftParen()],
                                         rpar=[cst.RightParen()])
                updated_args.append(cst.Arg(value=g_new))
            else:
                updated_args.append(arg)
        return updated_args

    def __get_callee_name_node(self, call_node):
        if isinstance(call_node.func, cst.Name):
            return call_node.func
        elif isinstance(call_node.func, cst.Attribute):
            return call_node.func.attr
        else:  # everything else, e.g., cst.Subscript
            return call_node.func

    def __create_call_call(self, node, updated_node):
        callee_name = cst.Name(value="_c_")
        node_of_callee_name = self.__get_callee_name_node(node)
        iid = self.__create_iid(node_of_callee_name)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        fct_arg = cst.Arg(value=updated_node.func)
        full_name = self.__unfold_node(node)
        full_name_arg = cst.Arg(value=cst.SimpleString(value=full_name))
        all_args = [iid_arg, fct_arg, full_name_arg] + \
            self.__ensure_generator_expr_have_parens(updated_node.args)
        call = cst.Call(func=callee_name, args=all_args)
        return call

    def __create_attribute_call(self, node, updated_node):
        callee_name = cst.Name(value="_a_")
        assert type(node.attr) == cst.Name, type(node.attr)
        iid = self.__create_iid(node.attr)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        value_arg = cst.Arg(updated_node.value)
        attr_arg = cst.Arg(cst.SimpleString(
            value=f"{self.quotation_char}{node.attr.value}{self.quotation_char}"))
        full_name = self.__unfold_node(node)
        full_name_arg = cst.Arg(value=cst.SimpleString(value=full_name))
        call = cst.Call(func=callee_name, args=[iid_arg, value_arg, attr_arg, full_name_arg])
        return call
    
    def __create_line_call(self, node, updated_node, end_node):
        callee_name = cst.Name(value="_l_")
        iid = self.__create_iid(node, end_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        call = cst.Call(func=callee_name, args=[iid_arg])
        return call
    
    def __create_line_call_stmt(self, node, updated_node, end_node):
        statement_call = self.__create_line_call(node, updated_node, end_node)
        stmt = cst.SimpleStatementLine(body=[cst.Expr(value=statement_call)],
                                trailing_whitespace=cst.TrailingWhitespace(
                                    whitespace=cst.SimpleWhitespace(value='',)
                                ),
                            )
        return stmt

    def __create_subscript_call(self, original_node: cst.Subscript, updated_node: cst.Subscript):
        callee_name = cst.Name(value='_s_')
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        full_name = self.__unfold_node(original_node)
        name_arg = cst.Arg(value=cst.SimpleString(value=full_name))
        # TODO include index/slice arg (not trivial because of extended slices e.g np indexes)
        lambada = cst.Lambda(params=cst.Parameters(
            params=[]), body=updated_node)
        return cst.Call(func=callee_name, args=[iid_arg, name_arg, cst.Arg(value=lambada)])

    def __create_aux_stmt(self, updated_node, value):
        aux_stmt = cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                    targets=[
                        cst.AssignTarget(
                        target=cst.Name(value='aux', lpar=[], rpar=[],),
                        whitespace_before_equal=cst.SimpleWhitespace(value=' ',),
                        whitespace_after_equal=cst.SimpleWhitespace(value=' ',),),
                    ],
                    value=value
                    )
                ],
                trailing_whitespace=updated_node.trailing_whitespace
            )
        return aux_stmt

    def __update_indented_block(self, node, updated_node, end_node):
        stmt = self.__create_line_call_stmt(node, updated_node, end_node)
        body_content = [stmt, cst.Expr(cst.Newline())]
        body_content.extend(updated_node.body.body)
        new_body = cst.IndentedBlock(body=body_content)
        return updated_node.with_changes(body=new_body)
        
    def __create_import(self, name):
        module_name = cst.Attribute(value=cst.Name(
            value="lexecutor"), attr=cst.Name(value="Runtime"))
        fct_name = cst.Name(value=name)
        imp_alias = cst.ImportAlias(name=fct_name)
        imp = cst.ImportFrom(module=module_name, names=[imp_alias])
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt

    def __wrap_import(self, node, updated_node):
        statement_call = self.__create_line_call(node, updated_node, node)
        stmt = cst.SimpleStatementLine(body=[cst.Expr(value=statement_call)],
                                trailing_whitespace=cst.TrailingWhitespace(
                                    whitespace=cst.SimpleWhitespace(value='',)
                                ),
                            )
        body_content = [cst.SimpleStatementLine(body=[updated_node])]
        body_content.extend([stmt, cst.Expr(cst.Newline())])

        try_stmt = cst.Try(body=cst.IndentedBlock(
            body=body_content),
            handlers=[cst.ExceptHandler(body=cst.IndentedBlock(
                body=[cst.SimpleStatementLine(body=[cst.Pass()])]),
                type=cst.Name(value="ImportError"))])
        return try_stmt

    def __is_l_value(self, node):
        parent = self.get_metadata(ParentNodeProvider, node)

        # assignments to a single value
        if (type(parent) == cst.AssignTarget or
                type(parent) == cst.AnnAssign or
                type(parent) == cst.AugAssign):
            return True

        # multi-assignments
        if type(parent) == cst.Element:
            grand_parent = self.get_metadata(ParentNodeProvider, parent)
            if type(grand_parent) == cst.Tuple:
                grand_grand_parent = self.get_metadata(
                    ParentNodeProvider, grand_parent)
                if (type(grand_grand_parent) == cst.AssignTarget or
                    type(grand_grand_parent) == cst.AnnAssign or
                        type(grand_grand_parent) == cst.AugAssign):
                    return True

        return False

    def __is_ignored_call(self, call_node):
        if type(call_node.func) == cst.Name:
            return call_node.func.value in self.ignored_calls
        else:
            return False

    def __unfold_node(self, node):
        name = cst.helpers.get_full_name_for_node(node)
        return self.quotation_char + (name if name is not None else '_anon_') + self.quotation_char

    def visit_SimpleStatementLine(self, node):
        # don't visit lines marked with special comment
        c = node.trailing_whitespace.comment
        if c is not None and c.value == "# don't instrument":
            return False
        return True

    def visit_Import(self, node):
        # don't instrument imports, as we'll wrap them in try-except
        return False

    def visit_ImportFrom(self, node):
        # don't instrument imports, as we'll wrap them in try-except
        return False

    def visit_Del(self, node):
        # don't instrument delete statements, as "del" on call on allowed
        return False

    def visit_FormattedString(self, node):
        if node.start == 'f"' or node.start == 'fr"' or node.start == 'rf"':
            self.quotation_char = "'"
            self.fstring_stack.append(node)
        elif node.start == "f'" or node.start == "fr'" or node.start == 'rf"':
            self.quotation_char = '"'
            self.fstring_stack.append(node)
        if len(self.fstring_stack) > 1:
            self.instrument = False
        return True

    def leave_FormattedString(self, node, updated_node):
        if self.fstring_stack and node == self.fstring_stack[-1]:
            # flip quotation character back
            if self.quotation_char == "'":
                self.quotation_char = '"'
            elif self.quotation_char == '"':
                self.quotation_char = "'"
            self.fstring_stack.pop()
            if len(self.fstring_stack) < 2:
                self.instrument = True
        return updated_node

    def leave_Call(self, node, updated_node: cst.Call):
        # replace super() / super().init__() calls since we treat all functions / methods as regular functions
        if m.matches(node, m.Call(func=m.Attribute(value=m.Call(func=m.Name(value='super')), attr=m.Name(value='__init__')))):
            return cst.Call(func=cst.Name(value='_dummy_super_init__'), args=updated_node.args)
        if isinstance(node.func, cst.Name) and node.func.value == 'super':
            return updated_node.with_changes(func=cst.Name('_dummy_super'))

        # replace isinstance checks with modified check
        if isinstance(updated_node.func, cst.Name) and updated_node.func.value == 'isinstance':
            return updated_node.with_changes(func=cst.Name('_isinstance'))
        # rewrite Call nodes to intercept function calls
        if not self.__is_ignored_call(node) and not self.line_coverage_instrumentation:
            wrapped_call = self.__create_call_call(node, updated_node)
            return wrapped_call
        else:
            return updated_node

    def leave_Name(self, node, updated_node):
        if not self.instrument:
            return updated_node

        # rewrite Name nodes to intercept values they resolve to
        if node in self.used_names and node.value not in self.ignored_names and not self.line_coverage_instrumentation:
            wrapped_name = self.__create_name_call(node, updated_node)
            return wrapped_name
        else:
            return updated_node

    def leave_Attribute(self, node, updated_node):
        if not self.instrument:
            return updated_node

        if not self.__is_l_value(node) and not self.line_coverage_instrumentation:
            wrapped_attribute = self.__create_attribute_call(node, updated_node)
            return wrapped_attribute
        else:
            return updated_node

    def leave_Subscript(self, original_node: cst.Subscript, updated_node: cst.Subscript):
        if not self.instrument:
            return updated_node

        if not self.__is_l_value(original_node) and not self.line_coverage_instrumentation:
            return self.__create_subscript_call(original_node, updated_node)
        return updated_node

    def leave_SimpleStatementLine(self, node, updated_node):
        if isinstance(node.body[0], cst.Expr):
            if isinstance(node.body[0].value, cst.SimpleString):
                if node.body[0].value.value.startswith('"""'):
                    return updated_node
            
        statement_call = self.__create_line_call(node, updated_node, node)
        stmt = cst.SimpleStatementLine(body=[cst.Expr(value=statement_call)],
                                trailing_whitespace=updated_node.trailing_whitespace)

        # Put line call in front of statements as it is otherwise never reached
        if isinstance(node.body[0], (cst.Continue, cst.Break, cst.Raise)):
            return cst.FlattenSentinel([stmt, updated_node])

        if isinstance(node.body[0], cst.Pass):
            return cst.FlattenSentinel([updated_node, stmt])
        if isinstance(node.body[0], cst.Return):
            if node.body[0].value:
                value = updated_node.body[0].value
            else:
                value = cst.Name(value='None')
            aux_stmt = self.__create_aux_stmt(updated_node, value)
            new_return_content = [cst.Return(value=cst.Name(value='aux',lpar=[],rpar=[],),
                                whitespace_after_return=cst.SimpleWhitespace(value=' ',),
                                semicolon=cst.MaybeSentinel.DEFAULT,)]
            return cst.FlattenSentinel([aux_stmt, stmt, updated_node.with_changes(body=new_return_content)])
        try:
            if isinstance(node.body[0], cst.Expr) and isinstance(node.body[0].value, cst.Call) and node.body[0].value.func.value == 'exit':
                if len(updated_node.body[0].value.args) < 3:
                    value = cst.SimpleString(value='""',lpar=[],rpar=[],)
                else:
                    value = updated_node.body[0].value.args[2]
                aux_stmt =  self.__create_aux_stmt(updated_node, value)
                new_exit_content = [cst.Expr(
                    value=cst.Call(
                        func=cst.Name(value='exit',lpar=[],rpar=[],),
                        args=[cst.Arg(
                                value=cst.Name(value='aux',lpar=[],rpar=[],),
                                keyword=None,
                                equal=cst.MaybeSentinel.DEFAULT,
                                comma=cst.MaybeSentinel.DEFAULT,
                                star='',
                                whitespace_after_star=cst.SimpleWhitespace(value='',),
                                whitespace_after_arg=cst.SimpleWhitespace(value='',),
                            ),],lpar=[],rpar=[],
                        whitespace_after_func=cst.SimpleWhitespace(value='',),
                        whitespace_before_args=cst.SimpleWhitespace(value='',),),
                    semicolon=cst.MaybeSentinel.DEFAULT,)]
                return cst.FlattenSentinel([aux_stmt, stmt, updated_node.with_changes(body=new_exit_content)])
        except Exception as e:
            print(e)
        if not self.instrument:
            return cst.FlattenSentinel([updated_node, stmt])

        # surround imports with try-except;
        # cannot do this in leave_Import because we need to replace the import's parent node
        if isinstance(node.body[0], cst.Import) or isinstance(node.body[0], cst.ImportFrom):
            # don't wrap __future__ imports
            if not (isinstance(node.body[0], cst.ImportFrom) and
                    node.body[0].module is not None and
                    node.body[0].module.value == "__future__"):
                # don't try-except-pass wrap imports that are already surrounded by try-except (as they should sometimes fail)
                skip = False
                parent = self.get_metadata(ParentNodeProvider, node)
                if isinstance(parent, cst.IndentedBlock):
                    grand_parent = self.get_metadata(
                        ParentNodeProvider, parent)
                    if isinstance(grand_parent, cst.Try):
                        skip = True
                if not skip:
                    wrapped_import = self.__wrap_import(
                        node.body[0], updated_node.body[0])
                    return wrapped_import
        return cst.FlattenSentinel([updated_node, stmt])

    def leave_For(self, node: cst.For, updated_node: cst.For):
        line_call = self.__create_line_call(node, updated_node, node.iter)

        # handle iteration over tuple without parens
        if isinstance(updated_node.iter, cst.Tuple) and not updated_node.iter.lpar and not updated_node.iter.rpar:
            for_iter = updated_node.iter.with_changes(lpar=[cst.LeftParen()], rpar=[cst.RightParen()])
        else:
            for_iter = updated_node.iter
        line_call = line_call.with_changes(args=[*line_call.args, cst.Arg(value=for_iter)])
        ws = node.whitespace_after_for if node.whitespace_after_for.value else cst.SimpleWhitespace(value=' ')
        return updated_node.with_changes(iter=line_call, whitespace_after_for=ws)
    
    def leave_While(self, node: cst.While, updated_node: cst.While):
        line_call = self.__create_line_call(node, updated_node, node.test)
        line_call = line_call.with_changes(args=[*line_call.args, cst.Arg(value=updated_node.test)])
        ws = node.whitespace_after_while if node.whitespace_after_while.value else cst.SimpleWhitespace(value=' ')
        return updated_node.with_changes(test=line_call, whitespace_after_while=ws)

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node):
        return self.__update_indented_block(node, updated_node, node.params)

    def leave_ClassDef(self, node: cst.ClassDef, updated_node):
        return self.__update_indented_block(node, updated_node, node.bases[-1] if node.bases else None)
    
    def leave_With(self, node: cst.With, updated_node):
        return self.__update_indented_block(node, updated_node, node.items[-1])
    
    def leave_If(self, node: cst.If, updated_node: cst.If):
        line_call = self.__create_line_call(node, updated_node, node.test)
        line_call = line_call.with_changes(args=[*line_call.args, cst.Arg(value=updated_node.test)])
        ws = node.whitespace_before_test if node.whitespace_before_test.value else cst.SimpleWhitespace(value=' ')
        return updated_node.with_changes(test=line_call, whitespace_before_test=ws)

    def leave_Else(self, node, updated_node):
        return self.__update_indented_block(node, updated_node, None)

    def leave_Try(self, node, updated_node):
        return self.__update_indented_block(node, updated_node, None)
    
    def leave_ExceptHandler(self, node: cst.ExceptHandler, updated_node: cst.ExceptHandler):

        if node.type is None:
            return self.__update_indented_block(node, updated_node, None)

        try_statement: cst.Try = self.get_metadata(ParentNodeProvider, node)
        raise_statements = m.findall(try_statement.body, m.Raise())

        def compare_exceptions(raised_exc, caught_exc):
            if isinstance(raised_exc, cst.Name) and isinstance(caught_exc, cst.Name) and raised_exc.value == caught_exc.value:
                return True
            elif isinstance(raised_exc, cst.Attribute) and isinstance(caught_exc, cst.Attribute) and self.__unfold_node(raised_exc) == self.__unfold_node(caught_exc):
                return True
            elif isinstance(raised_exc, cst.Call):
                if isinstance(raised_exc.func, cst.Name) and isinstance(caught_exc, cst.Name) and raised_exc.func.value == caught_exc.value:
                    return True
                elif isinstance(raised_exc.func, cst.Attribute) and isinstance(caught_exc, cst.Attribute) and self.__unfold_node(raised_exc.func) == self.__unfold_node(caught_exc):
                    return True
            return False

        if isinstance(node.type, cst.Tuple):
            new_elements = []
            for element in node.type.elements:
                for raise_statement in raise_statements:
                    if not raise_statement.exc:
                        continue
                    if compare_exceptions(raise_statement.exc, element.value):
                        new_elements.append(cst.Element(value=cst.Call(
                                        func=cst.Attribute(value=cst.Name(value='ExceptionFactory'),
                                                           attr=cst.Name(value='intentional_exception_type')),
                                        args=[cst.Arg(value=cst.SimpleString(self.__unfold_node(element.value)))])))
                        break
                else:
                    new_elements.append(cst.Element(value=cst.StarredElement(value=cst.Call(
                        func=cst.Attribute(value=cst.Name(value='ExceptionFactory'),
                                           attr=cst.Name(value='exception_type')),
                        args=[cst.Arg(value=cst.SimpleString(self.__unfold_node(element.value)))]))))

            return self.__update_indented_block(node, updated_node.with_changes(type=cst.Tuple(elements=new_elements)), node.type)
        else:
            name = self.__unfold_node(node.type)
            for raise_statement in raise_statements:
                if not raise_statement.exc:
                    continue
                if compare_exceptions(raise_statement.exc, node.type):
                    return self.__update_indented_block(node, updated_node.with_changes(type=cst.Call(func=cst.Attribute(value=cst.Name(value='ExceptionFactory'),
                                                                                        attr=cst.Name(value='intentional_exception_type')),
                                                                                                      args=[cst.Arg(value=cst.SimpleString(name))])), node.type)
            return self.__update_indented_block(node, updated_node.with_changes(
                type=cst.Call(func=cst.Attribute(value=cst.Name(value='ExceptionFactory'),
                                                 attr=cst.Name(value='exception_type')),
                              args=[cst.Arg(value=cst.SimpleString(name))])), node.type)


    def leave_Finally(self, node, updated_node):
        return self.__update_indented_block(node, updated_node, None)

    def leave_Raise(self, original_node, updated_node):
        # updated_node.exc is always cst.Call since exception node is wrapped in either _n_, _c_, or _a_ first.
        # or None for bare raise statements
        old_exception: cst.Call = updated_node.exc
        if old_exception and old_exception.func.value == '_n_':
            args = [cst.Arg(value=old_exception)]
        elif old_exception and old_exception.func.value == '_c_':
            # index 0 is iid of _c_ call
            name_call = [old_exception.args[1]]
            remaining_args = old_exception.args[2:]
            args = name_call + remaining_args
        elif old_exception and old_exception.func.value == '_a_':
            args = [cst.Arg(value=old_exception)]
        else:
            return updated_node
        static_name = self.__unfold_node(original_node.exc)
        args = [cst.Arg(value=cst.SimpleString(value=static_name))] + args
        custom_exception: cst.Call = cst.Call(args=args,
                                              func=cst.Attribute(value=cst.Name(value='ExceptionFactory'),
                                                                 attr=cst.Name(value='intentional_exception')))
        return updated_node.with_changes(exc=custom_exception)

    def leave_Module(self, node, updated_node):
        if not self.instrument:
            return updated_node
        
        # check for "__future__" imports; they must remain at beginning of file
        target_idx = 0  # index to add our imports at
        new_body = []
        for i in range(len(updated_node.body)):
            stmt = updated_node.body[i]
            new_body.append(stmt)

            if (isinstance(stmt, cst.SimpleStatementLine)
               and isinstance(stmt.body[0], cst.ImportFrom)
               and stmt.body[0].module.value == "__future__"):
                target_idx = i + 1
            
        # add our imports
        import_n = self.__create_import("_n_")
        import_a = self.__create_import("_a_")
        import_c = self.__create_import("_c_")
        import_l = self.__create_import("_l_")
        import_s = self.__create_import("_s_")
        import_e = self.__create_import("ExceptionFactory")
        import_i = self.__create_import("_isinstance")
        import_su = self.__create_import("_dummy_super")
        import_sui = self.__create_import("_dummy_super_init__")

        new_body = (list(new_body[:target_idx])
                    + [import_n, import_a, import_c, import_l, import_s, import_e, import_i, import_su, import_sui]
                    + list(new_body[target_idx:]))

        return updated_node.with_changes(body=new_body)
