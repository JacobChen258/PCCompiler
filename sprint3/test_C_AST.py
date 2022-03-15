from tty import CC
import pytest
from C_AST import *

case1 = Block([
    Declaration(Id('var1'), Type('int_t')),
    BinaryOperation(Id('var1'), '+', operand_a=Id('var1'), operand_b=Id('var2')),
])

case2 = Block([
    Declaration(Id('var1'), Type('int_t')),
    BinaryOperation(Id('var1'), '+', operand_a=Id('var1'), operand_b=Id('var1')),
    IfStmt(ifCond=Id('var1'), body=Block([
        BinaryOperation(Id('var1'), '+', operand_a=Id('var1'), operand_b=Id('var2')),
        IfStmt(ifCond=Id('var1'), body=Block([
            BinaryOperation(Id('var1'), '+', operand_a=Id('var1'), operand_b=Id('var2')),
        ])),
    ])),
])

case3 = Block([
    FunctionDeclaration(
        name=Id("func1"),
        lst=ParameterLst([
            Parameter(Type('int_t'), Id('arg1')),
            Parameter(Type('int_t'), Id('arg2')),
        ]),
        body=Block([

        ]),
        returnType=Type('int_t'),
    )
])

generator = CCodeGenerator()
print(generator.generate_code(case3))

# cases = [
#     [case1, ""]
# ]

# @pytest.mark.parametrize("input_data, expected", cases)
# def test_main_c_ast(lexer, input_data, expected):
#     pass
    # result = lexer.test(input_data)
    # assert len(result) == 1, f"Expect 1, got {len(result)}: {[x.type for x in result]}"
    # assert result[0].type == expected, f"Expect {expected}, got {result[0].type}"
