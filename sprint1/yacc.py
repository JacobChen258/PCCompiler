import argparse
from ply import yacc
from lex import pythonLexer
from lex import tokens
import AST

precedence = (
    ('nonassoc', 'EQGREATER', 'EQLESS', 'GREATER', 'LESS', 'EQUAL', 'NOTEQUAL'),
    ('left', 'OR', 'XOR', 'AND'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULE')
)


class statementNode():
    def __init__(self, lineNo, tabCount, astNode):
        self.lineNo = lineNo
        self.tabCount = tabCount
        self.astNode = astNode

lst_stack = []
tup_stack = []

statementNodeLst = []

final_result = []

def statementBodyGenerator():
    #print("dsfsaddfasdadadsasdas")
    stack = []
    current_statement_with_body = None # the statement that is being considered for any child statements
    expected_tab_count = 0
    statements_with_body = ["IfStmt", "elifStmt", "elseStmt", "whileStmt", "forLoopRange", "forLoopList", "functionDef"]
    for statement in statementNodeLst:
        if statement.tabCount == expected_tab_count and current_statement_with_body != None:
            current_statement_with_body.astNode.body.append(statement.astNode)
            print(current_statement_with_body.astNode.body)
        elif statement.tabCount < expected_tab_count:
            while statement.tabCount < expected_tab_count:
                current_statement_with_body = stack.pop()
                expected_tab_count -= 1
            if statement.tabCount != 0 and current_statement_with_body != None:
                current_statement_with_body.astNode.body.append(statement.astNode)
                
        if statement.tabCount == 0:
            final_result.append(statement.astNode)
            print("YESYESYESYES", statement.astNode)
        else:
            print("NONONOONONONO", statement.astNode)
        if statement.astNode.__class__.__name__ in statements_with_body:
            print("DSFDADSSASADDAS")
            stack.append(statement)
            current_statement_with_body = statement
            if current_statement_with_body.astNode.body == None:
                current_statement_with_body.astNode.body = []
            expected_tab_count += 1

    
    
class pythonParser:
    # def p_program(self,p):
    #     """program  : expression"""
    #     # """program  : expression
    #                 # | block"""
    #     p[0] = p[1]

    def p_block(self,p):
         """block    : statement_lst"""
         p[0] = p[1]

    def p_statement_lst(self, p):
        """statement_lst : statement_lst statement
                         |  statement"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] +[p[2]]

    #start = 'expression'


    def p_expression(self, p):
        """expression : ID
                      | assignment
                      | primitive_literal
                      | non_primitive_literal"""
        if type(p[1]) == str:  # It is ID
            p[0] = AST.Id(name=p[1])
        else:  # Anything else
            p[0] = p[1]

    def p_type(self, p):
        """type     : primitive_type
                    | non_primitive_type"""
        p[0] = AST.Type(p[1])

    def p_primitive_type(self, p):
        """primitive_type   : TINTEGER
                            | TSTRING
                            | TFLOAT
                            | TBOOL"""
        p[0] = AST.PrimitiveType(value=p[1].lower())

    def p_non_primitive(self, p):
        """non_primitive_type   : LBRACKET type RBRACKET
                                | LPAREN type RPAREN"""
        if p[1] == '[':
            p[0] = AST.NonPrimitiveType(name='list', type=p[2])
        elif p[1] == '(':
            p[0] = AST.NonPrimitiveType(name='tuple', type=p[2])
        else:
            assert False

    def p_primitive_literal(self, p):
        """primitive_literal    : INTEGER
                                | FLOAT
                                | STRING
                                | BOOL"""
        p[0] = AST.PrimitiveLiteral(name=p[1].__class__.__name__, value=p[1])

    def p_non_primitive_literal(self, p):
        """non_primitive_literal : list
                                 | tuple"""  # TODO: This needs to be a list
        p[0] = p[1]

    def p_assignment(self, p):
        """assignment :  ID ASSIGN expression
                      |  ID COLON type ASSIGN expression"""
        if len(p) == 4:
            p[0] = AST.Assignment(left=AST.Id(name=p[1]), type=None, right=p[3])
            # should the type be p[3].__class__.__name__?
        else:
            p[0] = AST.Assignment(left=AST.Id(name=p[1]), type=p[3], right=p[5])

    def p_statement(self, p):
        """statement : statement_no_new_line NEWLINE"""
        lineNo = self.lexer.lexLineNo
        tabCount = self.lexer.getTabCount(lineNo)
        statementNodeLst.append(statementNode(lineNo, tabCount, p[1]))
        p[0] = p[1]

    def p_statement_no_new_line(self, p):
        """statement_no_new_line : assignment
                                 | function_dec
                                 | function_call
                                 | return_stmt
                                 | if_statement
                                 | elif_statement
                                 | else_statement
                                 | while_statement
                                 | for_loop_range
                                 | for_loop_lst"""
        p[0] = p[1]


    def p_expr_binary(self, p):
        """expression   : expression PLUS expression
                        | expression MINUS expression
                        | expression TIMES expression
                        | expression DIVIDE expression
                        | expression MODULE expression
                        | expression EQGREATER expression
                        | expression EQLESS expression
                        | expression GREATER expression
                        | expression LESS expression
                        | expression EQUAL expression
                        | expression NOTEQUAL expression
                        | expression OR expression
                        | expression AND expression
                        | expression XOR expression"""
        p[0] = AST.BinaryOperation(left=p[1], operator=p[2], right=p[3])

    def p_expr_unary(self, p):
        """
        expression  : MINUS expression
                    | NOT expression"""
        p[0] = AST.UnaryOperation(operator=p[1], right=[2])

    def p_expr_paren(self, p):
        """
        expression  : LPAREN expression RPAREN"""
        p[0] = AST.UnaryOperation(operator=p[1], right=p[2])

    def p_lst_empty(self,p):
        """
        expression : LBRACKET RBRACKET
        """
        p[0] = AST.NonPrimitiveLiteral(name='list', children=[])
    def p_lst_head(self, p):
        """
        list    : LBRACKET expression
        """
        global lst_stack
        if not p[2]:
            lst = AST.NonPrimitiveLiteral(name='list', children=[lst_stack[-1].children.pop()])
        else:
            lst = AST.NonPrimitiveLiteral(name='list', children=[p[2]])
        lst_stack.append(lst)
        #print("++++++ head ++++++++")
        #print(lst_stack)


    def p_lst_body(self, p):
        """
        list    : list COMMA list
                | list COMMA expression
        """
        global lst_stack
        if p[3]:
            lst_stack[-1].children.append(p[3])


    def p_lst_tail(self, p):
        """
        expression      : list RBRACKET
        """
        global lst_stack
        if len(lst_stack) > 1:
            lst_stack[-2].children.append(lst_stack.pop())
        else:
            p[0] = lst_stack.pop()

    def p_lst_append(self, p):
        """
        expression    : expression APPEND LPAREN expression RPAREN
        """
        if isinstance(p[1],AST.NonPrimitiveLiteral) and p[1].name == 'list':
            p[1].children.append(p[4])
        else:
            self.p_error(p)

        
    def p_tuple_empty(self,p):
        """
        expression : LPAREN RPAREN
        """
        p[0] = AST.NonPrimitiveLiteral(name='tuple',children=[])

    def p_tuple_head(self,p):
        """
        tuple   : LPAREN expression COMMA expression
        """
        # tuple must have either 0 or more than 1 expression
        global tup_stack
        if not p[2]:
            tup = AST.NonPrimitiveLiteral(name='tuple', children=[tup_stack[-1].children.pop()])
        else:
            tup = AST.NonPrimitiveLiteral(name='tuple', children=[p[2], p[4]])
        tup_stack.append(tup)

    def p_tuple_body(self,p):
        """
        tuple   : tuple COMMA expression
                | tuple COMMA tuple
        """
        global tup_stack
        if p[3]:
            tup_stack[-1].children.append(p[3])

    def p_tuple_tail(self, p):
        """
        expression      : tuple RPAREN
        """
        global tup_stack
        if len(tup_stack) > 1:
            tup_stack[-2].children.append(tup_stack.pop())
        else:
            p[0] = tup_stack.pop()

    def p_expr_paren(self,p):
        """
        expression  : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_error(self, p):
        print("Syntax error at token", p)



    # def p_expr_uminus(self,p):
    #     'expression : MINUS expression %prec UMINUS'
    #     p[0] = -p[2]

    # def p_expr_unot(self,p):
    #     'expression : NOT expression %prec UNOT'
    #     p[0] = not p[2]

    def p_function_dec(self, p):
        """function_dec : DEF ID LPAREN paramter_or_empty RPAREN FUNCTIONANNOTATION type COLON"""

        p[0] = AST.functionDef(name=p[2], lst=p[4], body=None, returnType=p[7])

    def p_parameter_or_empty(self, p):
        """paramter_or_empty : parameter_lst
                            | empty"""
        if len(p) == 1:
            p[0] = AST.paramterLst(lst=None)
        else:
            p[0] = AST.parameterLst(lst=p[1])

    def p_parameter_lst(self, p):
        """parameter_lst : parameter_lst COMMA parameter
                         | parameter"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
            
    def p_parameter(self, p):
        """parameter : ID COLON type"""
        
        p[0] = AST.parameter(paramType=p[3], var=p[1])

    def p_function_call(self, p):
        """function_call : ID LPAREN argument_or_empty RPAREN"""
        p[0] = AST.functionCall(name=p[1], lst=p[3])
        
    def p_argument_or_empty(self, p):
        """argument_or_empty : argument_lst
                             | empty"""
        if len(p) == 1:
            p[0] = AST.argumentLst(lst=None)
        else:
            p[0] = AST.argumentLst(lst=p[1])
    
    def p_argument_lst(self, p):
        """argument_lst : argument_lst COMMA expression
                        | expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_return_stmt(self, p):
        """return_stmt : RETURN expression"""
        p[0] = AST.returnStmt(stmt=p[2])

    def p_if_statement(self, p):
        """if_statement : IF expression COLON"""
        #print("IF Statment")
        p[0] = AST.IfStmt(ifCond=p[2], body=None)
    def p_elif_statement(self, p):
        """elif_statement : ELIF expression COLON"""
        p[0] = AST.elifStmt(elifCond=p[2], body=None)
    def p_else_statement(self, p):
        """else_statement : ELSE COLON"""
        p[0] = AST.elseStmt(body=None)

    def p_for_loop_range(self, p):
        """for_loop_range : FOR ID IN range COLON"""
        p[0] = AST.forLoopRange(var=p[2], rangeVal=p[4], body=None)
        
    def p_range(self, p):
        """range : RANGE LPAREN expression RPAREN
                 | RANGE LPAREN expression COMMA expression RPAREN
                 | RANGE LPAREN expression COMMA expression COMMA expression RPAREN"""

        if len(p) == 5:
            p[0] = AST.rangeValues(stop=p[3], start=None, step=None)
        elif len(p) == 7:
            p[0] = AST.rangeValues(stop=p[3], start=[5], step=None)
        else:
            p[0] = AST.rangeValues(stop=p[3], start=[5], step=p[7])

    #for list and tuples
    def p_for_loop_lst(self, p):
        """for_loop_lst : FOR ID IN non_primitive_literal COLON
                        | FOR ID IN ID COLON"""
        p[0] = AST.forLoopList(var=p[2], Lst=p[4], body=None)

    def p_while_statement(self, p):
        """while_statement : WHILE expression COLON"""
        p[0] = AST.whileStmt(cond=p[2], body=None)
            
    def p_empty(self, p):
        """empty :"""
        pass

    # Build the parser

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = pythonLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        result = self.parser.parse(data)
        print("Result")
        print(result)
        print("statementNodeList")
        for i in statementNodeLst:
            print("lineNo: ", i.lineNo)
            print("tabCount: ", i.tabCount)
            print("astNode: ", i.astNode)
        print("Now body generator")
        statementBodyGenerator()
        #return self.parser.parse(data)
        return final_result #in list format in current version

    # def prompt(self):
    #     while True:
    #         try:
    #             s = input('calc > ')
    #         except EOFError:
    #             break
    #         if not s:
    #             continue
    #         result = self.parser.parse(s)
    #         print(result)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Take in the miniJava source code and parses it')
    argparser.add_argument('FILE', help='Input file with miniJava source code')
    args = argparser.parse_args()
    f = open(args.FILE, 'r')
    data = f.read()
    f.close()
    m = pythonParser()
    m.build()
    print(m.parse(data))
