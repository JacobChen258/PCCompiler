import argparse
import pytest
import os
import difflib
from yacc import pythonParser

@pytest.fixture
def parser():
    p = pythonParser()
    p.build()
    return p

files = os.listdir('./tests/')
test_names = [f.replace('_input.py', '') for f in files if f.endswith('_input.py')]


def format_parser_output(o):
    import json
    return json.dumps(o, default=lambda x: { 'NODE': x.__class__.__name__, **x.__dict__}, indent=2)


@pytest.mark.parametrize("test_name", test_names)
def test_simple_token(parser, test_name):
    with open(f'./tests/{test_name}_input.py', 'r') as f:
        input_str = f.read()
    try:
        with open(f'./tests/{test_name}_output.json', 'r') as f:
            output_str = f.read().strip()
    except FileNotFoundError:
        print(f'No output file for {test_name}')
        output_str = None

    received = parser.parse(input_str)
    print("received")
    print(received)
    received_str = ""
    for i in received:
        received_str += format_parser_output(i)  + ' \n'

    with open(f'./tests/{test_name}_received.json', 'w+') as f:
        f.write(received_str)
    
    if output_str is not None:
        if received_str.strip().strip("\n") != output_str.strip().strip("\n"):
            diff = difflib.unified_diff(output_str.split('\n'), received_str.split('\n'), f"./tests/{test_name}_output.json", f"./tests/{test_name}_received.json", lineterm='')
            with open(f'./tests/{test_name}_received.diff', 'w+') as f:
                f.write('\n'.join(diff) + '\n')
            raise AssertionError(f'{test_name} failed')
        else:
            try:
                os.remove(f'./tests/{test_name}_received.diff')
            except FileNotFoundError:
                pass
    else:
        raise AssertionError(f'{test_name} missing output file')
