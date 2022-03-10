from __future__ import annotations
from ast import operator
from typing import Union, List
from dataclasses import dataclass


@dataclass
class Type:
    value: str # 'str_t', 'int_t', 'float_t', 'bool_t'
    # str_t -> char*
    # int_t -> long long
    # float_t -> double
    # bool_t -> bool or int

@dataclass
class NonPrimitiveType:
    type: Union['list', 'tuple']

@dataclass
class Id:
    name: str

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
    ifCond: Expression
    body: Block

@dataclass
class ElifStmt:
    elifCond: Expression
    body: Block

@dataclass
class ElseStmt:
    body: Block

@dataclass
class WhileStmt:
    cond: Expression
    body: Block

@dataclass
class Expression:
    value: Union[BinaryOperation, UnaryOperation, Id]

@dataclass
class Block:
    lst: List[Union[FunctionDeclaration, ReturnStmt, FunctionCall, ForLoopRange, ForLoopList, WhileStmt, \
                    IfStmt, ElifStmt, ElseStmt, BinaryOperation, UnaryOperation]]


"""
int t12;
t12 = t11 * t10;


"""
