from java_lexer import *
import ply.yacc as yacc
import sys

start = 'java'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'EQUALS'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NE', 'EQ'),
    ('left', 'GT', 'LT', 'GE', 'LE'),
    ('right','NEW', 'NOT'),
    ('left', 'PERIOD')
)

def p_java(p):
    'java : element java'
    p[0] = [p[1]] + p[2]

def p_java_empty(p):
    'java : '
    p[0] = []

def p_element_class(p):
    'element : PUBLIC CLASS IDENTIFIER compoundelem'
    p[0] = ('class', p[3], p[4])

def p_compoundelem(p):
    'compoundelem : LBRACE elements RBRACE'
    p[0] = p[2]

def p_elements(p):
    'elements : element elements'
    p[0] = [p[1]] + p[2]

def p_elements_empty(p):
    'elements : '
    p[0] = []

def p_element_statement(p):
    'element : statement'
    p[0] = ('statement', p[1])

def p_element_function(p):
    'element : PUBLIC return_type IDENTIFIER LPAREN optparams RPAREN compoundstmt'
    p[0] = ('function', p[2], p[3], p[5], p[7])

def p_element_function_static(p):
    'element : PUBLIC STATIC return_type IDENTIFIER LPAREN optparams RPAREN compoundstmt'
    p[0] = ('function', p[3], p[4], p[6], p[8])

def p_return_type(p):
    'return_type : type'
    p[0] = p[1]

def p_optparams(p):
    'optparams : params'
    p[0] = p[1]

def p_optparams_empty(p):
    'optparams : '
    p[0] = []

def p_params(p):
    'params : type IDENTIFIER COMMA params'
    p[0] = [(p[1], p[2])] + p[4]

def p_params_array(p):
    'params : type LBRACKET RBRACKET IDENTIFIER COMMA params'
    p[0] = [(p[1], p[4])] + p[6]

def p_params_last(p):
    'params : type IDENTIFIER'
    p[0] = [(p[1], p[2])]

def p_params_array_last(p):
    'params : type LBRACKET RBRACKET IDENTIFIER'
    p[0] = [(p[1], p[4])]

def p_statement_return(p):
    'statement : RETURN exp SEMI'
    p[0] = ('return', p[2])

def p_statement_for_loop(p):
    'statement : FOR LPAREN statement exp SEMI exp RPAREN compoundstmt'
    p[0] = ('for_loop', p[3], p[4], p[6], p[8])

def p_statement_if_then(p):
    'statement : IF LPAREN exp RPAREN ifstmt'
    p[0] = ('if-then', p[3], p[5])

def p_statement_if_then_else(p):
    'statement : IF LPAREN exp RPAREN ifstmt ELSE elsestmt'
    p[0] = ('if-then-else', p[3], p[5], p[7])

def p_ifstmt(p):
    '''ifstmt : statement
              | compoundstmt'''
    p[0] = p[1]

def p_compoundstmt(p):
    'compoundstmt : LBRACE statements RBRACE'
    p[0] = p[2]

def p_statements(p):
    'statements : statement statements'
    p[0] = [p[1]] + p[2]

def p_statements_empty(p):
    'statements : '
    p[0] = []

def p_elsestmt(p):
    '''elsestmt : statement
                | compoundstmt'''
    p[0] = p[1]

def p_statement_exp(p):
    'statement : exp SEMI'
    p[0] = ('exp', p[1])

def p_statement_identifier_assignment(p):
    'statement : IDENTIFIER EQUALS exp SEMI'
    p[0] = ('assign', p[1], p[3])

def p_statement_array_assignment(p):
    '''statement : IDENTIFIER LBRACKET INT RBRACKET EQUALS exp SEMI
                 | IDENTIFIER LBRACKET IDENTIFIER RBRACKET EQUALS exp SEMI'''
    p[0] = ('assign_array', p[1], p[3], p[6])

