from dataclasses import dataclass
import AST

"""
- goto: label
- op: left, right, operator, result
- push-param: var
- pop-param: var
- if: var, label for false, label for end
- elif: TODO
- else: TODO
- while: var, label for start, label for end

- list: ???
- for-loop: ???
- string: ???

- function declaration
  - return statement
- function call

"""

@dataclass
class IR_Label:
    value: int

@dataclass
class IR_Goto:
    label: int

@dataclass
class IR_BinaryOperation:
    result_reg: int
    left_reg: int
    right_reg: int
    operator: str

@dataclass
class IR_UnaryOperation:
    result_reg: int
    operator: str
    operand_reg: int

@dataclass
class IR_PushParam:
    reg: int

@dataclass
class IR_PopParam:
    reg: int

@dataclass
class IR_FunctionCall:
    name: str

@dataclass
class IR_FunctionReturn:
    reg: int

@dataclass
class IR_ReturnStmt:
    reg: int


class IRGen:
    def __init__(self):
        self.IR = []
        self.register_count = 0
        self.label_count = 0

    def generate(self, node):
        method = 'gen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def add_code(self, code):
        self.IR.append(code)

    def inc_register(self):
        self.register_count += 1
        return self.register_count

    def reset_register(self):
        self.register_count = 0

    def inc_label(self):
        self.label_count += 1
        return self.label_count

    def mark_label(self, label: int):
        self.IR.append(IR_Label(value=label))

    def print_ir(self):
        for ir in self.IR:
            print(ir)

    ###################################


    def gen_FunctionDef(self, node: AST.FunctionDef):
        skip_decl = self.inc_label()

        self.add_code(IR_Goto(label=skip_decl))

        self.mark_label(node.name)

        ###InComplete

    def gen_FunctionCall(self, node: AST.FunctionCall):
        args = node.lst
        for arg in args:
            self.add_code(IR_PushParam(reg=self.generate(arg)))

        self.add_code(IR_FunctionCall(name=node.name))

        self.add_code(IR_PopParam(reg=len(arg)))
        
        reg = self.inc_register()
        self.add_code(IR_FunctionReturn(reg=reg))

        return reg

    def gen_ReturnStmt(self, node: AST.ReturnStmt):
        expr = self.generate(node.stmt)
        self.add_code(IR_ReturnStmt(reg=expr))

    def gen_Assignment(self, node: AST.Assignment):
        pass

    def gen_RangeValues(self, node: AST.RangeValues):
        pass

    def gen_ForLoopList(self, node: AST.ForLoopList):
        pass

    def gen_ForLoopRange(self, node: AST.ForLoopRange):
        pass

    def gen_PrimitiveLiteral(self, node: AST.PrimitiveLiteral):
        pass

    def gen_NonPrimitiveLiteral(self, node: AST.NonPrimitiveLiteral):
        pass

    def gen_BinaryOperation(self, node: AST.BinaryOperation):
        left_reg = self.generate(node.left)
        operator = node.operator
        right_reg = self.generate(node.right)
        result_reg = self.inc_register()
        self.add_code(IR_BinaryOperation(result_reg=result_reg, left_reg=left_reg, right_reg=right_reg, operator=operator))
        return result_reg

    def gen_UnaryOperation(self, node: AST.UnaryOperation):
        operator = node.operator
        right_reg = self.generate(node.right)
        result_reg = self.inc_register()
        self.add_code(IR_UnaryOperation(result_reg=result_reg, operand_reg=right_reg, operator=operator))
        return result_reg

    def gen_IfStmt(self, node: AST.IfStmt):
        pass

    def gen_ElifStmt(self, node: AST.ElifStmt):
        pass

    def gen_ElseStmt(self, node: AST.ElseStmt):
        pass

    def gen_WhileStmt(self, node: AST.WhileStmt):
        pass

    def gen_Id(self, node: AST.Id):
        pass

"""
    def gen_AssignStmt(self, node):
        expr = self.generate(node.expr)
        self.add_code("{} := {}".format(node.name, expr))
        self.register_count = 0

    def gen_BinOp(self, node):
        # Left operand
        left = self.generate(node.left)
        # Right operand
        right = self.generate(node.right)

        reg = self.inc_register()
        self.add_code("{} := {} {} {}".format('_t%d' % reg, left, node.op, right))

        return '_t%d' % reg

    def gen_Constant(self, node):
        return node.value

    def gen_DeclStmt(self, node):
        expr = self.generate(node.expr)
        self.add_code("{} := {}".format(node.name, expr))
        self.register_count = 0

    def gen_FuncCall(self, node):

        # Push all of the arguments with "PushParam" function
        args = node.children()
        for (i, arg) in args:
            self.add_code("PushParam %s" % self.generate(arg))

        # Once all of the parameter has been pushed, actually call the function
        self.add_code("FuncCall %s" % node.name)

        # After we're done with the function, remove the spaces reserved
        # for the arguments
        self.add_code("PopParams %d" % len(args))

        reg = self.inc_register()
        self.add_code("{} := ret".format('_t%d' % reg))

        return '_t%d' % reg

    def gen_IfStmt(self, node):
        cond = self.generate(node.cond)

        fbranch_label = self.inc_label()
        tbranch_label = self.inc_label()

        # Skip to the false_body if the condition is not met
        self.add_code("if !({}) goto {}".format(cond, '_L%d' % fbranch_label))
        self.generate(node.true_body)
        # Make sure the statements from false_body is skipped
        self.add_code("goto _L%d" % tbranch_label)

        self.mark_label(fbranch_label)
        self.generate(node.false_body)
        self.mark_label(tbranch_label)

    def gen_MethodDecl(self, node):

        skip_decl = self.inc_label()

        # We want to skip the function code until it is called
        self.add_code("goto _L%d" % skip_decl)

        # Function label
        self.mark_label(node.name)

        # Allocate room for function local variables
        self.add_code("BeginFunc")

        # Actually generate the main body
        self.generate(node.body)
        self.generate(node.ret_stmt)

        # Do any cleanup before jumping back
        self.add_code("EndFunc")

        self.mark_label(skip_decl)

    def gen_Program(self, node):
        for (child_name, child) in node.children():
            self.generate(child)

    def gen_RetStmt(self, node):
        expr = self.generate(node.expr)
        self.add_code("ret := {}".format(expr))

    def gen_StmtList(self, node):
        for stmt in node.stmt_lst:
            self.generate(stmt)
"""
