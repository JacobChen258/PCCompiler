from yacc import pythonLexer, pythonParser
from type_checker import TypeChecker, SymbolTable

# lex = pythonLexer()
# lex.build()
# print(lex.test("a = 10"), sep='\n')

parser = pythonParser()
parser.build()

tc = TypeChecker()
print(tc.typecheck(parser.parse("a: [int] = [12]\n")[0], SymbolTable()))
