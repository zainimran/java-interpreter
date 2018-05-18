from java_lexer import *
from java_parser import *
import sys

global_environment = (None, {})

return_var = None

class_name = None

j_to_p_type = {
                'int': int,
                'double': float,
                'char': str,
                'String': str,
                'boolean': bool
            }

def env_lookup(environment, var_name):
    parent_env = environment[0]
    scoped_var_dict = environment[1]
    if var_name in scoped_var_dict:
        found_var = scoped_var_dict[var_name]
        return found_var
    elif parent_env is not None:
        return env_lookup(parent_env, var_name)
    else:
        print 'var does not exist or out of scope'
        sys.exit(1)

def env_lookup_list(environment, var_name, index):
    parent_env = environment[0]
    scoped_var_dict = environment[1]
    if var_name in scoped_var_dict:
        found_var = scoped_var_dict[var_name]
        return found_var
    elif parent_env is not None:
        env_lookup(parent_env, var_name)
    else:
        print 'array does not exist or out of scope'
        sys.exit(1)

def env_update(environment, var_name, new_value):
    parent_env = environment[0]
    scoped_var_dict = environment[1]
    if var_name in scoped_var_dict:
        if isinstance(new_value, j_to_p_type[scoped_var_dict[var_name]['type']]):
            if scoped_var_dict[var_name]['type'] == 'char':
                if len(new_value) <= 3:
                    scoped_var_dict[var_name]['value'] = new_value
                else:
                    print 'char type can not be updated to a string'
                    sys.exit(1)
            else:
                scoped_var_dict[var_name]['value'] = new_value
        else:
            print 'variable assigned a value of wrong type'
            sys.exit(1)
    elif parent_env is not None:
        env_update(parent_env, var_name, new_value)
    else:
        print 'var does not exist or out of scope so not updated'
        sys.exit(1)

def env_update_list(environment, array_name, index_pos, new_value):
    parent_env = environment[0]
    scoped_var_dict = environment[1]
    if array_name in scoped_var_dict:
        if isinstance(new_value, j_to_p_type[scoped_var_dict[array_name]['type']]):
            scoped_var_dict[array_name]['value'][index_pos] = new_value
        else:
            print 'variable assigned a value of wrong type'
            sys.exit(1)
    elif parent_env is not None:
        env_update_list(parent_env, array_name, index_pos, new_value)
    else:
        print 'var does not exist or out of scope so not updated'
        sys.exit(1)

def env_add(environment, var_type, var_name, init_value=None):
    scoped_var_dict = environment[1]
    scoped_var_dict[var_name] = {}
    if var_type == 'char' and init_value:
        if len(init_value) == 1:
            scoped_var_dict[var_name]['type'] = var_type
            scoped_var_dict[var_name]['value'] = str(init_value)
        else:
            print 'char type can not be assigned a string'
            sys.exit(1)
    else:
        scoped_var_dict[var_name]['type'] = var_type
        if init_value is None:
            scoped_var_dict[var_name]['value'] = init_value
        elif isinstance(init_value, j_to_p_type[scoped_var_dict[var_name]['type']]):
            # type_cast = j_to_p_type[scoped_var_dict[var_name]['type']]
            scoped_var_dict[var_name]['value'] = init_value
        else:
            print 'variable initialized with a value of wrong type'
            sys.exit(1)

def env_add_func(environment, func_return_type, func_name, params, statements):
    func_dict = environment[1]
    func_dict[func_name] = {
        'return_type': func_return_type,
        'params': params,
        'statements': statements
    }

def env_add_list(environment, var_type, var_name, list_size=0):
    scoped_var_dict = environment[1]
    scoped_var_dict[var_name] = {}
    scoped_var_dict[var_name]['type'] = var_type
    scoped_var_dict[var_name]['value'] = [None] * list_size

