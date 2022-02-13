import pytest
from yacc import pythonParser

@pytest.fixture
def parser():
    p = pythonParser()
    p.build()
    return p

cases = {
    "a = 10": "Assignment(left=Id(name='a'), type=None, right=PrimitiveLiteral(name='int', value=10))",
    "bbb = 10.0": "Assignment(left=Id(name='bbb'), type=None, right=PrimitiveLiteral(name='float', value=10.0))",
    "bbb: int = 10.0": "Assignment(left=Id(name='bbb'), type=Type(value=PrimitiveType(value='int')), right=PrimitiveLiteral(name='float', value=10.0))",
    "[]" : "NonPrimitiveLiteral(name='list', children=[])",
    "[1,2,3]" : "NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), PrimitiveLiteral(name='int', value=2), PrimitiveLiteral(name='int', value=3)])",
    "[1,[1,2]]" :"NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), PrimitiveLiteral(name='int', value=2)])])",
    "[1,[1,2],[1,2,3],[[[1]]],1]" : "NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), PrimitiveLiteral(name='int', value=2)]), NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1), PrimitiveLiteral(name='int', value=2), PrimitiveLiteral(name='int', value=3)]), NonPrimitiveLiteral(name='list', children=[NonPrimitiveLiteral(name='list', children=[NonPrimitiveLiteral(name='list', children=[PrimitiveLiteral(name='int', value=1)])])]), PrimitiveLiteral(name='int', value=1)])",
}

@pytest.mark.parametrize("input_data, expected", cases.items())
def test_simple_token(parser, input_data, expected):
    result = parser.parse(input_data)
    assert str(result) == expected, f"Expect {expected}, got {str(result)}"


"""
## Experimenting with alternative stringify method

So instead of

Assignment(left=Id(name='bbb'), type=Type(value=PrimitiveType(value='int')), right=PrimitiveLiteral(name='float', value=10.0))

We have
{'NODE': 'Assignment',
 'left': {'NODE': 'Id', 'name': 'bbb'},
 'right': {'NODE': 'PrimitiveLiteral', 'name': 'float', 'value': 10.0},
 'type': {'NODE': 'Type', 'value': {'NODE': 'PrimitiveType', 'value': 'int'}}}

# def test_simple_token_error(parser):
#     import json
#     from pprint import pprint
#     result = parser.parse('bbb: int = 10.0')
#     pprint(json.loads(json.dumps(result, default=lambda x: { 'NODE': x.__class__.__name__, **x.__dict__})))
#     assert False

"""
