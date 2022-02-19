from typing import Union, List
from dataclasses import dataclass

class Node():
    pass
    # def children(self):
    #     pass
    # attr_names = ()

# class NodeVisitor():
#     def visit(self, node):
#         method = 'visit_' + type(node).__name__
#         visitor = getattr(self, method, self.visit_generic)
#         return visitor(node)

#     def visit_generic(self, node, offset=0):
#         lead = ' ' * offset
#         output = lead + node.__class__.__name__ + ': '
#         if node.attr_names:
#             vlist = [getattr(node, n) for n in node.attr_names]
#             output += ', '.join(str(v) for v in vlist)

#         for child_name, child in node.children():
#             visitor = self.visit(child, offset + 2)
#             if visitor is not None:
#                 output += '\n' + visitor

#         return output

@dataclass
class Block(Node):
    pass

@dataclass
class PrimitiveType(Node):
    value: Union['str', 'int', 'float', 'bool']

    def __init__(self, value):
        self.value = value
        assert value in ['str', 'int', 'float', 'bool']

@dataclass
class NonPrimitiveType(Node):
    name: Union['tuple', 'list']
    value: PrimitiveType

@dataclass
class Type(Node):
    value: Union[PrimitiveType, NonPrimitiveType]

@dataclass
class Expression(Node):
    value: any #Union[BinaryOperation, UnaryOperation, Id, PrimitiveLiteral, NonPrimitiveLiteral]
               # Commented out because python wants them to be defined first, which results in a circular dependency

@dataclass
class PrimitiveLiteral(Node):
    name: Union['str', 'int', 'float', 'bool']
    value: str

@dataclass
class NonPrimitiveLiteral(Node):
    name: Union['tuple', 'list']
    children: List[Union[any, None]]

@dataclass
class Id(Node):
    name: str

@dataclass
class BinaryOperation(Node):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOperation(Node):
    operator: str
    right: Expression

@dataclass
class Assignment(Node):
    left: Id
    type: Union[Type, None]
    right: Node

@dataclass
class IfStmt(Node):
    ifCond: Expression
    body: Block

@dataclass
class ElifStmt(Node):
    elifCond: Expression
    body: Block

@dataclass
class ElseStmt(Node):
    body: Block

@dataclass
class WhileStmt(Node):
    cond: Expression
    body: Block

@dataclass
class RangeValues(Node):
    stop: Union[int, None]
    start: Union[int, None]
    step: Union[int, None]

@dataclass
class ForLoopRange(Node):
    var: Id
    rangeVal: RangeValues
    body: Block

@dataclass
class ForLoopList(Node):
    var: Id
    Lst: NonPrimitiveLiteral
    body: Block

@dataclass
class Parameter(Node):
    paramType: Type
    var: Id

@dataclass
class ParameterLst(Node):
    lst: Union[List[Parameter], None]

@dataclass
class ArgumentLst(Node):
    lst: Union[List[Expression], None]

@dataclass
class FunctionDef(Node):
    name: Id
    lst: ParameterLst
    body: Block
    returnType: Union[Type, None]

@dataclass
class ReturnStmt(Node):
    stmt: Expression


@dataclass
class FunctionCall(Node):
    name: Id
    lst: ArgumentLst

@dataclass
class Block(Node):
    lst: List[Union[FunctionDef, ReturnStmt, FunctionCall, ForLoopRange, ForLoopList, WhileStmt, \
                    IfStmt, ElifStmt, ElseStmt, Assignment]]





