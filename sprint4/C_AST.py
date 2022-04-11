from __future__ import annotations
from typing import Union, List, Literal
from dataclasses import dataclass
from value_table import ValueTable
import json


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

@dataclass
class NonPrimitiveSlicing:
    result_reg: Id
    obj: Id
    start: Union[Id,None]
    end: Union[Id,None]
    type: NonPrimitiveType

class CCodeGenerator:
    def __init__(self):
        self.function_declarations = []
        self.function_definitions = []
        self.state_in_function_declaration = False

        self.temp_list_dict = {}
        self.generated_code = []
        self.decl_scope = [[]]
        self.list_type_dict = {}
        self.list_decl_dict = []
        self.list_len_dict = {}
        self.converted_str_lst = {}

        self.is_inloop = False
        self.pre_run = False
        self.eval_mode = True  # Optimization flag
        self.variants = []
        self.has_if_head = False
        self.ignore_if = False
        self.var_table = ValueTable()

    def generate_code(self, root):
        structure = self.gen(root)
        formatted = self.generate_code_formatter(structure)
        declarations_str, definitions_str = self.generate_function_code()
        return self.code_template(declarations_str, definitions_str, formatted)

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
        for tmp in self.temp_list_dict.keys():
            var = self.temp_list_dict[tmp]
            if var != None:
                result = result.replace(tmp, var)
        return result

    def code_template(self, function_declarations, function_definitions, main_code):
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

    str_clean_up();
    list_clean_up();

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
        result = []
        self.decl_scope.append([])
        for x in node.lst:
            code = self.gen(x)
            if code:
                if type(code) == str and code.find(";") != len(code[0]) -1:
                    code_group = code.split(';')
                    for c in code_group:
                        if c:
                            result.append(c+";")
                else:
                    result.append(code)
        self.decl_scope.pop()
        return result

    def gen_Expression(self, node: Expression):
        return self.gen(node.value)

    def gen_Id(self, node: Id):
        return node.name

    def gen_Declaration(self, node: Declaration):
        type_t = self.gen(node.type)
        name = self.gen(node.id)
        if type_t == "list_t *":
            self.list_type_dict[name] = type_t
            return None
        if self.var_table.is_temp(name):
            self.var_table.set_temp(name,None)
            return None
        for scope in self.decl_scope:
            if name in scope:
                return None
        self.decl_scope[-1].append(name)
        return f"{type_t} {name};"

    def gen_Type(self, node: Type):
        if node.value.__class__.__name__ != "NonPrimitiveType":
            assert node.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t'], f"{node}"
            return node.value
        else:
            assert node.value.type in ['list', 'tuple']
            return "list_t *"

    def gen_UnaryOperation(self, node: UnaryOperation):
        left = self.gen(node.left)
        op = self.gen(node.operand)
        is_temp = self.var_table.is_temp(left)
        if self.eval_mode:
            if not self.pre_run:
                if is_temp:
                    self.var_table.set_temp(left,f'{node.operator} {op}')
                else:
                    value = self._eval(node)
                    self.var_table.set_variable(left,value)
                    return f"{left} = {value};"
            elif not is_temp and left not in self.variants:
                self.variants.append(left)
        else:
            if is_temp:
                self.var_table.set_temp(left,f'{node.operator} {op}')
            else:
                return f"{left} = {node.operator} {op};"


    #helper function for binary op
    def check_both_numbers(self, a, b, operator):
        if (isinstance(a, int) or isinstance(a, float)) and (isinstance(b, int) or isinstance(b, float)) :
            if operator == '+':
                return a + b
            if operator == '*':
                return a * b
            if operator == '-':
                return a - b
            if operator == '/':
                assert b != 0, "Cannot Divide by zero"
                return a/b
        return None

    def gen_BinaryOperation(self, node: BinaryOperation):
        # TODO: adding string. Need to check type of the operands, use helper function
        left = self.gen(node.left)
        op_a = self.var_table.lookup(self.gen(node.operand_a))
        op_b = self.var_table.lookup(self.gen(node.operand_b))
        is_temp = self.var_table.is_temp(left)
        if self.eval_mode:
            if not self.pre_run:
                if is_temp:
                    op_a = self._eval(node.operand_a)
                    op_b = self._eval(node.operand_b)
                    if type(op_a) == type(op_b) == str and (('"' in op_a or 'input_str()' == op_a) and \
                                                            ('"' in op_b or 'input_str()' == op_b)):
                        self.var_table.set_temp(left,f'str_concat({op_a},{op_b})')
                        return
                    self.var_table.set_temp(left, f'{op_a} {node.operator} {op_b}')
                else:
                    value = self._eval(node)
                    self.var_table.set_variable(left,value)
                    return f"{left} = {value};"
            elif not is_temp and left not in self.variants:
                self.variants.append(left)
        else:
            value = f"{op_a} {node.operator} {op_b}"
            if is_temp:
                self.var_table.set_temp(left,value)
            else:
                return f"{left} = {value};"

    def gen_Parameter(self, node: Parameter):
        var = self.gen(node.var)
        self.var_table.set_variable(var, var)
        return f"{self.gen(node.paramType)} {var}"

    def gen_ParameterLst(self, node: ParameterLst):
        return ", ".join(self.gen(param) for param in node.lst)

    def gen_FunctionDeclaration(self, node: FunctionDeclaration):
        assert not self.state_in_function_declaration, "Cannot declare function inside of a function"
        self.var_table.push_scope()
        function_declaration = f"{self.gen(node.returnType)} {self.gen(node.name)}({self.gen(node.lst)})"
        self.function_declarations.append(function_declaration)
        self.state_in_function_declaration = True
        self.function_definitions.append((
            function_declaration + " {",
            self.gen(node.body),
            "} " f"/* End of {self.gen(node.name)} */",
        ))
        self.var_table.pop_scope()
        self.state_in_function_declaration = False
        return None

    def gen_FunctionCall(self, node: FunctionCall):
        arg_list = []
        for i in node.lst:
            arg_list.append(self.var_table.lookup(i))
        arg_string = ", ".join(str(i) for i in arg_list)
        return node.name + "(" + arg_string + ")"

    def gen_IfStmt(self, node: IfStmt):
        self.var_table.push_scope()
        body = self.gen(node.body)
        variables = self.var_table.pop_scope()
        if self.eval_mode:
            eval_cond = self._eval(node.ifCond)
            if str(eval_cond) == 'True' or eval_cond == "true":
                self.has_if_head = True
                self.ignore_if = True
                if not body:
                    return None
                self.var_table.reset_variables(variables.keys())
                return "".join(body)
            elif str(eval_cond) == 'False' or eval_cond == "false" or eval_cond == "NONE_LITERAL":
                self.has_if_head = False
                self.ignore_if = False
                return None
        else:
            eval_cond = self.var_table.lookup(self.gen(node.ifCond))
        self.var_table.reset_variables(variables.keys())
        return (
            f"if ({eval_cond})" " {",
            self.gen(node.body),
            "}",
        )

    def gen_ElifStmt(self, node: ElifStmt):
        if self.eval_mode:
            if self.ignore_if:
                return None
            eval_cond = self._eval(node.elifCond)
            self.var_table.push_scope()
            body = self.gen(node.body)
            variables = self.var_table.pop_scope()
            if not body:
                return None
            if str(eval_cond) == 'True' or eval_cond == "true":
                self.var_table.reset_variables(variables.keys())
                if self.has_if_head:
                    return (
                        f"else if ({eval_cond})" " {",
                        body,
                        "}",
                    )
                else:
                    self.has_if_head = True
                    self.ignore_if = True
                    return "".join(body)
            elif str(eval_cond) == 'False' or eval_cond == "false" or eval_cond == "NONE_LITERAL":
                return None
        else:
            eval_cond = self.var_table.lookup(self.gen(node.elifCond))
        self.var_table.reset_variables(variables.keys())
        return (
            f"else if ({eval_cond})" " {",
            self.gen(node.body),
            "}",
        )

    def gen_ElseStmt(self, node: ElseStmt):
        self.var_table.push_scope()
        body = self.gen(node.body)
        variables = self.var_table.pop_scope()
        if self.eval_mode:
            if self.ignore_if or not body:
                return None
            if not self.has_if_head:
                self.var_table.reset_variables(variables.keys())
                return "".join(body)
        self.var_table.reset_variables(variables.keys())
        return (
            "else {",
            self.gen(node.body),
            "}",
        )

    def gen_WhileStmt(self, node: WhileStmt):
        cond = self.var_table.lookup(self.gen(node.cond))
        if self.eval_mode:
            if not self.is_inloop:
                eval_cond = self._eval(node.cond)
                if str(eval_cond) == 'False' or eval_cond == "false":
                    return None
                self.is_inloop = True
                self.pre_run = True
                self.gen(node.body)
                self.pre_run = False
                self.var_table.push_scope()
                body = self.gen(node.body)
                self.var_table.pop_scope()
                if not body:
                    return None
                result = (f"while ({cond})" " {",
                      body,
                      "}",)
                self.var_table.reset_variables(self.variants)
                self.variants = []
                self.is_inloop = False
                return result
            elif self.pre_run:
                self.gen(node.body)
                return None
            else:
                eval_cond = self._eval(node.cond)
                if str(eval_cond) == 'False' or eval_cond == "false":
                    return None
        return (
            f"while ({cond})" " {",
            self.gen(node.body),
            "}",
        )
    def gen_ForLoopRange(self, node: ForLoopRange):

        stop_val = node.rangeVal.stop
        step_val = node.rangeVal.step
        if self.var_table.is_temp(stop_val):
            stop_val = self.var_table.lookup(stop_val)
        if self.var_table.is_temp(step_val):
            step_val = self.var_table.lookup(step_val)
        self.var_table.push_scope()
        assign_string = self.gen_Assignment(Assignment(id=node.var, val=node.rangeVal.start))
        comp_string = f"{node.var.name} < {stop_val};"
        step_string = f"{node.var.name} += {step_val}"
        if self.eval_mode:
            ranges = self._eval(node.rangeVal)
            print(ranges)
            if type(ranges[2]) == int and type(ranges[0]) == int and  ranges[0] >= ranges[2]:
                return None
            if not self.is_inloop:
                self.is_inloop = True
                self.pre_run = True
                self.gen(node.body)
                self.pre_run = False
                body = self.gen(node.body)
                self.var_table.pop_scope()
                if not body:
                    return None
                result = (
                    "for (" + assign_string + " " + comp_string + " " + step_string + "){",
                    body,
                    "}",
                )
                self.var_table.reset_variables(self.variants)
                self.variants = []
                self.is_inloop = False
                return result
            elif self.pre_run:
                self.gen(node.body)
                self.var_table.pop_scope()
                return None
        self.var_table.pop_scope()
        return (
               "for (" + assign_string + " " + comp_string + " " + step_string + "){",
               self.gen(node.body),
               "}",
        )

    def gen_ForLoopList(self, node: ForLoopList):
        idx = self.var_table.lookup(node.indexVar.name)
        assign_var = self.gen(node.var)
        lst = self.var_table.lookup(node.Lst.name)
        assign_string = f"int_t i = 0;"
        comp_string = f"i < {node.length};"
        step_string = f"i += {idx}"
        self.var_table.push_scope()
        self.var_table.set_variable(assign_var, assign_var)
        self.var_table.set_variable("i" ,"i")
        if self.eval_mode:
            if not self.is_inloop:
                self.is_inloop = True
                self.pre_run = True
                self.gen(node.body)
                self.pre_run = False
                body = self.gen(node.body)
                self.var_table.pop_scope()
                if not body:
                    return None
                result = (
                    "for (" + assign_string + " " + comp_string + " " + step_string + "){",
                    [f"{assign_var} = list_get(int_v, {lst}, i);"],
                    body,
                    "}",
                )
                self.var_table.reset_variables(self.variants)
                self.variants = []
                self.is_inloop = False
                return result
            elif self.pre_run:
                self.gen(node.body)
                self.var_table[-1].pop(assign_var)
                self.var_table.pop_scope()
                return None
        return (
               "for (" + assign_string + " " + comp_string + " " + step_string + ") {",
               [f"{assign_var} = list_get(int_v, {lst}, i);"],
               self.gen(node.body),
               "}",
        )

    def gen_Assignment(self, node: Assignment):
        assign_var = self.gen(node.id)
        temp_var = False
        print(node)
        if self.var_table.is_temp(assign_var):
            temp_var = True
        if not self.pre_run:
            assign_value = node.val
            print(assign_value)
            # value pre-processing and early termination
            if isinstance(node.val, bool):
                assign_value = str(node.val).lower()
            elif isinstance(node.val, (Id, FunctionCall, String)):
                assign_value = self.gen(node.val)
                if isinstance(node.val, String):
                    self.converted_str_lst[assign_var] = assign_value
                elif temp_var and isinstance(node.val, FunctionCall) and node.val.name[:6] == "print_":
                    return f"{assign_value};"
            elif isinstance(assign_value,str) and self.var_table.is_temp(assign_value):
                assign_value = self.var_table.lookup_temp(assign_value)
            # update and lookup value table
            if temp_var:
                if node.val == "none-placeholder":
                    self.var_table.set_temp(assign_var, "NONE_LITERAL")
                else:
                    self.var_table.set_temp(assign_var, assign_value)
                return None
            elif assign_value in self.temp_list_dict.keys():
                self.temp_list_dict[assign_value] = assign_var
                self.list_len_dict[assign_var] = self.list_len_dict[assign_value]
                return None
            # handle list slicing
            if assign_value and assign_var not in self.temp_list_dict.values() and assign_var not in self.list_decl_dict and \
                    (assign_value in self.temp_list_dict.values() or assign_value in self.list_decl_dict or
                     (type(assign_value) == str and "list_slice" in assign_value)):
                self.list_decl_dict.append(assign_var)
                type_t = self.list_type_dict[assign_var]
                if "list_slice" in assign_value:
                    params = assign_value.split("(")[1].split(")")[0].split(",")
                    end = params[2]
                    start = params[1]
                    if isinstance(end,str):
                        end = self.var_table.lookup(end)
                    if isinstance(start,str):
                        start = self.var_table.lookup(start)
                    self.list_len_dict[assign_var] = eval(f"{end}-{start}")
                else:
                    self.list_len_dict[assign_var] = self.list_len_dict[assign_value]
                return "".join([f"{type_t} {assign_var};", f"{assign_var} = {assign_value}"])
            result = f"{assign_var} = {assign_value}"
        else:
            if not temp_var:
                self.variants.append(assign_var)
            return None
        # optimization
        if self.eval_mode and assign_var not in self.variants:
            if isinstance(node.val, FunctionCall):
                self.var_table.set_variable(assign_var, assign_var)
            elif not self.var_table.is_temp(node.val):
                value = self._eval(node)
                self.var_table.set_variable(assign_var,value)
                result = f"{assign_var} = {value};"
            else:
                self.var_table.set_variable(assign_var, assign_value)
        return result

    def gen_String(self, node: String):
        # Using json.dumps to do string escape
        import json
        return json.dumps(node.val)

    def gen_ReturnStatement(self, node: ReturnStatement):
        assert self.state_in_function_declaration, "Cannot have return statement outside of a function declaration"
        value = self.var_table.lookup(self.gen(node.value))
        return f"return {value};"

    def gen_LstAdd(self, node: LstAdd):
        obj = self.gen(node.obj)
        type_t = self.gen(node.type)
        type_t = type_t[:-1] + "v"
        value = self.var_table.lookup(self.gen(node.value))
        if node.idx == 'end':
            return f"list_add({type_t}, {obj}, {value});"

    def gen_NonPrimitiveIndex(self, node: NonPrimitiveIndex):
        idx_reg = self.gen(node.result)
        idx = self.gen(node.idx)
        type_v = self.convert_v_type(node.type)
        if idx in self.var_table.temp_dict:
            idx = self.var_table.lookup(idx)
        if idx_reg[0] == "_":
            self.var_table.set_temp(idx_reg,f"list_get({type_v},{self.gen(node.obj)},{idx})")
        else:
            return f"{self.gen(node.result)} = list_get({type_v},{self.gen(node.obj)},{idx})"

    def gen_NonPrimitiveLiteral(self, node: NonPrimitiveLiteral):
        head = self.gen(node.head)
        if isinstance(head, str) and head[0] == '_':
            self.temp_list_dict[head] = None
        init = [f"list_t * {head} = list_init({len(node.value)});"]
        val_type = self.convert_v_type(node.type)
        for item in node.value:
            value = self.var_table.lookup(self.gen(item))
            init.append(f"list_init_add({val_type},{self.gen(node.head)},{value});")
        self.list_len_dict[head] = len(node.value)
        return "".join(init)

    def gen_NonPrimitiveSlicing(self, node: NonPrimitiveSlicing):
        obj = self.gen(node.obj)
        result_reg = self.gen(node.result_reg)
        if node.start:
            start = self.var_table.lookup(self.gen(node.start))
        else:
            start = 0
        if node.end:
            end = self.var_table.lookup(self.gen(node.end))
        else:
            end = self.list_len_dict[obj]
        result = f"list_slice({obj},{start},{end})"
        self.var_table.set_temp(result_reg,result)
        return None

    def convert_v_type(self,node: Type):
        if isinstance(node.value, str):
            assert node.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t']
            return node.value.replace('_t', '_v')
        elif not isinstance(node.value, NonPrimitiveType):
            assert node.value.value.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t']
            return node.value.value.value.replace('_t', '_v')
        elif not isinstance(node.value, Type):
            assert node.value.value.value in ['str_t', 'int_t', 'float_t', 'bool_t', 'str_t', 'none_t']
            return node.value.value.value.replace('_t', '_v')
        else:
            return 'list_v'

    def _eval(self, node):
        method = 'eval_' + node.__class__.__name__
        try:
            return getattr(self, method)(node)
        except AttributeError:
            return node

    def eval_BinaryOperation(self, node: BinaryOperation):
        left = self._eval(node.operand_a)
        right = self._eval(node.operand_b)
        if self.gen(node.left) not in self.variants and isinstance(left, (bool, int, float))\
                and isinstance(right, (bool, int, float)):
            temp_dict = self.var_table.var_stack[-1].copy()
            for var in self.variants:
                temp_dict.pop(var,None)
            return eval(f"{left} {node.operator} {right}",temp_dict)
        return f"{left} {node.operator} {right}"

    def eval_UnaryOperation(self, node: UnaryOperation):
        operand = self._eval(node.operand)
        if self.gen(node.left) not in self.variants and isinstance(operand, (bool, int, float)):
            temp_dict = self.var_table.var_stack[-1].copy()
            for var in self.variants:
                temp_dict.pop(var,None)
            return eval(f"{node.operator} {operand}",temp_dict)
        return f"{node.operator} {operand}"

    def eval_Id(self, node: Id):
        if node.name[0] == "_":
            expr = self.var_table.lookup_temp(node.name)
            try:
                if node.name in self.converted_str_lst:
                    return self.converted_str_lst[node.name]
                temp_dict = self.var_table.var_stack[-1].copy()
                for var in self.variants:
                    temp_dict.pop(var,None)
                result = eval(f"{expr}",temp_dict)
                if type(result) == str:
                    import json
                    result = json.dumps(result)
                    print("result :",result, " name: ",node.name)
                    self.converted_str_lst[node.name] = result
                    return result
            except:
                result = expr
            return result
        else:
            if node.name not in self.variants and node.name in self.var_dict:
                return self.var_dict[node.name]
        return node.name

    def eval_PrimitiveLiteral(self,node:PrimitiveLiteral):
        return node.value

    def eval_FunctionCall(self,node:FunctionCall):
        return self.gen(node)

    def eval_Assignment(self,node:Assignment):
        expr = self.var_table.lookup(node.val)
        name = self.gen(node.id)
        try:
            if node.val in self.converted_str_lst:
                result = self.converted_str_lst[node.val]
                self.converted_str_lst[name] = result
                return result
            temp_dict = self.var_table.var_stack[-1].copy()
            for var in self.variants:
                temp_dict.pop(var,None)
            result = eval(f"{expr}", temp_dict)
            if type(result) == str:
                result = json.dumps(result)
                self.converted_str_lst[name] = result
                return json.dumps(result)
        except:
            result = expr
        print("result ",result)
        return result

    def eval_RangeValues(self,node:RangeValues):
        start = self.var_table.lookup(node.start)
        step = self.var_table.lookup(node.step)
        stop = self.var_table.lookup(node.stop)
        return [eval(f"{start}",self.var_table.var_stack[-1]),eval(f"{step}",self.var_table.var_stack[-1]),eval(f"{stop}",self.var_table.var_stack[-1])]
