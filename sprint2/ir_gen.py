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
class IR_PrimitiveLiteral:
    reg: int
    val: any

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
class IR_FunctionCall:
    name: str
    reg: int

@dataclass
class IR_FunctionReturn:
    reg: int

@dataclass
class IR_ReturnStmt:
    reg: int

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

#determines start of a list or tuple
@dataclass
class IR_List:
    reg: int
    operator: str #LIST, TUPLE 
    length: int

#represents individual elements in a list or tuple
@dataclass
class IR_List_VAL:
    reg: int

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

@dataclass
class IR_String:
    reg: int
    length: int

@dataclass
class IR_String_char:
    reg: int
    val: str

@dataclass
class IR_Parameter:
    reg:int
    length:int

@dataclass
class IR_Parameter_VAL:
    reg:int
    name:str

@dataclass
class IR_Argument:
    reg: int
    function_call_reg: int
    length: int

@dataclass
class IR_Argument_VAL:
    reg: int

@dataclass
class IR_Address:
    addr_reg: str

@dataclass
class IR_Deref:
    pointer_reg: str

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
        skip_decl = self.inc_label()

        self.add_code(IR_Goto(label=skip_decl))

        self.mark_label(node.name)

        params = node.lst
        params_reg = self.inc_register()
        self.add_code(IR_Parameter(reg=params_reg, length=len(params)))
        for param in params:
            param_reg = self.inc_register()
            self.add_code(IR_Parameter_VAL(reg=param_reg, name=param.var))



        

    def gen_FunctionCall(self, node: AST.FunctionCall):
        args = node.lst
        function_reg = self.inc_register()
        arg_reg = self.inc_register()
        self.add_code(IR_Argument(reg=arg_reg,function_call_reg=function_reg ,length=len(args)))
        for arg in args:
            self.add_code(IR_Argument_VAL(reg=self.generate(arg)))

        self.add_code(IR_FunctionCall(name=node.name, function_call_reg=function_reg))
        
        reg = self.inc_register()
        self.add_code(IR_FunctionReturn(reg=reg))

        return reg

    def gen_ReturnStmt(self, node: AST.ReturnStmt):
        expr = self.generate(node.stmt)
        self.add_code(IR_ReturnStmt(reg=expr))

    def gen_Assignment(self, node: AST.Assignment):
        self.add_code(IR_Assignment(name=self.generate(node.left),val=self.generate(node.right)))
        return node.left

    def gen_ForLoopList(self, node: AST.ForLoopList):
        # Assume list is address referenced
        list_reg = self.generate(node.Lst)
        cur_ptr = self.inc_register()
        self.add_code(IR_Assignment(name=cur_ptr,val = IR_Address(addr_reg=list_reg)))
        length_reg = self.inc_register()
        # first index of array is the length of array
        self.add_code(IR_Assignment(name=length_reg, val=IR_Deref(pointer_reg=cur_ptr)))
        # go to next index, which has the actual value
        self.add_code(IR_BinaryOperation(result_reg=cur_ptr,left_reg=cur_ptr,right_reg=1,operator="+"))
        end_ptr = self.inc_register()
        # calculate address of final index
        self.add_code(IR_BinaryOperation(result_reg=end_ptr,left_reg=cur_ptr,right_reg=length_reg,operator="+"))
        t_label = self.inc_label("FOR")
        f_label = self.inc_label()
        self.mark_label(t_label)
        cond_reg = self.inc_register()
        # check if current pointer address reached the end of address
        self.add_code(IR_BinaryOperation(result_reg=cond_reg, left_reg=cur_ptr, right_reg=end_ptr, operator="<"))
        self.add_code(IR_IfStmt(if_false=IR_Goto(f_label),cond_reg=cond_reg))
        self.add_code(IR_Assignment(name=node.var,val=IR_Deref(pointer_reg=cur_ptr)))
        for node in node.body.lst:
            self.generate(node)
        # increment idx
        self.add_code(IR_BinaryOperation(result_reg=cur_ptr,left_reg=cur_ptr,right_reg=1,operator="+"))
        self.add_code(IR_Goto(t_label))
        self.mark_label(f_label)

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
        for body in node.body.lst:
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
        for body in node.body.lst:
            self.generate(body)
        self.add_code(IR_Goto(t_label))
        self.mark_label(f_label)

    def gen_PrimitiveLiteral(self, node: AST.PrimitiveLiteral):
        prim_reg = self.inc_register()
        if node.name == "str":
            self.add_code(IR_String(reg=prim_reg, length=len(node.value)))
            for c in node.value:
                string_reg = self.inc_register()
                self.add_code(IR_String_char(reg=string_reg, val=c))
        else:
            self.add_code(IR_PrimitiveLiteral(reg=prim_reg, val=node.value))
        return prim_reg

    def gen_NonPrimitiveLiteral(self, node: AST.NonPrimitiveLiteral):
        begin = self.inc_register()
        if node.name == "list":
            self.add_code(IR_List(operator="LIST", reg=begin, length=len(node.children)))
        else:
            self.add_code(IR_List(operator="TUPLE", reg=begin, length=len(node.children)))

        for element in node.children:
            self.add_code(IR_List_VAL(self.generate(element)))

        return begin

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
        for stmt in node.body.lst:
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
        for stmt in node.body.lst:
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
        for stmt in node.body.lst:
            self.generate(stmt)
        # insert else IR
        self.IR = ir_copy[:cond_label_idx_stack[-1]] + self.IR + ir_copy[cond_label_idx_stack[-1]:]
        # pop cond_label and cond_label_idx
        cond_label_idx_stack.pop(-1)
        cond_label_stack.pop(-1)

    def gen_Id(self, node: AST.Id):
        return node.name

