import C_AST
from ir_gen import *
from symbol_table import SymbolTable
from typing import Union, List
from AST import Type as A_Type


class CASTGenerator:

    def __init__(self):
        self.seen_labels = []  # Labels have seen
        self.waiting_labels = []  # Labels have not seen
        self.temp_st = SymbolTable()  # Keep track of declared variables
        self.result_AST = []
        self.end_if_labels = []  # value is a tuple (label name, head of if)

    def generate_AST(self, ir, st=None):
        self.ir = ir[:]
        while self.ir:
            ir_line = self.ir.pop(0)
            self.result_AST += self.gen(ir_line, st)
        return C_AST.Block(self.result_AST)

    def gen(self, ir_line, st=None):
        method = 'gen_' + ir_line.__class__.__name__
        try:
            return getattr(self, method)(ir_line, st)
        except AttributeError:
            print(f"Trying to process ir {ir_line}")
            raise

    def gen_IR_Label(self, ir_node: IR_Label, st=None):
        if "FOR" in ir_node.value:
            # do something for FOR
            pass
        elif "WHILE" in ir_node.value:
            # do something for WHILE
            return self._gen_IR_While(self.ir.pop(0), st)
        elif 'FUNC' in ir_node.value:
            # This is a function, we need the label at the top of waiting
            # to find the end of declaration
            # Based on our Function IR, return statement is required.
            # Also, assume functions are declared in global scope
            end_func_idx = ir_node.value.rfind("_")
            return self._gen_IR_Func(self.ir.pop(0), ir_node.value[7:end_func_idx], st)
        else:
            # other cases
            return ir_node.value

    def gen_IR_Goto(self, ir_node: IR_Goto, st=None):
        if ir_node.label not in self.seen_labels:
            # If label not in seen, it means the following code is in a block
            self.waiting_labels.append(ir_node.label)
        return []

    def gen_IR_PrimitiveLiteral(self, ir_node: IR_PrimitiveLiteral, st=None):
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
        self.temp_st.declare_variable(name=ir_node.reg, type=C_AST.Type(value=type_val))
        id_node = C_AST.Id(name=ir_node.reg)
        decl_node = C_AST.Declaration(id=id_node, type=C_AST.Type(value=type_val))
        return [decl_node, C_AST.Assignment(id=id_node, val=ir_node.val)]

    def gen_IR_BinaryOperation(self, ir_node: IR_BinaryOperation, st=None):
        result_node = C_AST.Id(name=ir_node.result_reg)
        left_node = C_AST.Id(name=ir_node.left_reg)
        right_node = C_AST.Id(name=ir_node.right_reg)
        operation_node = C_AST.BinaryOperation(left=result_node,
                                               operator=ir_node.operator,
                                               operand_a=left_node,
                                               operand_b=right_node)
        if ir_node.result_reg not in self.temp_st.scope_stack[-1]:
            # need assignment
            # should we consider string here?
            if ir_node.operator in ["<", "<=", "=>", ">", "=="]:
                type_t = 'bool_t'
            else:
                operand_t = [self.temp_st.lookup_variable(ir_node.left_reg).value,
                             self.temp_st.lookup_variable(ir_node.right_reg).value]
                if 'float_t' in operand_t:
                    type_t = 'float_t'
                else:
                    type_t = 'int_t'
            self.temp_st.declare_variable(name=ir_node.result_reg, type=C_AST.Type(value=type_t))
            decl_node = C_AST.Declaration(id=result_node, type=C_AST.Type(value=type_t))
            return [decl_node, operation_node]
        return [operation_node]

    def gen_IR_UnaryOperation(self, ir_node: IR_UnaryOperation, st=None):
        result_node = C_AST.Id(name=ir_node.result_reg)
        operand_node = C_AST.Id(name=ir_node.left_reg)
        operation_node = C_AST.UnaryOperation(left=result_node, operator=ir_node.operator, operand=operand_node)
        if ir_node.result_reg not in self.temp_st.scope_stack[-1]:
            if ir_node.operator == "!":
                type_t = "bool_t"
            else:
                type_t = self.temp_st.lookup_variable(ir_node.operand_reg).value
            decl_node = C_AST.Declaration(id=result_node, type=C_AST.Type(value=type_t))
            return [decl_node, operation_node]
        return [operation_node]

    def gen_IR_PushParam(self, ir_node: IR_PushParam, st=None):  # should it be just value rather than register?
        pass

    def gen_IR_PopParam(self, ir_node: IR_PopParam, st=None):  # number of params to pop?
        pass

    def gen_IR_FunctionCall(self, ir_node: IR_FunctionCall, st=None):
        pass

    def gen_IR_FunctionReturn(self, ir_node: IR_FunctionReturn, st=None):
        pass

    def gen_IR_ReturnStmt(self, ir_node: IR_ReturnStmt, st=None):
        return [C_AST.ReturnStmt(stmt=C_AST.Id(ir_node.reg))]

    def gen_IR_PushStack(self, ir_node: IR_PushStack, st=None):
        pass

    def gen_IR_PopStack(self, ir_node: IR_PopStack, st=None):
        pass

    def gen_IR_IfStmt(self, ir_node: IR_IfStmt, st=None):
        false_label = ir_node.if_false.label
        idx = 0
        prev_node = None
        next_node = self.ir[idx]
        # if next node is not label or not the false label, then it is in body
        while not (next_node.__class__.__name__ == 'IR_Label' and next_node.value == false_label):
            idx += 1
            prev_node = next_node
            next_node = self.ir[idx]
        # based on the if stmt structure in IR, the end of if label must be before false label
        self.end_if_labels.append([prev_node.label, 0])
        if_node = C_AST.IfStmt(ifCond=C_AST.Id(name=ir_node.cond_reg), body=C_AST.Block([]))
        # signal is set to false when reaching the false label
        continue_sig = True
        self.temp_st.push_scope()
        while continue_sig:
            node = self.ir.pop(0)
            val = self.gen(node, st)
            if val and val == false_label:
                continue_sig = False
            elif val:
                if_node.body.lst += val
        # call elif to check if we have following elif
        if_stmt = self._gen_IR_ElifStmt(self.ir.pop(0), [if_node], st)
        self.temp_st.pop_scope()
        return if_stmt

    def _gen_IR_ElifStmt(self, ir_node: any, if_stmt=None, st=None):
        idx = 0
        prev_node = None
        next_node = ir_node
        continue_sig = True
        while not (next_node.__class__.__name__ == 'IR_ElifStmt' or \
                   (next_node.__class__.__name__ == 'IR_Label' and next_node.value == self.end_if_labels[-1][0])):
            # it has to reach one of the condition without reaching the end of ir
            prev_node = next_node
            next_node = self.ir[idx]
            idx += 1
        self.temp_st.push_scope()
        if next_node.__class__.__name__ == 'IR_Label':
            # if stmts is empty, there is not trailing if statements
            if not prev_node:
                self.end_if_labels.pop()
                self.temp_st.pop_scope()
                return if_stmt
            result_stmt = C_AST.ElseStmt(body=C_AST.Block([]))
            cur_node = ir_node
            while continue_sig:
                val = self.gen(cur_node, st)
                if val and val == self.end_if_labels[-1][0]:
                    continue_sig = False
                elif val:
                    result_stmt.body.lst += val
                if continue_sig:
                    cur_node = self.ir.pop(0)
        else:
            # reach elif, stmts are the conditonal expression, need to be inserted before if head`
            cond_ast = []
            cur_node = ir_node
            while cur_node.__class__.__name__ != 'IR_ElifStmt':
                cond_ast += self.gen(cur_node, st)
                cur_node = self.ir.pop(0)
            if_stmt = if_stmt[:self.end_if_labels[-1][1]] + cond_ast + if_stmt[self.end_if_labels[-1][1]:]
            self.end_if_labels[-1][1] += len(cond_ast)
            result_stmt = C_AST.ElifStmt(elifCond=C_AST.Id(cur_node.cond_reg), body=C_AST.Block([]))
            false_label = next_node.elif_false.label
            while continue_sig:
                node = self.ir.pop(0)
                val = self.gen(node, st)
                if val and val == false_label:
                    continue_sig = False
                elif val:
                    result_stmt.body.lst += val
        if_stmt.append(result_stmt)
        if result_stmt.__class__.__name__ == "ElseStmt":
            self.end_if_labels.pop()
            self.temp_st.pop_scope()
            return if_stmt
        if_stmt = self._gen_IR_ElifStmt(self.ir.pop(0), if_stmt, st)
        self.temp_st.pop_scope()
        return if_stmt

    def gen_IR_Assignment(self, ir_node: IR_Assignment, st=None):
        id_node = C_AST.Id(name=ir_node.name)
        stmt_node = C_AST.Assignment(id=id_node, val=ir_node.val)
        if ir_node.name not in self.temp_st.scope_stack[-1]:
            type_t = self.temp_st.lookup_variable(name=ir_node.val).value
            self.temp_st.declare_variable(name=ir_node.name, type=C_AST.Type(type_t))
            decl_node = C_AST.Declaration(id=id_node, type=C_AST.Type(type_t))
            return [decl_node, stmt_node]
        return [stmt_node]

    def gen_IR_List(self, ir_node: IR_List, st=None):
        pass

    def gen_IR_List_VAL(self, ir_node: IR_List_VAL, st=None):
        pass

    def gen_IR_LoopStart(self, ir_node: IR_LoopStart, st=None):
        pass

    def gen_IR_LoopStop(self, ir_node: IR_LoopStop, st=None):
        pass

    def gen_IR_LoopStep(self, ir_node: IR_LoopStep, st=None):
        pass

    def gen_IR_String(self, ir_node: IR_String, st=None):
        pass

    def gen_IR_String_char(self, ir_node: IR_String_char, st=None):
        pass

    def gen_IR_Parameter(self, ir_node: IR_Parameter, st=None):
        pass

    def gen_IR_Parameter_VAL(self, ir_node: IR_Parameter_VAL, st=None):
        return ir_node.name

    def gen_IR_Argument(self, ir_node: IR_Argument, st=None):
        pass

    def gen_IR_Argument_VAL(self, ir_node: IR_Argument_VAL, st=None):
        pass

    def gen_IR_Address(self, ir_node: IR_Address, st=None):
        pass

    def gen_IR_Deref(self, ir_node: IR_Deref, st=None):
        pass

    def _gen_IR_Func(self, ir_node: IR_Parameter, func_name: str, st: SymbolTable):
        params = []
        param_regs = []
        length = ir_node.length
        for i in range(length):
            cur_node = self.ir.pop(0)
            val = self.gen(cur_node)
            params.append(val)
            param_regs.append(cur_node.reg)
        types = st.get_func_by_name(func_name, params)
        converted_types = self.convert_types(types[0])
        converted_ret_type = self.convert_types([types[1]])[0]
        hash_name = self.temp_st.declare_C_function(func_name, converted_types, types[1])
        self.temp_st.push_scope()
        param_lst = C_AST.ParameterLst([])
        for i in range(len(params)):
            param_lst.lst.append(C_AST.Parameter(var=C_AST.Id(params[i]), paramType=converted_types[i]))
            self.temp_st.declare_variable(params[i], converted_types[i])
            self.temp_st.declare_variable(param_regs[i], converted_types[i])
        func_node = C_AST.FunctionDeclaration(name=C_AST.Id(hash_name), lst=param_lst, body=C_AST.Block([]), \
                                              returnType=converted_ret_type)
        continue_sig = True
        while continue_sig:
            cur_node = self.ir.pop(0)
            val = self.gen(cur_node, st)
            if val and val == self.waiting_labels[-1]:
                self.seen_labels.append(self.waiting_labels.pop())
                continue_sig = False
            elif val:
                func_node.body.lst += val
        return [func_node]

    def convert_types(self, param_types: List[A_Type]):
        converted_types = []
        for type in param_types:
            if type.value.__class__.__name__ == "PrimitiveType":
                converted_types.append(C_AST.Type(type.value.value + "_t"))
            else:
                converted_types.append(C_AST.NonPrimitiveType(type.value.name))
        return converted_types

    def _gen_IR_While(self, ir_node: any, st=None):
        head = []
        cur_node = ir_node
        while cur_node.__class__.__name__ != "IR_IfStmt":
            head += self.gen(cur_node, st)
            cur_node = self.ir.pop(0)
        false_label = cur_node.if_false.label
        result_stmt = C_AST.WhileStmt(cond=C_AST.Id(cur_node.cond_reg),body=C_AST.Block([]))
        continue_sig = True
        while continue_sig:
            cur_node = self.ir.pop(0)
            val = self.gen(cur_node,st)
            if val and val == false_label:
                continue_sig = False
            elif val:
                result_stmt.body.lst+= val
        return head + [result_stmt]

