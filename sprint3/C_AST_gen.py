import C_AST
from ir_gen import *


class CASTGenerator:
    seen_labels = []    # Labels have seen
    waiting_labels = []     # Labels have not seen
    temp_st = {}   # Keep track of declared variables
    result_AST = []
    current_str = None
    current_str_count = 0

    def generate_AST(self, ir,st=None):
        self.ir = ir[:]
        while self.ir:
            ir_line = self.ir.pop(0)
            self.result_AST += self.gen(ir_line, st)
        return C_AST.Block(self.result_AST)

    def gen(self, ir_line,st=None):
        method = 'gen_' + ir_line.__class__.__name__
        try:
            return getattr(self, method)(ir_line,st)
        except AttributeError:
            print(f"Trying to process ir {ir_line}")
            raise

    def lookup_temp(self,name):
        if name in self.temp_st:
            return self.temp_st[name]
        return None

    def gen_IR_Label(self, ir_node:IR_Label,st=None):
        if "FOR" in ir_node.value:
            # do something for FOR
            pass
        elif "WHILE" in ir_node.vlaue:
            # do something for WHILE
            pass
        elif 'FUNC' in ir_node.value:
            # This is a function, we need the label at the top of waiting
            # to find the end of declaration
            pass
        else:
            # other cases
            pass

    def gen_IR_Goto(self,ir_node:IR_Goto,st=None):
        if ir_node.label in self.seen_labels:
            pass
        # If label not in seen, it means the following code is in a block
        self.waiting_labels.append(ir_node.label)

    def gen_IR_PrimitiveLiteral(self,ir_node:IR_PrimitiveLiteral,st=None):
        ''' All primitive literal are assigned to register'''
        type_val = type(ir_node.val)
        # String is not represented as primitive literal in IR
        if type_val == int:
            type_val = 'int_t'
        elif type_val == float:
            type_val = "float_t"
        else:
            type_val = "bool_t"
        # Primitive Literal Reg will not be assigned again
        self.temp_st[ir_node.reg] = type_val
        id_node = C_AST.Id(name=ir_node.reg)
        decl_node = C_AST.Declaration(id = id_node,type=C_AST.Type(value=type_val))
        return [decl_node,C_AST.Assignment(id=id_node,val=ir_node.val)]

    def gen_IR_BinaryOperation(self,ir_node:IR_BinaryOperation,st=None):
        result_node = C_AST.Id(name=ir_node.result_reg)
        left_node = C_AST.Id(name=ir_node.left_reg)
        right_node = C_AST.Id(name=ir_node.right_reg)
        operation_node = C_AST.BinaryOperation(left=result_node,
                                               operator=ir_node.operator,
                                               operand_a=left_node,
                                               operand_b=right_node)
        if not self.lookup_temp(ir_node.result_reg):
            # need assignment
            # should we consider string here?
            if ir_node.operator in ["<", "<=", "=>", ">"]:
                type_t = 'bool_t'
            else:
                operand_t = [self.lookup_temp(ir_node.left_reg),self.lookup_temp(ir_node.right_reg)]
                if 'float_t' in operand_t:
                    type_t = 'float_t'
                else:
                    type_t = 'int_t'
            self.temp_st[ir_node.result_reg] = type_t
            decl_node = C_AST.Declaration(id=result_node,type=C_AST.Type(value=type_t))
            return [decl_node,operation_node]
        return [operation_node]

    def gen_IR_UnaryOperation(self,ir_node:IR_UnaryOperation,st=None):
        result_node = C_AST.Id(name=ir_node.result_reg)
        operand_node = C_AST.Id(name=ir_node.left_reg)
        operation_node = C_AST.UnaryOperation(left=result_node,operator=ir_node.operator,operand=operand_node)
        if not self.lookup_temp(ir_node.result_reg):
            if ir_node.operator == "!":
                type_t = "bool_t"
            else:
                type_t = self.lookup_temp(ir_node.operand_reg)
            decl_node = C_AST.Declaration(id=result_node,type=C_AST.Type(value=type_t))
            return [decl_node,operation_node]
        return [operation_node]

    def gen_IR_PushParam(self,ir_node:IR_PushParam,st=None):  # should it be just value rather than register?
        pass

    def gen_IR_PopParam(self,ir_node:IR_PopParam,st=None):  # number of params to pop?
        pass

    def gen_IR_FunctionCall(self,ir_node:IR_FunctionCall,st=None):
        pass

    def gen_IR_FunctionReturn(self,ir_node:IR_FunctionReturn,st=None):
        pass

    def gen_IR_ReturnStmt(self,ir_node:IR_ReturnStmt,st=None):
        pass

    def gen_IR_PushStack(self,ir_node:IR_PushStack,st=None):
        pass

    def gen_IR_PopStack(self,ir_node:IR_PopStack,st=None):
        pass

    def gen_IR_IfStmt(self,ir_node:IR_IfStmt,st=None):
        pass

    def gen_IR_ElifStmt(self,ir_node:IR_ElifStmt,st=None):
        pass

    def gen_IR_Assignment(self,ir_node:IR_Assignment,st=None):
        id_node = C_AST.Id(name=ir_node.name)
        stmt_node = C_AST.Assignment(id=id_node,val=ir_node.val)
        if not self.lookup_temp(name=ir_node.name):
            type_t = self.lookup_temp(name=ir_node.val)
            self.temp_st[ir_node.name] = type_t
            decl_node = C_AST.Declaration(id=id_node,type=C_AST.Type(type_t))
            return [decl_node,stmt_node]
        return [stmt_node]

    def gen_IR_List(self,ir_node:IR_List,st=None):
        pass

    def gen_IR_List_VAL(self,ir_node:IR_List_VAL,st=None):
        pass

    def gen_IR_LoopStart(self,ir_node:IR_LoopStart,st=None):
        pass

    def gen_IR_LoopStop(self,ir_node:IR_LoopStop,st=None):
        pass

    def gen_IR_LoopStep(self,ir_node:IR_LoopStep,st=None):
        pass

    def gen_IR_String(self,ir_node:IR_String,st=None):
        current_str = C_AST.String(val="", len=node.length)
        current_str_count = 0
        return current_str

    def gen_IR_String_char(self,ir_node:IR_String_char,st=None):
        current_str.val = current_str.val + node.val
        current_str_count += 1
        if current_str_count == current_str.len:
            current = current_str
            current_str_count = 0
            current_str = None
            


    def gen_IR_Parameter(self,ir_node:IR_Parameter,st=None):
        pass

    def gen_IR_Parameter_VAL(self,ir_node:IR_Parameter_VAL,st=None):
        pass

    def gen_IR_Argument(self,ir_node: IR_Argument,st=None):
        pass

    def gen_IR_Argument_VAL(self,ir_node: IR_Argument_VAL,st=None):
        pass

    def gen_IR_Address(self,ir_node:IR_Address,st=None):
        pass

    def gen_IR_Deref(self,ir_node:IR_Deref,st=None):
        pass


