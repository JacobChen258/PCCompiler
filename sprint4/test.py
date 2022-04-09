import pytest
import os
import difflib
from yacc import pythonParser
from type_checker import TypeChecker, SymbolTable
from ir_gen import IRGen
from C_AST_gen import CASTGenerator
from C_AST import CCodeGenerator

def parser():
    p = pythonParser()
    p.build()
    return p


def remove_comments(input_str):
    # A dirty but quick way to implement comments
    return '\n'.join(line for line in input_str.split('\n') if not line.startswith('#'))

def parse_from_code_to_blocks(input_str):
    return parser().parse(input_str)

def type_check_from_blocks_to_st(blocks):
    tc = TypeChecker()
    st = SymbolTable()
    for block in blocks:
        tc.typecheck(block, st)
    return st

def from_blocks_to_ir(blocks):
    ir_generator = IRGen()
    ir_generator.generate_IR(blocks)
    return ir_generator.IR

def from_ir_st_to_c(ir, st, opt_on):
    c_ast_generator = CASTGenerator()
    c_ast = c_ast_generator.generate_AST(ir, st)
    c_code_generator = CCodeGenerator()
    c_code_generator.eval_mode = opt_on
    return c_code_generator.generate_code(c_ast)

def check_if_code_compiles(filename, output):
    import subprocess
    proc = subprocess.run(f'gcc {filename} -o {output}', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    print("----- stderr -----")
    print(proc.stderr)
    print("----- stdout -----")
    print(proc.stdout)
    assert proc.returncode == 0, f"gcc return code was {proc.returncode}"


test_names_compile = [f.replace('.py', '') for f in os.listdir(f'./tests/compile/') if f.endswith('.py')]

@pytest.mark.parametrize("test_name", test_names_compile)
def test_compile(test_name):

    with open(f'./tests/compile/{test_name}.py', 'r') as f:
        input_str = f.read()

    input_str = remove_comments(input_str)

    blocks = parse_from_code_to_blocks(input_str)
    st = type_check_from_blocks_to_st(blocks)
    ir = from_blocks_to_ir(blocks)

    with open(f'./tests/compile/{test_name}_IR.txt', 'w+') as f:
        f.write('\n'.join(repr(ir_line) for ir_line in ir) + '\n')

    code = from_ir_st_to_c(ir, st, opt_on=False)

    with open(f'./tests/compile/{test_name}.c', 'w+') as f:
        f.write(code)

    check_if_code_compiles(f'./tests/compile/{test_name}.c', f'./tests/compile/{test_name}')


def format_parser_output(o):
    import json
    return json.dumps(o, default=lambda x: { 'NODE': x.__class__.__name__, **x.__dict__}, indent=2)