def eval_exp(tree, environment=None):
    node_type = tree[0]
    node_value = tree[1]
    if node_type == 'int':
        return int(node_value)
    elif node_type == 'double':
        return float(node_value)
    elif node_type in ['char', 'String']:
        return node_value
    elif node_type == 'boolean':
        return bool(node_value)
    elif node_type == 'identifier':
        var_object = env_lookup(environment, node_value)
        if var_object is not None and var_object['value'] is not None:
            return eval_exp((var_object['type'], var_object['value']))
        else:
            print 'trying to read uninitialized variable'
            sys.exit(1)
    elif node_type == 'identifier_array':
        index_exp = tree[2]
        if not isinstance(index_exp, int):
            index_var = env_lookup(environment, index_exp)
            if index_var is not None and index_var['value'] is not None:
                index_pos = eval_exp((index_var['type'], index_var['value']), environment)
        else:
            index_pos = index_exp
        array_object = env_lookup_list(environment, node_value, index_pos)
        if array_object is not None and array_object['value'][index_pos] is not None:
            return eval_exp((array_object['type'], array_object['value'][index_pos]))
        else:
            print 'unbounded access of an array'
            sys.exit(1)
    elif node_type == 'unaryop':
        operator = tree[1]
        right_child = tree[2]
        right_var = env_lookup(environment, right_child)
        if right_var is not None and right_var['value'] is not None:
            right_value = eval_exp((right_var['type'], right_var['value']))
        else:
            print 'invalid unary operator'
            sys.exit(1)
        if operator == '++':
            new_value = right_value + 1
        elif operator == '--':
            new_value = right_value - 1
        env_update(environment, right_child, new_value)
        return new_value
    elif node_type == 'binop':
        left_child = tree[1]
        operator = tree[2]
        right_child = tree[3]
        left_val = eval_exp(left_child, environment)
        right_val = eval_exp(right_child, environment)
        if operator == '+' and isinstance(left_val, (int, float, str)) and isinstance(right_val, (int, float, str)):
            if isinstance(left_val, str):
                return left_val + str(right_val)
            elif isinstance(right_val, str):
                return str(left_val) + right_val
            else:
                return left_val + right_val
        elif operator == '-' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val - right_val
        elif operator == '*' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val * right_val
        elif operator == '/' and right_val and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val / right_val
        elif operator == '%' and right_val and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val % right_val
        elif operator == '<' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val < right_val
        elif operator == '<=' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val <= right_val
        elif operator == '>' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val > right_val
        elif operator == '>=' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val >= right_val
        elif operator == '==' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val == right_val
        elif operator == '!=' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val != right_val
        elif operator == '==' and isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val == right_val
        else:
            print 'invalid binary operation attempted'
            sys.exit(1)
    elif node_type == 'call':
        func_name = tree[1]
        args = tree[2]
        func_object = env_lookup(environment, func_name)
        if func_object is not None:
            func_environment = (environment, {}, func_name)
            if func_name != 'main':
                for index, p in enumerate(func_object['params']):
                    if args[index][0] == 'identifier':
                        var_object = env_lookup(environment, args[index][1])
                        if var_object is not None:
                            env_add(func_environment, p[0], p[1], var_object['value'])
                        else:
                            print 'variable argument not resolved'
                            sys.exit(1)
                    elif args[index][0] == 'identifier_array':
                        array_object = env_lookup(environment, args[index][1])
                    elif args[index][0] == 'binop':
                        exp_arg = eval_exp(args[index], environment)
                        if exp_arg is not None:
                            env_add(func_environment, p[0], p[1], exp_arg)
                        else:
                            print 'incorrect expression argument'
                            sys.exit(1)
                    else:
                        env_add(func_environment, p[0], p[1], args[index][1])
            func_statements = func_object['statements']
            for fs in func_statements:
                eval_statement(fs, func_environment)
            # print '\nfunction ', func_name, ' environment: ', func_environment
            if return_var is not None:
                return return_var
    else:
        print 'invalid expression'
        sys.exit(1)

