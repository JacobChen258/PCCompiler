import AST
from symbol_table import SymbolTable, ParseError

class TypeChecker:

    def typecheck(self, node, st=None):
        method = 'check_' + node.__class__.__name__
        return getattr(self, method, self.generic_typecheck)(node, st)


    def generic_typecheck(self, node, st=None):
        if node is None:
            return ''
        else:
            return ''.join(self.typecheck(c, st) for c_name, c in node.children())


    def assert_same_type(self, t1, t2):
        """
        Helper function to check if two given type node is that of the
        same type. Precondition is that both t1 and t2 are that of class Type
        """
        if not (isinstance(t1, AST.PrimitiveType) and isinstance(t2, AST.PrimitiveType)) and \
                not (isinstance(t1, AST.NonPrimitiveType) and isinstance(t2, AST.NonPrimitiveType)):
            raise ParseError(f"Different class type: t1={t1.__class__.__name__} t2={t2.__class__.__name__}")

        if repr(t1) != repr(t2): # Handles nested types
            raise ParseError(f"Different type: t1={repr(t1)} t2={repr(t2)}")


    def check_Assignment(self, node: AST.Assignment, st: SymbolTable):
        variable_name = node.left.name
        variable_type = None
        try:
            variable_type = st.lookup_variable(variable_name)
        except ParseError:
            # Variable does not exist, declare it now, and check RHS type
            variable_type = node.type
            assert variable_type is not None, f"When declaring {node.left.name}, type is missing"
            st.declare_variable(variable_name, variable_type)
            assert variable_type == self.typecheck(node.right)
        else:
            # Variable already exists, check the type of RHS
            assert variable_type == self.typecheck(node.right)


