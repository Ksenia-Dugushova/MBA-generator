#!/usr/bin/python3

"""
MBA expression generation including linear, polynomial, non-polynomial.
"""

import sys
sys.path.append("../tools")
import z3
import ast
from ast import Expression
from ast import AST, parse, Expression, BinOp, Compare, BoolOp, Call,  Attribute,  Constant, Mult, BitAnd, Load, UnaryOp, Name, BitXor, Sub, BitOr, Invert, Add, USub, UAdd, iter_fields
import subprocess
import os
from lMBA_generate import complex_groundtruth
from mba_string_operation import verify_mba_unsat
from pMBA_generate import groundtruth_2_pmba
from nonpMBA_generate import add_zero, recursively_apply, replace_sub_expre, replace_one_variable




def generate_ast_from_expression(expression):
    """Generate AST from a given MBA expression."""
    return ast.parse(expression, mode='eval')



def mba_obfuscator(sexpre, flag="l"):
    """MBA expression generation..
    Args:
        sexpre: a simple expression.
        flag: transformation choice, must in ["l", "p", "np"].
    Returns:
        cexpre: the related complex MBA expression.
    """
       
    if flag not in ["l", "p", "np_zero", "np_recur", "np_replace"]:
        print("flag wrong! pleaxe input l or p or np")
        return None

    testall = True
    if flag == "l":
        cexpre = complex_groundtruth(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        if not z3res:
            testall = False
    elif flag == "p":
        cexpre = groundtruth_2_pmba(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        if not z3res:
            testall = False
    elif flag == "np_zero":
        cexpre = add_zero(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        if not z3res:
            testall = False
    elif flag == "np_recur":
        cexpre = recursively_apply(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        if not z3res:
            testall = False
    elif flag == "np_replace":
        cexpre = replace_sub_expre(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        if not z3res:
            testall = False

    if testall:
        pass
        #pass verification.
    else:
        print("sorry, program output a wrong expression!")


    return cexpre

'''
    if testall:
        
        # Разделение строки на отдельные выражения
        expressions = sexpre.split(" ")
        for expression in expressions:
            # Удаление части "x+y"
            expression = expression.replace("x+y ", "")
            # Генерация AST для оставшегося выражения
            ast_tree = generate_ast_from_expression(expression)
            with open("res_AST.txt", "a") as ast_file:
                ast_file.write(ast.dump(ast_tree) + "\n")



    else:
        print("Sorry, the program output a wrong expression!")

    return cexpre

'''



def unittest():
        sexpre = "x+y"


        with open("res_of_obf.txt", "w") as f:
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'l')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'l')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'l')}\n")
            #f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'p')}\n")
            #f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_zero')}\n")
            #f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_recur')}\n")
            #f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_replace')}\n")

        # Открываем файл с результатами обфускации
        with open("res_of_obf.txt", "r") as f:
            # Читаем каждую строку
            for i, line in enumerate(f, start=1):
                # Разделяем строку на два выражения
                expression, obfuscated_result = line.strip().split(", ")
                with open(f"res{i}_in_progr.c", "w") as output_file:
                    output_file.write('''int test(int x, int y) {return ''')
                        # Записываем обфусцированный результат
                    output_file.write(obfuscated_result)
                    output_file.write(';\n\n')
                    output_file.write('}')

                

def generate_asm_files():
        parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        for i in range (1,4):
                c_filename = os.path.join(parent_directory, f"mba_obfuscator\\res{i}_in_progr.c")
                #c_filename = os.path.join(parent_directory, f"mba_obfuscator\\res_in_progr.c")
                print(f"{i} ASM")
                #asm_filename = os.path.join(parent_directory, f"mba_obfuscator\\res{i}_in_asm.s")
                #subprocess.run(["clang","-O0", "-S", "-o", "-", c_filename ])
               
                process = subprocess.Popen(["clang", "-O0", "-S", "-o", "-", c_filename], stdout=subprocess.PIPE)
                output, _ = process.communicate()  # Захватываем stdout
                
                # Декодируем двоичный вывод в строку
                asm_code = output.decode("utf-8")
                
                # Извлекаем инструкции между movl (включительно) и popq (исключительно)
                start_index = asm_code.find("movl")
                end_index = asm_code.find("popq", start_index)
                if start_index != -1 and end_index != -1:
                    extracted_asm = asm_code[start_index:end_index]
                    # Убираем отступы из каждой строки
                    extracted_asm = '\n'.join(line.strip() for line in extracted_asm.split('\n'))
                    print(extracted_asm)
'''
        with open('res_of_obf.txt', 'r') as file:
            expressions = file.readlines()

        with open('res_AST.txt', 'w') as output_file:
            for expression in expressions:
                expression_parts = expression.split(',')
            
                expression_after_comma = expression_parts[1].strip()
                print(expression_after_comma)
                ast_tree = generate_ast_from_expression(expression_after_comma)

                output_file.write(ast.dump(ast_tree) + '\n')

                    
                #print(ast.dump(ast_tree))
                

#we left the idea with AST


tmp = Expression(body=BinOp(left=BinOp(left=BinOp(left=BinOp(left=BinOp(left=BinOp(left=BinOp(left=BinOp(left=UnaryOp(op=USub(), operand=Constant(value=2)), op=Mult(), right=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitAnd(), right=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load())))))), op=Sub(), right=BinOp(left=Constant(value=1), op=Mult(), right=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitAnd(), right=UnaryOp(op=Invert(), operand=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load())))))))), op=Add(), right=BinOp(left=Constant(value=2), op=Mult(), right=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitXor(), right=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load()))))))), op=Add(), right=BinOp(left=Constant(value=4), op=Mult(), right=UnaryOp(op=Invert(), operand=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitAnd(), right=UnaryOp(op=Invert(), operand=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load()))))))))), op=Sub(), right=BinOp(left=Constant(value=4), op=Mult(), right=UnaryOp(op=Invert(), operand=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitOr(), right=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load())))))))), op=Sub(), right=BinOp(left=Constant(value=5), op=Mult(), right=UnaryOp(op=Invert(), operand=BinOp(left=BinOp(left=Constant(value=4), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=Name(id='y', ctx=Load()))), op=BitOr(), right=UnaryOp(op=Invert(), operand=BinOp(left=UnaryOp(op=UAdd(), operand=Constant(value=3)), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitAnd(), right=UnaryOp(op=Invert(), operand=Name(id='y', ctx=Load()))))))))), op=Add(), right=BinOp(left=Constant(value=1), op=Mult(), right=BinOp(left=Name(id='x', ctx=Load()), op=BitOr(), right=Name(id='y', ctx=Load())))), op=Sub(), right=BinOp(left=Constant(value=3), op=Mult(), right=Name(id='x', ctx=Load()))))
def str_node(node):
    if isinstance(node, AST):
        fields = [(name, str_node(val)) for name, val in iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)

def ast_visit(node, level=0):
    print('  ' * level + str_node(node))
    for field, value in iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, AST):
                    ast_visit(item, level=level+1)
        elif isinstance(value, AST):
            ast_visit(value, level=level+1)

ast_visit(tmp)
'''
if __name__ == "__main__":
    unittest()
    generate_asm_files()
#рабоотает




'''''
# Открываем файл для записи
with open("res_of_obf.txt", "w") as f:
    # Перенаправляем стандартный поток вывода в файл
    sys.stdout = f

    def unittest():
        sexpre = "x+y"

        print(sexpre, mba_obfuscator(sexpre, "l"))
        #print(sexpre, mba_obfuscator(sexpre, "p"))
        #print(sexpre, mba_obfuscator(sexpre, "np_zero"))
        #print(sexpre, mba_obfuscator(sexpre, "np_recur"))
        #print(sexpre, mba_obfuscator(sexpre, "np_replace"))

    if __name__ == "__main__":
        unittest()
        '''