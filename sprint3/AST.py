from __future__ import annotations
from typing import Union, List, Literal
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
class PrimitiveType(Node):
    value: Literal['str', 'int', 'float', 'bool', 'none']

    def __init__(self, value):
        self.value = value
        assert value in ['str', 'int', 'float', 'bool', 'none']

@dataclass
class NonPrimitiveType(Node):
    name: Union['tuple', 'list']
    value: PrimitiveType

@dataclass
class Type(Node):
    value: Union[PrimitiveType, NonPrimitiveType]

@dataclass
class Expression(Node):
    value: Union[BinaryOperation, UnaryOperation, Id, PrimitiveLiteral, NonPrimitiveLiteral]
               # Commented out because python wants them to be defined first, which results in a circular dependency

@dataclass
class PrimitiveLiteral(Node):
    name: Union['str', 'int', 'float', 'bool']
    value: str

@dataclass
class NonPrimitiveLiteral(Node):
    name: Union['tuple', 'list']
    children: List[Union[any, None]]

@dataclass(unsafe_hash=True)
class Id(Node):
    name: str

@dataclass
class BinaryOperation(Node): # Jat
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOperation(Node): # Jat
    operator: str
    right: Expression

@dataclass
class Assignment(Node): # Mostly done already
    left: Id
    type: Union[Type, None]
    right: Node

@dataclass
class IfStmt(Node): # Jat
    ifCond: Expression
    body: Block

@dataclass
class ElifStmt(Node): # Jat
    elifCond: Expression
    body: Block

@dataclass
class ElseStmt(Node): # Jat
    body: Block

@dataclass
class WhileStmt(Node): # Jat
    cond: Expression
    body: Block

@dataclass
class RangeValues(Node): # Yifei
    stop: Union[Expression, None]
    start: Union[Expression, None]
    step: Union[Expression, None]

@dataclass
class ForLoopRange(Node): # Yifei
    var: Id
    rangeVal: RangeValues
    body: Block

@dataclass
class ForLoopList(Node): # Yifei
    var: Id
    Lst: Expression
    body: Block

@dataclass
class Parameter(Node): # Jocob
    paramType: Type
    var: Id

@dataclass
class ParameterLst(Node): # Jocob
    lst: Union[List[Parameter], None]

@dataclass
class ArgumentLst(Node): # Jocob
    lst: Union[List[Expression], None]

@dataclass
class FunctionDef(Node): # Jocob
    name: Id
    lst: ParameterLst
    body: Block
    returnType: Union[Type, None]

@dataclass
class ReturnStmt(Node): # Jocob
    stmt: Expression


@dataclass
class FunctionCall(Node):
    name: Id
    lst: ArgumentLst

@dataclass
class Block(Node):
    lst: List[Union[FunctionDef, ReturnStmt, FunctionCall, ForLoopRange, ForLoopList, WhileStmt, \
                    IfStmt, ElifStmt, ElseStmt, Assignment]]

@dataclass
class LstAppend(Node):
    obj: Union[NonPrimitiveLiteral,Id]
    val: Expression

@dataclass
class NonPrimitiveIndex(Node):
    obj: Expression
    idx: Expression




