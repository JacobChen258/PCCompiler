import pytest
from yacc import pythonParser

@pytest.fixture
def parser():
    p = pythonParser()
    p.build()
    return p

cases = {
    "a = 10": "FLOAT",
    "a = 10.0": "FLOAT",
}

@pytest.mark.parametrize("input_data, expected", cases.items())
def test_simple_token(parser, input_data, expected):
    result = parser.parse(input_data)
    print(result)
    assert False
