#!/usr/bin/python3

"""
MBA expression generation including linear, polynomial, non-polynomial.
"""

import sys
sys.path.append("../tools")
import z3
import ast
from ast import Expression
from ast import BinOp, UnaryOp, Name, Constant, USub, Mult, Load, BitAnd, Sub, Add, BitXor, Invert, BitOr




from lMBA_generate import complex_groundtruth
from mba_string_operation import verify_mba_unsat
from pMBA_generate import groundtruth_2_pmba
from nonpMBA_generate import add_zero, recursively_apply, replace_sub_expre, replace_one_variable

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Constant:
    def __init__(self, value):
        self.value = value

class Name:
    def __init__(self, id, ctx):
        self.id = id
        self.ctx = ctx

class Mult:
    def __str__(self):
        return "MUL"

class Add:
    def __str__(self):
        return "ADD"

class Sub:
    def __str__(self):
        return "SUB"

class BitAnd:
    def __str__(self):
        return "AND"

class BitOr:
    def __str__(self):
        return "OR"

class BitXor:
    def __str__(self):
        return "XOR"

class Invert:
    def __str__(self):
        return "NOT"

def translate_to_asm(node):
    # Функция для генерации ассемблерного кода из AST
    if isinstance(node, BinOp):
        left_asm = translate_to_asm(node.left)
        right_asm = translate_to_asm(node.right)
        op_asm = str(node.op)
        if op_asm == "ADD":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nadd rax, rbx"
        elif op_asm == "SUB":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nsub rax, rbx"
        elif op_asm == "MUL":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nimul rbx"
        elif op_asm == "AND":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nand rax, rbx"
        elif op_asm == "OR":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nor rax, rbx"
        elif op_asm == "XOR":
            return f"{right_asm}\npush rax\n{left_asm}\npop rbx\nxor rax, rbx"
    elif isinstance(node, UnaryOp):
        operand_asm = translate_to_asm(node.operand)
        op_asm = str(node.op)
        if op_asm == "NOT":
            return f"{operand_asm}\nnot rax"
    elif isinstance(node, Constant):
        return f"mov rax, {node.value}"
    elif isinstance(node, Name):
        return f"mov rax, {node.id}"


def generate_ast_from_expression(expression):
    """Generate AST from a given MBA expression."""
    return ast.parse(expression, mode='eval')

def process_ast_file(input_file, output_file):
    # Чтение AST из файла
    with open(input_file, 'r') as f:
        ast_strings = f.readlines()

    # Открытие файла для записи ассемблерного кода
    with open(output_file, 'w') as f:
        # Обработка каждой строки AST
        for ast_string in ast_strings:
            # Преобразование строки AST в объект AST
            ast_tree = ast.parse(ast_string)
            # Генерация ассемблерного кода из AST
            asm_code = translate_to_asm(ast_tree.body)
            # Запись ассемблерного кода в файл
            f.write(asm_code + '\n')

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
        
        # Разделение строки на отдельные выражения
        expressions = sexpre.split(" ")
        for expression in expressions:
            # Удаление части "x+y"
            expression = expression.replace("x+y ", "")
            # Генерация AST для оставшегося выражения
            ast_tree = generate_ast_from_expression(expression)
            # Запись AST в файл
            with open("res_AST.txt", "a") as ast_file:
                ast_file.write(ast.dump(ast_tree) + "\n")


    else:
        print("Sorry, the program output a wrong expression!")

    return cexpre




def unittest():
        sexpre = "x+y"


        with open("res_of_obf.txt", "w") as f:
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'l')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'p')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_zero')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_recur')}\n")
            f.write(f"{sexpre}, {mba_obfuscator(sexpre, 'np_replace')}\n")


        # Чтение строк из файла
        with open('res_of_obf.txt', 'r') as file:
            expressions = file.readlines()

        # Открытие файла для записи AST
        with open('res_AST.txt', 'w') as output_file:
            # Обработка каждого выражения после запятой
            for expression in expressions:
                # Разделение строки по запятой и взятие второй части
                expression_parts = expression.split(',')
            
                expression_after_comma = expression_parts[1].strip()
                print(expression_after_comma)
                # Генерация AST для выражения
                ast_tree = generate_ast_from_expression(expression_after_comma)

                # Запись AST в файл
                output_file.write(ast.dump(ast_tree) + '\n')

                    
                #print(ast.dump(ast_tree))

        process_ast_file('res_AST.txt', 'res_AST_assembl.txt')





if __name__ == "__main__":
    unittest()
#рабоотает




'''''
# Открываем файл для записи
with open("res_of_obf.txt", "w") as f:
    # Перенаправляем стандартный поток вывода в файл
    sys.stdout = f

    def unittest():
        sexpre = "x+y"

        print(sexpre, mba_obfuscator(sexpre, "l"))
        print(sexpre, mba_obfuscator(sexpre, "p"))
        print(sexpre, mba_obfuscator(sexpre, "np_zero"))
        print(sexpre, mba_obfuscator(sexpre, "np_recur"))
        print(sexpre, mba_obfuscator(sexpre, "np_replace"))

    if __name__ == "__main__":
        unittest()
        '''