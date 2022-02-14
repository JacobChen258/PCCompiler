from ply import lex

reserved = {
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'range': 'RANGE',
    'if': "IF",
    'elif': "ELIF",
    'else': "ELSE",
    'return': 'RETURN',
    'int': 'TINTEGER',
    'str': 'TSTRING',
    'float': "TFLOAT",
    'bool': "TBOOL",
    'def': "DEF",
    'print': "PRINT",
    '.append': "APPEND"
}

tokens = [
    'PLUS',
    'MINUS',
    'MODULE',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'EQGREATER',
    'EQLESS',
    'NOTEQUAL',
    'EQUAL',
    'ASSIGN',
    'GREATER',
    'LESS',
    'AND',
    'OR',
    'NOT',
    'XOR',
    'PERIOD',
    'FUNCTIONANNOTATION',
    'NONE',
    'BOOL',
    'STRING',
    'FLOAT',
    'INTEGER',
    'ID',
    'NEWLINE',
    'TAB', 
    'COLON',
    'COMMA',
] + list(reserved.values())

# NOTICE: STRING INCLUDES THE QUOTATION MARKS AS WELL


class pythonLexer():
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MODULE = r'%'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_EQGREATER = r'\>='
    t_EQLESS = r'\<='
    t_EQUAL = r'=='
    t_ASSIGN = r'='
    t_GREATER = r'\>'
    t_LESS = r'\<'
    t_XOR = r'\^'
    t_PERIOD = r'.'
    t_COMMA = r','
    t_COLON = r':'
    #t_FUNCTIONANNOTATION = r'(-\>)'
    t_ignore_COMMENT = r'\#.*'
    t_ignore = ' '
    literals = ".!@-`~\\|/{}?'\""

    #keeps track number of tabs for each line number
    tab_list = []
    lexLineNo = 1


    def t_NONE(self,t):
        r'None'
        t.value = None
        return t

    def t_BOOL(self,t):
        r'(True)|(False)'
        t.value = bool(t.value)
        return t

    def t_NOTEQUAL(self,t):
        r'\!='
        return t

    def t_AND(self,t):
        r'(and)|(&)'
        return t

    def t_OR(self,t):
        r'(or)|\|'
        return t

    def t_NOT(self,t):
        r'(not)|!'
        return t

    # NOT HANDLE ESCAPE STRING YET
    def t_STRING(self,t):
        r'("(?:\\.|[^"\\])*")|(\'(?:\\.|[^\'\\])*\')'
        t.value = str(t.value)
        return t

    def t_FLOAT(self,t):
        r'-?(([1-9]\d*)|(0))\.\d*'
        t.value = float(t.value)
        return t

    def t_INTEGER(self,t):
        r'-?(([1-9]\d*)|0)'
        t.value = int(t.value)
        return t

    def t_ID(self,t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID')  # Check for reserved words
        return t

    def t_NEWLINE(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.lexLineNo = t.lexer.lineno
        print("NewLine Stufffffff")
        print(len(t.value))
        print(t.lexer.lineno)
        return t

    def t_TAB(self, t):
        r'\t+'
        print("TAB TAB TAB TAB STUFFFFFF")
        self.tab_list.append([t.lexer.lineno + 1, len(t.value)])
        print(self.tab_list)

    def t_FUNCTIONANNOTATION(self, t):
        r'(-\>)'
        return t


    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def getTabCount(self, lineNo):
        for i in self.tab_list:
            if i[0] == lineNo:
                return i[1]
        return 0

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        result = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            result.append(tok)
        return result

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Take in the miniJava source code and perform lexical analysis.')
    parser.add_argument('FILE', help="Input file with miniJava source code")
    args = parser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    m = pythonLexer()
    m.build()
    print(m.test(data), sep='\n')
