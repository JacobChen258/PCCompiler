import AST
from AST import Type, PrimitiveType, NonPrimitiveType
from symbol_table import SymbolTable, ParseError
from typing import Union

class TypeChecker:

    def typecheck(self, node, st=None) -> Union[Type, None]:
        method = 'check_' + node.__class__.__name__
        result_type = getattr(self, method, self.generic_typecheck)(node, st)
        assert isinstance(result_type, AST.Type) or result_type is None
        return result_type

    def generic_typecheck(self, node, st=None):
        assert False, '??'
        # if node is None:
        #     return ''
        # else:
        #     return ''.join(self.typecheck(c, st) for c_name, c in node.children())


    def check_FunctionDef(self, node: AST.FunctionDef, st: SymbolTable):
        param_lst = node.lst.lst or []

        if node.returnType is not None:
            return_type = node.returnType
        else:
            return_type = None

        st.declare_function(node.name.name, param_lst, return_type)
        st.func_call_stack.append(return_type)

        st.push_scope()

        for function_body_statement in node.body.lst:
            self.typecheck(function_body_statement, st)

        st.pop_scope()
        st.func_call_stack.pop()


    def check_FunctionCall(self, node: AST.FunctionCall, st: SymbolTable) -> Type:
        arg_types = []
        if node.lst.lst:
            for argument_expression in node.lst.lst:
                arg_types.append(self.typecheck(argument_expression, st))

        return st.lookup_function(node.name.name, arg_types)


    def check_ReturnStmt(self, node: AST.ReturnStmt, st: SymbolTable):
        return_type = self.typecheck(node.stmt, st)
        if len(st.func_call_stack) == 0:
            raise ParseError("Unexpected empty list for st.func_call_stack")

        func_return_type = st.func_call_stack[-1]
        if not func_return_type and not return_type:
            # Both are None
            pass

        elif func_return_type and return_type:
            self.assert_same_type(func_return_type, return_type)

        else:
            raise ParseError("The return type does no match the last declared function call" + \
                f"at node: {repr(node)}")


    # def get_ParameterLst(self, node: AST.ParameterLst):
    #     types = []
    #     if node.lst:
    #         for i in node.lst:
    #             types.append(self.get_GenericType(i))
    #     return types

    # def get_Parameter(self, node: AST.Parameter):
    #     return self.get_GenericType(node.paramType)

    # def get_PrimitiveType(self, node: AST.PrimitiveType):
    #     return Type(value=node)

    # def get_NonPrimitiveType(self, node: AST.NonPrimitiveType):
    #     return Type(value=node)


    def assert_same_type(self, t1: Type, t2: Type):
        """
        Helper function to check if two given type node is that of the
        same type. Precondition is that both t1 and t2 are that of class Type
        """
        assert isinstance(t1, Type)
        assert isinstance(t2, Type)

        if not (isinstance(t1.value, AST.PrimitiveType) and isinstance(t2.value, AST.PrimitiveType)) and \
                not (isinstance(t1.value, AST.NonPrimitiveType) and isinstance(t2.value, AST.NonPrimitiveType)):
            raise ParseError(f"Different class type: t1={t1.__class__.__name__} t2={t2.__class__.__name__}")

        if repr(t1.value) != repr(t2.value): # Handles nested types
            raise ParseError(f"Different type: t1={repr(t1)} t2={repr(t2)}")


    def check_Assignment(self, node: AST.Assignment, st: SymbolTable) -> Type:
        variable_name = node.left.name
        variable_type = None
        try:
            variable_type = st.lookup_variable(variable_name)
        except ParseError:
            # Variable does not exist, declare it now, and check RHS type
            variable_type = node.type
            assert variable_type is not None, f"When declaring {node.left.name}, type is missing"
            st.declare_variable(variable_name, variable_type)
            assert variable_type.type == self.typecheck(node.right, st)
        else:
            # Variable already exists, check the type of RHS
            assert variable_type.type == self.typecheck(node.right, st)

        return variable_type.type


    def check_RangeValues(self, node: AST.RangeValues, st: SymbolTable) -> None:
        int_type = Type(PrimitiveType('int'))
        self.assert_same_type(int_type, self.typecheck(node.start.value, st))
        if node.stop is not None:
            self.assert_same_type(int_type, self.typecheck(node.stop.value, st))
        if node.step is not None:
            self.assert_same_type(int_type, self.typecheck(node.step.value, st))
        return None


    def check_ForLoopList(self, node: AST.ForLoopList, st: SymbolTable) -> None:
        list_type = self.typecheck(node.Lst, st)
        st.push_scope()
        st.declare_variable(node.var.name, list_type.value)
        for body_statement in node.body.lst:
            self.typecheck(body_statement, st)
        st.pop_scope()
        return None


    def check_ForLoopRange(self, node: AST.ForLoopRange, st: SymbolTable) -> None:
        list_type = Type(PrimitiveType('int'))
        st.push_scope()
        st.declare_variable(node.var.name, list_type.value)
        for body_statement in node.body.lst:
            self.typecheck(body_statement, st)
        st.pop_scope()
        return None


"""

for a in [1,2,3]:
    pass


list_list_list_int

"""


