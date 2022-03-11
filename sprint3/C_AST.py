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
    ifCond: Expression
    body: Block

@dataclass
class ElifStmt:
    elifCond: Expression
    body: Block

@dataclass
class ElseStmt:
    body: Block

@dataclass
class WhileStmt:
    cond: Expression
    body: Block

@dataclass
class Expression:
    value: Union[BinaryOperation, UnaryOperation, Id]

@dataclass
class Block:
    lst: List[Union[FunctionDeclaration, ReturnStmt, FunctionCall, ForLoopRange, ForLoopList, WhileStmt, \
                    IfStmt, ElifStmt, ElseStmt, BinaryOperation, UnaryOperation]]


class CCodeGenerator:
    def generate_code(self, root, indent=0):
        structure = self.gen(root)
        formatted = self.generate_code_formatter(structure)
        return formatted

    def generate_code_formatter(self, structure, indent=0):
        result = ""
        for line in structure:
            if isinstance(line, tuple):
                code = self.generate_code_formatter(line, indent)
            elif isinstance(line, list):
                code = self.generate_code_formatter(line, indent + 1)
            else:
                code = "    " * indent + line + "\n"
            result += code
        return result

    def code_template(self, generated_code):
        return """
        #include <stdio.h>
        #include <bool.h>

        typedef int_t   long long;
        typedef float_t double;
        typedef bool_t  bool;

        /* Function declarations */

        /* End of function declarations */

        /* Function definitions */

        /* End of function definitions */

        /* Main */
        int main() {

            /**********/

            return 0;
        }
        /* End of main */
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
        function_definition = f"{self.gen(node.returnType)} {self.gen(node.name)}({self.gen(node.lst)})"
        return (
            function_definition + " {",
            self.gen(node.body),
            "} " f"/* End of {self.gen(node.name)} */",
        )

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