def p_statement_var_decl(p):
    'statement : type IDENTIFIER SEMI'
    p[0] = ('decl_var', p[1], p[2])

def p_statement_var_decl_init(p):
    'statement : type IDENTIFIER EQUALS exp SEMI'
    p[0] = ('decl_init_var', p[1], p[2], p[4])

def p_statement_array_decl(p):
    'statement : type LBRACKET RBRACKET IDENTIFIER EQUALS NEW type LBRACKET INT RBRACKET SEMI'
    p[0] = ('decl_array', p[1], p[4], p[9])

def p_statement_print(p):
    'statement : SYSTEM PERIOD OUT PERIOD PRINTLN LPAREN exp RPAREN SEMI'
    p[0] = ('print', p[7])

def p_type(p):
    '''type : INT
            | DOUBLE
            | CHAR
            | STRING
            | BOOLEAN
            | VOID'''
    p[0] = p[1]

def p_exp_call(p):
    'exp : IDENTIFIER LPAREN optargs RPAREN'
    p[0] = ('call', p[1], p[3])

def p_optargs(p):
    'optargs : args'
    p[0] = p[1] # the work happens in "args"

def p_optargsempty(p):
    'optargs : '
    p[0] = [] # no arguments -> return the empty list

def p_args(p):
    'args : exp COMMA args'
    p[0] = [p[1]] + p[3]

def p_args_last(p): # one argument
    'args : exp'
    p[0] = [p[1]]

def p_exp_int(p):
    'exp : INT'
    p[0] = ('int', p[1])

def p_exp_double(p):
    'exp : DOUBLE'
    p[0] = ('double', p[1])

def p_exp_identifier(p):
    'exp : IDENTIFIER'
    p[0] = ('identifier', p[1])

def p_exp_identifier_array(p):
    '''exp  : IDENTIFIER LBRACKET INT RBRACKET
            | IDENTIFIER LBRACKET IDENTIFIER RBRACKET'''
    p[0] = ('identifier_array', p[1], p[3])

def p_exp_unaryop(p):
    '''exp  : PLUSPLUS IDENTIFIER
            | MINUSMINUS IDENTIFIER'''
    p[0] = ('unaryop', p[1], p[2])

def p_exp_binop(p):
    '''exp  : exp PLUS exp
            | exp MINUS exp
            | exp TIMES exp
            | exp DIVIDE exp
            | exp GT exp
            | exp GE exp
            | exp LT exp
            | exp LE exp
            | exp EQ exp
            | exp NE exp'''
    p[0] = ('binop', p[1], p[2], p[3])

def p_exp_binop_paren(p):
    '''exp  : LPAREN exp PLUS exp RPAREN
            | LPAREN exp MINUS exp RPAREN
            | LPAREN exp TIMES exp RPAREN
            | LPAREN exp DIVIDE exp RPAREN
            | LPAREN exp GT exp RPAREN
            | LPAREN exp GE exp RPAREN
            | LPAREN exp LT exp RPAREN
            | LPAREN exp LE exp RPAREN
            | LPAREN exp EQ exp RPAREN
            | LPAREN exp NE exp RPAREN'''
    p[0] = ('binop', p[2], p[3], p[4])

def p_exp_char(p):
    'exp : CHAR'
    p[0] = ('char', p[1])

def p_exp_string(p):
    'exp : STRING'
    p[0] = ('String', p[1])

def p_exp_boolean(p):
    'exp : BOOLEAN'
    p[0] = ('boolean', p[1])

def p_error(p):
    if p:
        print("syntax error by token {0} of type {1} at {2}:{3}"
                .format(p.value, p.type, p.lineno, p.lexpos))
    else:
        print('syntax error at EOF')
    sys.exit(1)


# javaLexer = lex.lex()
javaParser = yacc.yacc()
# inputString = '''if(4<5){
#                     int x=4+9;
#                         x = 30;
#                     }'''
# parseTree = javaParser.parse(inputString, javaLexer)

# if parseTree:
#     print(parseTree)