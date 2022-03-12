from C_AST import *
from ir_gen import *


class CASTGenerator:
    seen_labels = []    # Labels have seen
    waiting_labels = []     # Labels have not seen
    declared_vars = []   # Keep track of declared variables
    C_AST = []
    def generate_AST(self, ir,st=None):
        self.ir = ir[:]
        while self.ir:
            self.C_AST.append(self.gen(self.ir.pop(),st))
        return self.C_AST

    def gen(self, ir_line):
        method = 'gen_' + ir_line.__class__.__name__
        try:
            return getattr(self, method)(ir_line)
        except AttributeError:
            print(f"Trying to process ir {ir_line}")
            raise

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
        pass

    def gen_IR_BinaryOperation(self,ir_node:IR_BinaryOperation,st=None):
        pass

    def gen_IR_UnaryOperation(self,ir_node:IR_UnaryOperation,st=None):
        pass

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
        pass

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
        pass

    def gen_IR_String_char(self,ir_node:IR_String_char,st=None):
        pass

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