def eval_statement(tree, environment):
    statement_type = tree[0]
    if statement_type == 'decl_var':
        var_type = tree[1]
        var_name = tree[2]
        env_add(environment, var_type, var_name)
    elif statement_type == 'decl_init_var':
        var_type = tree[1]
        var_name = tree[2]
        exp_tree = tree[3]
        init_value = eval_exp(exp_tree, environment)
        env_add(environment, var_type, var_name, init_value)
    elif statement_type == 'assign':
        var_name = tree[1]
        exp_tree = tree[2]
        new_value = eval_exp(exp_tree, environment)
        if new_value is not None:
            env_update(environment, var_name, new_value)
        else:
            print 'invalid assignment statement'
            sys.exit(1)
    elif statement_type == 'decl_array':
        array_type = tree[1]
        array_name = tree[2]
        array_size = tree[3]
        env_add_list(environment, array_type, array_name, array_size)
    elif statement_type == 'assign_array':
        array_name = tree[1]
        index_exp = tree[2]
        if not isinstance(index_exp, int):
            index_var = env_lookup(environment, index_exp)
            if index_var is not None and index_var['value'] is not None:
                index_pos = eval_exp((index_var['type'], index_var['value']), environment)
        else:
            index_pos = index_exp
        exp_tree = tree[3]
        new_value = eval_exp(exp_tree, environment)
        if new_value is not None:
            env_update_list(environment, array_name, index_pos, new_value)
    elif statement_type == 'if-then':
        exp_tree = tree[1]
        statements = tree[2]
        if eval_exp(exp_tree, environment):
            for s in statements:
                eval_statement(s, environment)
    elif statement_type == 'if-then-else':
        exp_tree = tree[1]
        if_statements = tree[2]
        else_statements = tree[3]
        if eval_exp(exp_tree, environment):
            if not isinstance(if_statements, list):
                eval_statement(if_statements, environment)
            else:
                for s in if_statements:
                    eval_statement(s, environment)
        else:
            if not isinstance(else_statements, list):
                eval_statement(else_statements, environment)
            else:
                for s in else_statements:
                    eval_statement(s, environment)
    elif statement_type == 'exp':
        exp_tree = tree[1]
        eval_exp(exp_tree, environment)
    elif statement_type == 'return':
        exp_tree = tree[1]
        return_value = eval_exp(exp_tree, environment)
        if environment[2] is not None:
            returned_func_name = environment[2]
            returned_func_obj = env_lookup(environment, returned_func_name)
            if isinstance(return_value, j_to_p_type[returned_func_obj['return_type']]):
                global return_var
                return_var = return_value
            else:
                print 'function return type does not match with returned value'
                sys.exit(1)
        else:
            print 'invalid return statement'
            sys.exit(1)
    elif statement_type == 'print':
        exp = tree[1]
        evaled_exp = eval_exp(exp, environment)
        if evaled_exp is not None:
            print evaled_exp
    elif statement_type == 'for_loop':
        iterator = tree[1]
        increment_cond = tree[2]
        increment = tree[3]
        block_stmts = tree[4]
        if iterator is not None:
            eval_statement(iterator, environment)
        while(1):
            if increment_cond is not None:
                if eval_exp(increment_cond, environment):
                    for b in block_stmts:
                        eval_statement(b, environment)
                    eval_exp(increment, environment)
                else:
                    break

def save_function(tree, environment):
    return_type = tree[1]
    func_name = tree[2]
    params = tree[3]
    statements = tree[4]
    env_add_func(environment, return_type, func_name, params, statements)

def eval_statements_and_call_main(tree, environment):
    global class_name
    class_name = tree[1]
    elements = tree[2]
    for e in elements:
        if e[0] == 'statement':
            eval_statement(e[1], environment)
        elif e[0] == 'function':
            save_function(e, environment)
    eval_exp(('call', 'main', []), global_environment)


javaLexer = lex.lex()
javaParser = yacc.yacc()
inputString = '''public class Fib {
                    public int fib(int n) {
                        if (n<=1) {
                            return n;
                        } else {
                            return fib(n - 1) + fib(n - 2);
                        }
                    }

                    public static void main(String[] args) {
                        int[] arr = new int[1000];
                        int numF = 10*(5+8);
                        for (int i=0; i<numF; ++i) {
                            int ans = fib(i);
                            arr[i] = ans;
                            System.out.println("The " + i + "th Fibonacci number is " +  arr[i]);
                        }
                    }
                }
                '''

                # '''int r = 4;
                # public int fib(int n){
                #     if(n<=1) {return n;}
                #     else {
                #         n = n - 1;
                #         int a = fib(n);
                #         n = n - 1;
                #         int b = fib(n);
                #         return a+b;
                #     }
                # }
                # int p = fib(r);
                # double q = 10.0;
                # System.out.println(--p);
                # for(int i=0; i<10; ++i){
                #     System.out.println("hello");
                # }
                # int[] myarr = new int[5];
                # myarr[r] = 2;
                # System.out.println(myarr[r] + " is");
                # '''

parseTree = javaParser.parse(inputString, javaLexer)
# print '\nparse tree: ', parseTree

for t in parseTree:
    if t[0] == 'class':
        eval_statements_and_call_main(t, global_environment)

# print '\nglobal environment: ', global_environment, '\n'