from dataclasses import dataclass
from AST import Type
from typing import Union, List

class ParseError(Exception): pass

@dataclass
class Variable():
    type: Type

@dataclass
class Function():
    param_types: List[Type]
    return_type: Union[Type, None]

@dataclass
class Functions():
    functions: List[Function]

class SymbolTable(object):
    """
    Base symbol table class
    """

    def __init__(self):
        self.scope_stack = [dict()]
        self.func_call_stack = []

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        assert len(self.scope_stack) > 1
        self.scope_stack.pop()

    def declare_variable(self, name: str, type: Type, line_number=-1):
        """
        Add a new variable.
        Need to do duplicate variable declaration error checking.
        """
        if name in self.scope_stack[-1]:
            raise ParseError("Redeclaring variable named \"" + name + "\"", line_number)
        self.scope_stack[-1][name] = Variable(type=type)

    def lookup_variable(self, name: str, line_number=-1):
        """
        Return the type of the variable named 'name', or throw
        a ParseError if the variable is not declared in the scope.
        """
        # You should traverse through the entire scope stack
        for scope in reversed(self.scope_stack):
            if name in scope:
                found = scope[name]
                assert isinstance(found, Variable), f"When looking for {name}, found function when expecting variable"
                return found.type
        raise ParseError("Referencing undefined variable \"" + name + "\"", line_number)


    def declare_function(self, name: str, param_types: List[Type], return_type: Union[Type, None], line_number=-1):
        function_to_be_declared = Function(param_types, return_type)
        if name in self.scope_stack[-1]:
            if isinstance(self.scope_stack[-1][name], Functions):
                try:
                    self.lookup_function(name, param_types)
                except ParseError:
                    pass # Expect the function to not be found
                else:
                    raise ParseError("Re-declaring function with same param types \""+name+"\"", line_number)

                self.scope_stack[-1][name].functions.append(function_to_be_declared)
            else:
                raise ParseError("Function \"" + name + "\" is previously declared as variable", line_number)

        self.scope_stack[-1][name] = Functions([function_to_be_declared])


    def lookup_function(self, name: str, param_types: List[Type], line_number=-1):
        for scope in reversed(self.scope_stack):
            if name in scope:
                assert isinstance(scope[name], Functions), "Expect function, got probably Variable"
                for f in scope[name].functions:
                    if repr(param_types) == repr(param_types):
                        return f.return_type

        raise ParseError("Referencing undefined function \"" + name + "\"", line_number)


    # def declare_function(self, name: str, param_types, return_type):
    #     function_signature = f"{name}#{repr(param_types)}"
    #     if function_signature in self.scope_stack[-1]:
    #         raise ParseError("Redeclaring variable named \"" + name + "\"")
    #     else:
    #         self.scope_stack[-1][function_signature] = return_type

    # def lookup_function(self, name, param_types):
    #     function_signature = f"{name}#{repr(param_types)}"
