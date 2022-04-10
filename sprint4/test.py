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

def read(filename):
    with open(filename) as f:
        return f.read()

def write(filename, s):
    with open(filename, 'w+') as f:
        f.write(s)

def ir_to_str(ir):
    return '\n'.join(repr(ir_line) for ir_line in ir) + '\n'

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

def compiler(input_file, c, executable, opt_on=False, ir_tmp=None):
    input_str = read(input_file)
    input_str = remove_comments(input_str)

    for index, s in enumerate(input_str.split('\n')):
        if s.startswith(' ') and len(s.strip()) != 0:
            raise Exception(f"Leading spaces detected at line {index}\nIndentation using spaces are not supported. Did you mean to use tabs?")

    try:
        blocks = parse_from_code_to_blocks(input_str)
    except Exception as e:
        raise Exception("Parser Error: " + e.args[0])
    try:
        st = type_check_from_blocks_to_st(blocks)
    except Exception as e:
        raise Exception("Type Checker Error: " + e.args[0])

    try:
        ir = from_blocks_to_ir(blocks)
    except Exception as e:
        raise Exception("IR Translation Error: ", e.args[0])
    if ir_tmp: write(ir_tmp, ir_to_str(ir))
    try:
        code = from_ir_st_to_c(ir, st, opt_on=opt_on)
    except Exception as e:
        breakpoint()
        raise Exception("Unable to generate target: ", e.args[0])

    write(c, code)

    try:
        check_if_code_compiles(c, executable)
    except Exception as e:
        raise Exception("Unable to compile output: ", e)


def check_if_code_compiles(filename, output):
    import subprocess
    proc = subprocess.run(f'gcc {filename} -o {output}', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    assert proc.returncode == 0, f"gcc return code was {proc.returncode}\n{proc.stderr}"

def execute_program(filename, input=""):
    import subprocess
    proc = subprocess.run(f'{filename}', shell=True, stdout=subprocess.PIPE, universal_newlines=True, input=input)
    return (proc.returncode, proc.stdout)


test_names_compile = [f.replace('.py', '') for f in os.listdir(f'./tests/error/') if f.endswith('.py')]
@pytest.mark.parametrize("test_name", test_names_compile)
def test_compile(test_name):
    d= './tests/compile'
    compiler(
        input_file=f'{d}/{test_name}.py',
        c=f'{d}/{test_name}.c',
        executable=f'{d}/{test_name}',
        opt_on=False,
        ir_tmp=f'{d}/{test_name}_IR.txt',
    )


@pytest.mark.parametrize("test_name", test_names_compile)
def test_error(test_name):
    d = './tests/error'

    first_line, second_line = read(f'{d}/{test_name}.py').split('\n')[:2]
    assert first_line.startswith('#'), "Expect first line to be a comment for this test"
    assert second_line.startswith('#'), "Expect second line to be a comment for this test"
    expected_words = second_line.replace('#', '').strip().split()

    if '[RUNTIME]' in first_line:
        try:
            compiler(
                input_file=f'{d}/{test_name}.py',
                c=f'{d}/{test_name}.c',
                executable=f'{d}/{test_name}',
                opt_on='[OPT_ON]' in first_line,
                ir_tmp=f'{d}/{test_name}_IR.txt',
            )
        except Exception as e:
            raise Exception(f"Does not expect error at this stage, got: {e}")

        code, stdout = execute_program(f'{d}/{test_name}', input='')
        assert code == 1, f"Expected runtime error, got: {code=} {stdout=}"

        for word in expected_words:
            first_line = str(stdout).split('\n')[0]
            assert word in first_line, f"Expect error message to contain {word}\n\nGot Error:{str(stdout)}"
        if len(expected_words) == 0:
            raise Exception("Got stdout: " + str(stdout))


    else:
        try:
            compiler(
                input_file=f'{d}/{test_name}.py',
                c=f'{d}/{test_name}.c',
                executable=f'{d}/{test_name}',
                opt_on='[OPT_ON]' in first_line,
                ir_tmp=f'{d}/{test_name}_IR.txt',
            )
        except Exception as e:
            # Expect every word in second line to appear in the error message
            for word in expected_words:
                first_line = str(e).split('\n')[0]
                assert word in first_line, f"Expect error message to contain {word}\n\nGot Error:{str(e)}"
            if len(expected_words) == 0:
                raise Exception("Got error: " + str(e))
        else:
            raise Exception("Expected an error to be thrown")
