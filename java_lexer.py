import re
import ply.lex as lex


reserved = (
    'ABSTRACT', 'CONTINUE',
    'FOR', 'NEW', 'SWITCH',
    'ASSERT', 'DEFAULT', 'GOTO', 'PACKAGE', 'SYNCHRONIZED',
    'BOOLEAN', 'D', 'IF', 'PRIVATE', 'THIS',
    'BREAK', 'DOUBLE', 'IMPLEMENTS', 'PROTECTED', 'THROW',
    'BYTE', 'ELSE', 'IMPORT', 'PUBLIC', 'THROWS',
    'CASE', 'ENUM', 'INSTANCEOF', 'RETURN', 'TRANSIENT',
    'CATCH', 'EXTENDS', 'FINAL', 'INTERFACE', 'STATIC', 'VOID',
    'CLASS', 'FINALLY', 'STRICTFP', 'VOLATILE',
    'CONST', 'NATIVE', 'SUPER', 'WHILE',
    'INT', 'DOUBLE', 'CHAR', 'STRING', 'BOOLEAN', 'SYSTEM', 'OUT', 'PRINTLN'
)

reserved_lower = [r.lower() for r in reserved]
reserved_lower[reserved_lower.index('string')] = 'String'
reserved_lower[reserved_lower.index('system')] = 'System'

tokens = reserved + (
    'IDENTIFIER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    'EQUALS', 'PLUSEQUAL', 'MINUSEQUAL',
    'PLUSPLUS', 'MINUSMINUS',
    'LPAREN', 'RPAREN',
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'SEMI', 'COLON',
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_MOD = r'%'
t_OR = r'(\|\|)|(OR)'
t_AND = r'(\&\&|AND)'
t_NOT = r'!'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_EQUALS = r'='
t_PLUSEQUAL = r'\+='
t_MINUSEQUAL = r'-='
t_PLUSPLUS = r'\+\+'
t_MINUSMINUS = r'--'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_PERIOD = r'\.'
t_SEMI = r';'

def t_BOOLEAN(token):
    r'(true|false)'
    return token

def t_IDENTIFIER(token):
    r'[A-Za-z$_][A-Za-z0-9$_]*'
    if token.value in reserved_lower:
        token.type = token.value.upper()
    return token

def t_DOUBLE(token):
    r'-?(\d+\.\d+)'
    try:
        token.value = float(token.value)
    except ValueError:
        print('Error in converting: %f', token.value)
        token.value = 0.0
    return token

def t_INT(token):
    r'-?(\d+)'
    try:
        token.value = int(token.value)
    except ValueError:
        print('Error in converting: %d', token.value)
        token.value = 0
    return token

def t_CHAR(token):
    r'\'([^\\\n]|(\\.))*?\''
    return token

def t_STRING(token):
    r'\"([^\\\n"]|(\\.))*\"'
    return token

def t_newline(token):
    r'\n'
    token.lexer.lineno += token.value.count("\n")

def t_error(token):
    if token.value[0] != ' ':
        print("Illegal character {0} at {1}:{2}".format(token.value[0], token.lineno, token.lexpos))
    token.lexer.skip(1)

