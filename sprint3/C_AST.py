from __future__ import annotations
from typing import Union, List, Literal
from dataclasses import dataclass


@dataclass
class Type:
    value: Union[Literal['str_t', 'int_t', 'float_t', 'bool_t', 'none_t'],NonPrimitiveType]

    def __init__(self, value):
        if value.__class__.__name__ != 'NonPrimitiveType':
            assert value in ['str_t', 'int_t', 'float_t', 'bool_t', 'none_t']
        self.value = value



@dataclass
class NonPrimitiveType:
    type: Union['list', 'tuple']
    value: Type


@dataclass
class Id:
    name: str
    def __init__(self, name):
        assert isinstance(name, str), f"Got {name=}"
        self.name = name


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
    indexVar : Id
    length : any
    Lst: Expression
    body: Block


@dataclass
class Expression:
    value: Union[BinaryOperation, UnaryOperation, Id]


@dataclass
class ArgumentLst:
    lst: Union[List[Expression], List[Id], None]


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
    id: Id
    val: any


@dataclass
class String:
    val: str
    len: int


@dataclass
class ReturnStatement:
    value: Id


@dataclass
class PrimitiveLiteral:
    id: Id
    type: Type
    value: any


@dataclass
class LstAdd:
    obj: Id
    value: any
    type: Type
    idx: Union[str, int]

@dataclass
class NonPrimitiveIndex:
    result: Id
    obj: Id
    type: Type
    idx: Id


@dataclass
class NonPrimitiveLiteral:
    head: Id
    type: NonPrimitiveType
    value: List[Union[Id, PrimitiveLiteral]]

class CCodeGenerator:
    function_declarations = []
    function_definitions = []
    state_in_function_declaration = False
    array_cleanup = []

    def generate_code(self, root):
        structure = self.gen(root)
        formatted = self.generate_code_formatter(structure)
        declarations_str, definitions_str = self.generate_function_code()
        clean_up = self.generate_clean_up()
        return self.code_template(declarations_str, definitions_str, formatted, clean_up)

    def generate_function_code(self):
        declarations_str = ";\n".join(self.function_declarations)
        if len(declarations_str) != 0: declarations_str += ';'
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

    def generate_clean_up(self):
        clean_up = ''
        for array in self.array_cleanup:
            clean_up += f"list_free({array});\n"
        return clean_up

    def code_template(self, function_declarations, function_definitions, main_code, clean_up):
        if len(function_declarations) == 0:
            function_code = ""
        else:
            function_code = f"""
/***** Function declarations *****/
{function_declarations}
/***** End of function declarations *****/

/***** Function definitions *****/
{function_definitions}
/***** End of function definitions *****/
        """.strip() + '\n'

        return f"""
#include "../starter.c"

{function_code}
int main() {{
/***** Main *****/
{main_code}
/***** End of main *****/

/***** Memory clean up *****/
{clean_up}
/***** End of Memory clean up *****/

    return 0;
}}
        """.strip() + '\n'

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
        type_t = self.gen(node.type)
        name = self.gen(node.id)
        return f"{type_t} {name};"

    def gen_Type(self, node: Type):
        if node.value.__class__.__name__ != "NonPrimitiveType":
            assert node.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t'], f"{node}"
            return node.value
        else:
            assert node.value.type in ['list', 'tuple']
            return "list_t *"

    def gen_UnaryOperation(self, node: UnaryOperation):
        return f"{self.gen(node.left)} = {node.operator} {self.gen(node.operand)};"

    def gen_BinaryOperation(self, node: BinaryOperation):
        # TODO: adding string. Need to check type of the operands, use helper function
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

    def gen_FunctionCall(self, node: FunctionCall):
        arg_string = ", ".join(i for i in node.lst)
        return node.name + "(" + arg_string + ")"

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
    def gen_ForLoopRange(self, node: ForLoopRange):
        assign_string = self.gen_Assignment(Assignment(id=node.var, val=node.rangeVal.start))
        comp_string = f"{node.var.name} < {node.rangeVal.stop};"
        step_string = f"{node.var.name} += {node.rangeVal.step}"

        return (
               "for (" + assign_string + " " + comp_string + " " + step_string + "){",
               self.gen(node.body),
               "}",
        )

    def gen_ForLoopList(self, node: ForLoopList):

        assign_string = f"{node.indexVar} = 0;"
        comp_string = f"{node.indexVar} < {node.length};"
        step_string = f"{node.indexVar} += 1"

        #index_string = f"list_get(int_v, {node.Lst}, {node.indexVar})"
        #assign_node = Assignment(id=node.var, val=index_string)
        #node.body.lst = [assign_node] + node.body.lst

        return (
               "for (" + assign_string + " " + comp_string + " " + step_string + "){",
               [f"{node.var} = list_get(int_v, {node.Lst}, {node.indexVar});"],
               self.gen(node.body),
               "}",
        )

    def gen_Assignment(self, node: Assignment):
        if isinstance(node.val, (Id, FunctionCall, String)):
            return f"{self.gen(node.id)} = {self.gen(node.val)};"
        elif isinstance(node.val, bool):
            return f"{self.gen(node.id)} = {str(node.val).lower()};"
        elif node.val == "none-placeholder":
            return f"{self.gen(node.id)} = NONE_LITERAL;"
        else:
            return f"{self.gen(node.id)} = {node.val};"

    def gen_String(self, node: String):
        # Using json.dumps to do string escape
        import json
        return json.dumps(node.val)
        # return "{" + ", ".join("\'" + i + "\'" for i in node.val) + ", \' \\0\'}"

    def gen_ReturnStatement(self, node: ReturnStatement):
        assert self.state_in_function_declaration, "Cannot have return statement outside of a function declaration"
        return f"return {self.gen(node.value)};"

    def gen_LstAdd(self, node: LstAdd):
        obj = self.gen(node.obj)
        type_t = self.gen(node.type)
        type_t = type_t[:-1]+"v"
        value = self.gen(node.value)
        if node.idx == 'end':
            return f"list_add({type_t},{obj},{value});\n"

    def gen_NonPrimitiveIndex(self, node: NonPrimitiveIndex):
        return f"{self.gen(node.result)}=list_get({self.gen(node.type)},{self.gen(node.obj)},{self.gen(node.idx)})"

    def gen_NonPrimitiveLiteral(self, node: NonPrimitiveLiteral):
        head = self.gen(node.head)
        init = f"list_t * {head} = list_init({len(node.value)});\n"
        self.array_cleanup.append(head)
        val_type = self.convert_v_type(node.type)
        for item in node.value:
            init += f"list_init_add({val_type},{self.gen(node.head)},{self.gen(item)});\n"
        return init

    def convert_v_type(self,node: Type):
        if not isinstance(node.value, NonPrimitiveType):
            assert node.value.value.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t']
            return node.value.value.value.replace('_t', '_v')
        else:
            return "list_v"
