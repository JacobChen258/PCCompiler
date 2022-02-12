from ply import yacc
from lex import pythonLexer
from lex import tokens
import AST

precedence = (
    ('nonassoc',
     'EQGREATER',
     'EQLESS',
     'GREATER',
     'LESS',
     'EQUAL',
     'NOTEQUAL',),
    ('left',
     'PLUS',
     'MINUS'),
    ('left',
     'TIMES',
     'DIVIDE',
     'MODULE'),
    # ('right',
    #  'UMINUS',
    #  'UNONT'),
)


class pythonParser:
    # def p_program(self,p):
    #     """program  : expression"""
    #     # """program  : expression
    #                 # | block"""
    #     p[0] = p[1]

    # def p_block(self,p):
    #     """block    : while_block
    #                 | for_block
    #                 | if_block"""
    #     p[0] = p[1]

    def p_expression(self,p):
        """expression : ID
                      | assignment
                      | primitive_literal
                      | non_primitive_literal"""
        if type(p[1]) == str: # It is ID
            p[0] = AST.Id(name=p[1])
        else: # Anything else
            p[0] = p[1]

    def p_type(self, p):
        """type     : primitive_type
                    | non_primitive_type"""
        p[0] = AST.Type(p[1])

    def p_primitive_type(self, p):
        """primitive_type   : TINT
                            | TSTR
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
        """non_primitive_literal : LBRACKET expression RBRACKET
                                 | LPAREN expression RPAREN""" # TODO: This needs to be a list
        if p[1] == '[':
            p[0] = AST.NonPrimitiveLiteral(name='list', children=p[2])
        elif p[1] == '(':
            p[0] = AST.NonPrimitiveLiteral(name='tuple', children=p[2])
        else:
            assert False

    def p_assignment(self, p):
        """assignment :  ID ASSIGN expression
                      |  ID COLON type ASSIGN expression"""
        if len(p) == 4:
            p[0] = AST.Assignment(left=AST.Id(name=p[1]), type=None, right=p[3])
        else:
            p[0] = AST.Assignment(left=AST.Id(name=p[1]), type=p[3], right=p[5])

    # def p_expr_uminus(self,p):
    #     'expression : MINUS expression %prec UMINUS'
    #     p[0] = -p[2]

    # def p_expr_unot(self,p):
    #     'expression : NOT expression %prec UNOT'
    #     p[0] = not p[2]

    

    # Build the parser

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = pythonLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        return self.parser.parse(data)

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
    m = pythonParser()
    m.build()
    print(m.parse("a = 10"))
    # m.prompt()
