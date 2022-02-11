from ply import yacc
from lex import pythonLexer
from lex import tokens

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
    ('right',
     'UMINUS',
     'UNONT'),
)


class pythonParser:

    def p_program(self,p):
        """program  : expression
                    | block"""
        p[0] = p[1]

    def p_block(self,p):
        """block    : while_block
                    | for_block
                    | if_block"""
        p[0] = p[1]

    def p_parameter(self,p):
        """parameter    : ID : type"""
        p[0] = p[1] + ":" + p[2]

    def p_type(self,p):
        """type     : primitive_type
                    | non_primitive_type"""
        p[0] = p[1]

    def p_primitive(self,p):
        """primitive_type   : TINTEGER
                            | TSTRING
                            | TFLOAT
                            | TBOOL"""
        p[0] = p[1]

    def p_non_primitive(self,p):
        """non_primitive_type   : LBRACKET type RBRACKET
                                | LPAREN type RPAREN"""
        if p[1] == '[':
            p[0] = '[' + p[2] + ']'
        else:
            p[0] = '(' + p[2] + ')'

    def p_numeric_term(self,p):
        """numeric_term     : number
                            | ID"""
        p[0] = p[1]

    def p_numeric(self,p):
        """number   : INTEGER
                    | FLOAT"""
        p[0] = [1]

    def p_cond_no_paren_term(self,p):
        """cond_no_paren_term   : BOOL
                                | number
                                | STRING"""
        p[0] = p[1]

    def p_expr_uminus(self,p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    def p_expr_unot(self,p):
        'expression : NOT expression %prec UNOT'
        p[0] = not p[2]

    def p_function_dec(self, p):
        """function_dec : DEF ID LPAREN paramter_or_empty RPAREN COLON FUNCTIONANNOTATION type"""

    def p_parameter_or_empty(self, p):
        """paramter_or_empty: paramter_lst | empty

        """

    def p_parameter_lst(self, p):
        """parameter_lst : parameter_lst COMMA parameter
                     | parameter
        """

    def p_function_call(self, p):
        """function_call : ID LPAREN argument_or_empty RPAREN
        
        """
    def p_argument_or_empty(self, p):
        """argument_or_empty : argument_lst | emtpy

        """
    
    def p_argument_lst(self, p):
        """argument_lst : argument_lst COMMA expression | expression

        """

    # Build the parser
    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = pythonLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    # Show the prompt for user input
    def prompt(self):
        while True:
            try:
                s = input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            result = self.parser.parse(s)
            print(result)

if __name__ == "__main__":
    m = pythonParser()
    m.build()
    m.prompt()
