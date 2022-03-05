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

cond_label_stack = []
cond_label_idx_stack = []

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
class IR_PushParam: # should it be just value rather than register?
    reg: int

@dataclass
class IR_PopParam: # number of params to pop?
    reg: int

@dataclass
class IR_PushStack:
    val: int

class IR_PopStack:
    val: int

@dataclass
class IR_IfStmt:
    if_false: IR_Goto
    cond_reg: int

@dataclass
class IR_ElifStmt:
    elif_false: IR_Goto
    cond_reg: int

@dataclass
class IR_Assignment:
    name: str
    val: any

@dataclass
class IR_LoopStart:
    reg: str
    val: any

@dataclass
class IR_LoopStop:
    reg: str
    val: any

@dataclass
class IR_LoopStep:
    reg: str
    val: any

class IRGen:
    def __init__(self):
        self.IR = []
        self.register_count = 0
        self.label_count = 0

    def generate_IR(self,nodes):
        for node in nodes:
            self.generate(node)

    def generate(self, node):
        method = 'gen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def add_code(self, code):
        self.IR.append(code)

    def inc_register(self):
        self.register_count += 1
        return "_t{}".format(self.register_count)

    def reset_register(self):
        self.register_count = 0

    def inc_label(self,type=None):
        self.label_count += 1
        if type:
            return "L_{}{}".format(type,self.label_count)
        return "L_{}".format(self.label_count)

    def mark_label(self, label: int):
        self.IR.append(IR_Label(value=label))

    def print_ir(self):
        for ir in self.IR:
            print(ir)

    ###################################


    def gen_FunctionDef(self, node: AST.FunctionDef):
        pass

    def gen_FunctionCall(self, node: AST.FunctionCall):
        pass

    def gen_ReturnStmt(self, node: AST.ReturnStmt):
        pass

    def gen_Assignment(self, node: AST.Assignment):
        self.add_code(IR_Assignment(name=self.generate(node.left),val=self.generate(node.right)))
        return node.left

    def gen_ForLoopList(self, node: AST.ForLoopList):
        pass

    def gen_RangeValues(self, node:AST.RangeValues):
        start_reg = self.inc_register()
        stop_reg = self.inc_register()
        step_reg = self.inc_register()
        if node.start:
            self.add_code(IR_LoopStart(reg=start_reg, val=self.generate(node.start)))
        else:
            self.add_code(IR_LoopStart(reg=start_reg, val=self.generate(0)))
        self.add_code(IR_LoopStop(reg=stop_reg, val=self.generate(node.stop)))
        if node.step:
            self.add_code(IR_LoopStep(reg=step_reg, val=self.generate(node.step)))
        else:
            self.add_code(IR_LoopStep(reg=step_reg, val=1))
        return [start_reg,step_reg,stop_reg]

    def gen_ForLoopRange(self, node: AST.ForLoopRange):
        range = self.generate(node.rangeVal)
        t_label = self.inc_label("FOR")
        f_label = self.inc_label()
        self.add_code(IR_Assignment(name=node.var, val=range[0]))
        self.mark_label(t_label)
        cond_reg = self.inc_register()
        self.add_code(IR_BinaryOperation(result_reg=cond_reg, left_reg=node.var, right_reg=range[2], operator="<"))
        self.add_code(IR_IfStmt(if_false=IR_Goto(f_label), cond_reg=cond_reg))
        for body in node.body:
            self.generate(body)
        self.add_code(IR_BinaryOperation(result_reg=range[0], left_reg=node.var, right_reg=range[1], operator="+"))
        self.add_code(IR_Assignment(name=node.var,val=range[0]))
        self.add_code(IR_Goto(t_label))
        self.mark_label(f_label)


    def gen_WhileStmt(self, node: AST.WhileStmt):
        t_label = self.inc_label("WHILE")
        f_label = self.inc_label()
        self.mark_label(t_label)
        cond = self.generate(node.cond)
        self.add_code(IR_IfStmt(if_false=IR_Goto(f_label), cond_reg=cond))
        for body in node.body:
            self.generate(body)
        self.add_code(IR_Goto(t_label))
        self.mark_label(f_label)

    def gen_PrimitiveLiteral(self, node: AST.PrimitiveLiteral):
        return node.value

    def gen_NonPrimitiveLiteral(self, node: AST.NonPrimitiveLiteral):
        vals = []
        for node in node.children:
            vals.append(self.generate(node))
        return vals

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
        global cond_label_stack,cond_label_idx_stack
        cond = self.generate(node.ifCond)

        fbranch_label = self.inc_label()
        cond_label_stack.append(self.inc_label())   # record the

        # Skip to the false_body if the condition is not met
        self.add_code(IR_IfStmt(if_false=IR_Goto(fbranch_label),cond_reg=cond))
        for stmt in node.body:
            self.generate(stmt)
        # End of true body
        self.add_code(IR_Goto(cond_label_stack[-1]))

        # mark false and true labels
        # record the idx of true label for elif and else insertion
        # it is possible that false label has no content
        self.mark_label(fbranch_label)
        cond_label_idx_stack.append(len(self.IR))
        self.mark_label(cond_label_stack[-1])

    def gen_ElifStmt(self, node: AST.ElifStmt):
        global cond_label_stack, cond_label_idx_stack
        # copy the whole IR to make sure that
        # subsequent conditional stmts are in place
        ir_copy = self.IR[:]
        # reset IR
        self.IR = []
        cond = self.generate(node.elifCond)
        fbranch_label = self.inc_label()
        self.add_code(IR_ElifStmt(elif_false=IR_Goto(fbranch_label), cond_reg=cond))
        for stmt in node.body:
            self.generate(stmt)
        self.add_code(IR_Goto(cond_label_stack[-1]))
        self.mark_label(fbranch_label)
        len_elif = len(self.IR)
        # insert elif IR
        self.IR = ir_copy[:cond_label_idx_stack[-1]] + self.IR + ir_copy[cond_label_idx_stack[-1]:]
        # update the true label index
        cond_label_idx_stack[-1] += len_elif



    def gen_ElseStmt(self, node: AST.ElseStmt):
        global cond_label_stack, cond_label_idx_stack
        # copy the whole IR to make sure that
        # subsequent conditional stmts are in place
        ir_copy = self.IR[:]
        # reset IR
        self.IR = []
        for stmt in node.body:
            self.generate(stmt)
        # insert else IR
        self.IR = ir_copy[:cond_label_idx_stack[-1]] + self.IR + ir_copy[cond_label_idx_stack[-1]:]
        # pop cond_label and cond_label_idx
        cond_label_idx_stack.pop(-1)
        cond_label_stack.pop(-1)

    def gen_Id(self, node: AST.Id):
        return node.name

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
    
        def gen_IfStmt(self, node: AST.IfStmt):
        print("if statement")
        cond = self.generate(node.ifCond)
        fbranch_label = self.inc_label()
        tbranch_label = None # This will be assigned,once all subsequent condition statements are done
        sub_cond = None # This is for the elif and else statement

        # Skip the statement body if the condition is false
        self.add_code(IR_IfStmt(if_false=IR_Goto(fbranch_label),cond_reg=cond))
        for i in range(len(node.body)):
            # check if elif or else exists, we need to generate their code separately
            if node.body[i].__class__.__name__ == "ElifStmt" or node.body[i].__class__.__name__ == "ElseStmt":
                sub_cond = node.body[i]
            else:
                self.generate(node.body[i])

        tlabel_idx = len(self.IR)
        self.add_code(tbranch_label) # make space for tlabel, will be updated later

        self.mark_label(fbranch_label)
        # to unify the tlabel for all subsequent conditional statements
        # we let elif and else return the true label value
        if sub_cond:
            tbranch_label = self.generate(sub_cond)
        else:
            # if there is no elif or else, then just get the next label number
            tbranch_label = self.inc_label()
        # update IR
        self.IR[tlabel_idx] = IR_Goto(tbranch_label)
        # make the true label here instead of else stmt
        self.mark_label(tbranch_label)

    def gen_ElifStmt(self, node: AST.ElifStmt):
        # same as ifStmt
        cond = self.generate(node.elifCond)
        fbranch_label = self.inc_label()
        tbranch_label = None
        sub_cond = None

        self.add_code(IR_ElifStmt(elif_false=IR_Goto(fbranch_label), cond_reg=cond))
        for i in range(len(node.body)):
            if node.body[i].__class__.__name__ == "ElifStmt" or node.body[i].__class__.__name__ == "ElseStmt":
                sub_cond = node.body[i]
            else:
                self.generate(node.body[i])

        tlabel_idx = len(self.IR)
        self.add_code(tbranch_label)

        self.mark_label(fbranch_label)
        if sub_cond:
            tbranch_label = self.generate(sub_cond)
        else:
            tbranch_label = self.inc_label()
        self.IR[tlabel_idx] = IR_Goto(tbranch_label)
        # we don't mark label here, return tlabel instead
        return tbranch_label

    def gen_ElseStmt(self, node: AST.ElseStmt):
        # elseStmt generate body and return the tlabel, nothing else
        for i in range(len(node.body)):
                self.generate(node.body[i])
        tlabel = self.inc_label()
        # no need goto here
        return tlabel

"""
