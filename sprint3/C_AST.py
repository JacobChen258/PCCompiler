from __future__ import annotations
from typing import Union, List
from dataclasses import dataclass


@dataclass
class Type:
    value: str # 'str_t', 'int_t', 'float_t', 'bool_t'
    # str_t -> char*
    # int_t -> long long
    # float_t -> double
    # bool_t -> bool or int

@dataclass
class NonPrimitiveType:
    type: Union['list', 'tuple']

@dataclass
class Id:
    name: str

@dataclass
class Declaration:
    id: Id
    type: Type

@dataclass
class UnaryOperation:
    left: Id
    operator: str
    operand: Id

@dataclass
class BinaryOperation:
    left: Id
    operator: str
    operand_a: Id
    operand_b: Id

@dataclass
class Parameter:
    paramType: Type
    var: Id

@dataclass
class ParameterLst:
    lst: List[Parameter]

@dataclass
class FunctionDeclaration:
    name: Id
    lst: ParameterLst
    body: Block
    returnType: Union[Type, None]

@dataclass
class IfStmt:
    ifCond: Id
    body: Block

@dataclass
class ElifStmt:
    elifCond: Id
    body: Block

@dataclass
class ElseStmt:
    body: Block

@dataclass
class WhileStmt:
    cond: Id
    body: Block

@dataclass
class RangeValues:
    stop: Union[Expression, None]
    start: Union[Expression, None]
    step: Union[Expression, None]

@dataclass
class ForLoopRange:
    var: Id
    rangeVal: RangeValues
    body: Block

@dataclass
class ForLoopList:
    var: Id
    Lst: Expression
    body: Block

@dataclass
class Expression:
    value: Union[BinaryOperation, UnaryOperation, Id]

@dataclass
class ArgumentLst:
    lst: Union[List[Expression], None]

@dataclass
class ReturnStmt:
    stmt: Expression

@dataclass
class FunctionCall:
    name: Id
    lst: ArgumentLst

@dataclass
class Block:
    lst: List[Union[FunctionDeclaration, ReturnStmt, FunctionCall, ForLoopRange, ForLoopList, WhileStmt, \
                    IfStmt, ElifStmt, ElseStmt, BinaryOperation, UnaryOperation]]

@dataclass
class Assignment:
    id : Id
    val: any

@dataclass
class ReturnStatement:
    value: Id

@dataclass
class PrimitiveLiteral:
    id: Id
    type: Type
    value: any

class CCodeGenerator:
    function_declarations = []
    function_definitions = []
    state_in_function_declaration = False

    def generate_code(self, root):
        structure = self.gen(root)
        formatted = self.generate_code_formatter(structure)
        declarations_str, definitions_str = self.generate_function_code()
        return self.code_template(declarations_str, definitions_str, formatted)

    def generate_function_code(self):
        declarations_str = ";\n".join(self.function_declarations) + ";"
        definitions_str = ""
        for definition in self.function_definitions:
            formatted = self.generate_code_formatter(definition)
            definitions_str += formatted
        return declarations_str, definitions_str

    def generate_code_formatter(self, structure, indent=0):
        result = ""
        for line in structure:
            if line is None:
                continue
            if isinstance(line, tuple):
                code = self.generate_code_formatter(line, indent)
            elif isinstance(line, list):
                code = self.generate_code_formatter(line, indent + 1)
            else:
                code = "    " * indent + line + "\n"
            result += code
        return result

    def code_template(self, function_declarations, function_definitions, main_code):
        return f"""
#include <stdio.h>
#include <stdbool.h>

typedef long long int_t;
typedef double float_t;
typedef bool bool_t;
bool True = true;
bool False = false;
/***** Function declarations *****/
{function_declarations}
/***** End of function declarations *****/

/***** Function definitions *****/
{function_definitions}
/***** End of function definitions *****/


int main() {{

/***** Main *****/
{main_code}
/***** End of main *****/

    return 0;
}}
        """

    def gen(self, node):
        method = 'gen_' + node.__class__.__name__
        try:
            return getattr(self, method)(node)
        except AttributeError:
            print(f"Trying to process node {node}")
            raise

    def gen_Block(self, node: Block):
        return [self.gen(x) for x in node.lst]

    def gen_Expression(self, node: Expression):
        return self.gen(node.value)

    def gen_Id(self, node: Id):
        return node.name

    def gen_Declaration(self, node: Declaration):
        return f"{self.gen(node.type)} {self.gen(node.id)};"

    def gen_Type(self, node: Type):
        assert node.value in ['str_t', 'int_t', 'float_t', 'bool_t']
        return node.value

    def gen_UnaryOperation(self, node: UnaryOperation):
        return f"{self.gen(node.left)} = {node.operator} {self.gen(node.operand)};"

    def gen_BinaryOperation(self, node: BinaryOperation):
        return f"{self.gen(node.left)} = {self.gen(node.operand_a)} {node.operator} {self.gen(node.operand_b)};"

    def gen_Parameter(self, node: Parameter):
        return f"{self.gen(node.paramType)} {self.gen(node.var)}"

    def gen_ParameterLst(self, node: ParameterLst):
        return ", ".join(self.gen(param) for param in node.lst)

    def gen_FunctionDeclaration(self, node: FunctionDeclaration):
        assert not self.state_in_function_declaration, "Cannot declare function inside of a function"
        function_declaration = f"{self.gen(node.returnType)} {self.gen(node.name)}({self.gen(node.lst)})"
        self.function_declarations.append(function_declaration)
        self.state_in_function_declaration = True
        self.function_definitions.append((
            function_declaration + " {",
            self.gen(node.body),
            "} " f"/* End of {self.gen(node.name)} */",
        ))
        self.state_in_function_declaration = False
        return None

    def gen_IfStmt(self, node: IfStmt):
        return (
            f"if ({self.gen(node.ifCond)})" " {",
            self.gen(node.body),
            "}",
        )

    def gen_ElifStmt(self, node: ElifStmt):
        return (
            f"else if ({self.gen(node.elifCond)})" " {",
            self.gen(node.body),
            "}",
        )

    def gen_ElseStmt(self, node: ElseStmt):
        return (
            "else {",
            self.gen(node.body),
            "}",
        )

    def gen_WhileStmt(self, node: WhileStmt):
        return (
            f"while ({self.gen(node.cond)})" " {",
            self.gen(node.body),
            "}",
        )

    def gen_Assignment(self,node:Assignment):
        if type(node.val) != Id:
            return f"{self.gen(node.id)} = {node.val};"
        return f"{self.gen(node.id)} = {self.gen(node.val)};"

    def gen_ReturnStatement(self, node: ReturnStatement):
        assert self.state_in_function_declaration, "Cannot have return statement outside of a function declaration"
        return f"return {self.gen(node.value)}"

