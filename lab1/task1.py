import os
from typing import List


class Constructor:
    def __init__(self, letter, arity):
        self.letter = letter
        self.arity = arity


class Variable:
    def __init__(self, letter):
        self.letter = letter


class Term:
    def __init__(self, entity, terms=None):
        self.terms = terms
        self.entity = entity

    def to_string(self):
        if self.entity.__class__ == Variable:
            return self.entity.letter
        else:
            if self.entity.arity == 0:
                return self.entity.letter
            else:
                string = f"{self.entity.letter}("
                i = 0
                for term in self.terms:
                    string += term.to_string()
                    if i + 1 < len(self.terms):
                        string += ","
                    i += 1
                return string + ")"


def get_parsing_pos(line):
    return line.find(" = ") + 3


def parse_constructors(line):
    constructors = []
    constructors_str = [word.strip() for word in line[get_parsing_pos(line):].split(",")]
    for constructor_str in constructors_str:
        lbracket_pos = constructor_str.find("(")
        constructors.append(Constructor(constructor_str[:lbracket_pos], int(constructor_str[lbracket_pos + 1:-1])))

    return constructors


def parse_variables(line):
    variables = []
    vars_str = [word.strip() for word in line[get_parsing_pos(line):].split(",")]
    for var_str in vars_str:
        variables.append(Variable(var_str))

    return variables


def get_entity(letter, constructors: List[Constructor], variables: List[Variable]):
    for c in constructors:
        if letter == c.letter:
            return c
    for v in variables:
        if letter == v.letter:
            return v
    return -1


def find_close_bracket(line):
    line = line[line.find("("):]
    b = 0
    i = 0
    for c in line:
        if c == "(":
            b += 1
        elif c == ")":
            b -= 1
        if b == 0:
            return i + 1
        i += 1


def parse_term(line: str, constructors, variables):
    if line == "":
        return

    letter = line[0]

    e = get_entity(letter, constructors, variables)
    if e.__class__ == Constructor:
        args = []
        args_str = line[line.find("(") + 1:line.rfind(")")]
        i = 0
        while i < len(args_str):
            c = args_str[i]
            if c.isalpha():
                if i + 1 == len(args_str):
                    args.append(c)
                    i += 1
                elif args_str[i + 1] == "(":
                    i1 = i + 1 + find_close_bracket(args_str[i:])
                    args.append(args_str[i:i1])
                    i = i1
                else:
                    args.append(c)
                    i += 1
            else:
                i += 1
        return Term(e, [parse_term(arg, constructors, variables) for arg in args] if e.arity != 0 else None)
    elif e.__class__ == Variable:
        return Term(e)
    else:
        pass


def read_input(path):
    with open(path, "r") as input_file:
        constructors = parse_constructors(input_file.readline())
        variables = parse_variables(input_file.readline())

        term1 = input_file.readline()
        term1 = term1[get_parsing_pos(term1):]
        term1 = parse_term(term1, constructors, variables)
        term2 = input_file.readline()
        term2 = term2[get_parsing_pos(term2):]
        term2 = parse_term(term2, constructors, variables)
        return variables, constructors, term1, term2


def get_right_part(p, left_part):
    rules = p.split('\n')
    for rule in rules:
        if rule[:rule.find(':=')].strip() == left_part:
            return rule[rule.find(':=') + 2:].strip()
    return False


def get_left_part(p, right_part):
    rules = p.split('\n')
    for rule in rules:
        if rule[rule.find(':=') + 2:].strip() == right_part:
            return rule[:rule.find(':=')].strip().strip()
    return False


def get_unificating_term(p, var: Term):
    r = get_right_part(p, var.to_string())
    l = get_left_part(p, var.to_string())
    return r or l


def unificate(t1: Term, t2: Term, p: str):
    if t1.entity.__class__ == Variable:
        if t2.entity.__class__ == Variable:
            if t1.entity.letter == t2.entity.letter:
                return p, t1
            t11 = get_unificating_term(p, t1)
            t12 = get_unificating_term(p, t2)
            if not t11 and not t12:
                return p + f"{t1.to_string()} := {t2.to_string()}\n", t2
            elif t11 == t2.to_string():
                return p, t2
            else:
                return False, None
        else:
            t11 = get_unificating_term(p, t1)
            if not t11:
                return p + f"{t1.to_string()} := {t2.to_string()}\n", t2
            elif t11 == t2.to_string():
                return p, t2
            else:
                return False, None
    else:
        if t2.entity.__class__ == Variable:
            t12 = get_unificating_term(p, t2)
            if not t12:
                return p + f"{t2.to_string()} := {t1.to_string()}\n", t1
            elif t12 == t1.to_string():
                return p, t1
            else:
                return False, None
        else:
            if t1.entity.letter != t2.entity.letter or t1.entity.arity != t2.entity.arity:
                return False, None
            else:
                if t1.entity.arity == 0:
                    return p, t1
                u = Term(t1.entity, [])
                for i in range(0, len(t1.terms)):
                    p, u1 = unificate(t1.terms[i], t2.terms[i], p)
                    if p == False:
                        return False, None
                    u.terms.append(u1)

            return p, u


def check_tests(dir_path):
    tests = os.listdir(dir_path)
    for test in tests:
        v, c, t1, t2 = read_input(f"{dir_path}/{test}")
        print(f"NAME = {test}")
        print('\n')
        with open(f"{dir_path}/{test}") as input:
            for line in input.readlines():
                print(line, end='')
        print('\n')
        p, u = unificate(t1, t2, "")
        if p == False:
            print("Невозможно унифицировать")
        else:
            print(u.to_string())
            print(p)
        print("===============")


if __name__ == '__main__':
    check_tests("./test")
