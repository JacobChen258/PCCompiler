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
class block(Node):
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
    children: List[Expression]

@dataclass
class Id(Node):
    name: str

@dataclass
class BinaryOperation(Node):
    left: Expression
    right: Expression
    operator: str

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
    ifBody: block

@dataclass
class elifStmt(Node):
    elifCond: Expression
    elifBody: block

@dataclass
class elseStmt(Node):
    elseBody: block

@dataclass
class whileStmt(Node):
    cond: Expression
    body: block

@dataclass
class rangeValues(Node):
    stop: Union[int, None]
    start: Union[int, None]
    step: Union[int, None]

@dataclass
class forLoopRange(Node):
    var: Id 
    rangeVal: rangeValues
    body: block

@dataclass
class forLoopList(Node):
    var: Id
    Lst: NonPrimitiveLiteral
    body: block
    
@dataclass
class parameter(Node):
    paramType: Type
    var: Id

@dataclass
class parameterLst(Node):
    lst: Union[List[parameter], None]

@dataclass
class argumentLst(Node):
    lst: Union[List[Expression], None]

@dataclass
class functionDef(Node):
    name: Id
    lst: parameterLst
    body: block
    returnType: Union[Type, None]

@dataclass
class returnStmt(Node):
    stmt: Expression
    

@dataclass
class functionCall(Node):
    name: Id
    lst: argumentLst

@dataclass
class block(Node):
    lst: List[Union[functionDef, returnStmt, functionCall, forLoopRange, forLoopList, whileStmt, \
                    IfStmt, elifStmt, elseStmt, Assignment]]




    
