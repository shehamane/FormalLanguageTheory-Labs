import os
import re
import copy


class Equation:
    def __init__(self, var_name, a, b):
        self.var_name = var_name
        self.a = a
        self.b = b


class Substitution:
    def __init__(self, name, alpha, beta, free):
        self.name = name
        self.alpha = alpha
        self.beta = beta
        self.free = free


equation_regex = re.compile(
    '([A-Z])\s*=\s*(?:((?:[a-z]+|\([a-z]+(?:\|[a-z]+)+\))[A-Z](?:\s*\+\s*(?:[a-z]+|\([a-z]+(?:\|[a-z]+)+\))[A-Z])*)\s*\+\s*)?([a-z]+|\([a-z]+(\|[a-z]+)+\))\n?$')

var_regex = re.compile('[A-Z]')


def read_input(path):
    equations = []
    defined_vars = []
    all_vars = []
    with open(path, 'r') as input:
        for equation_str in input.readlines():
            equation_str = equation_str.strip()
            if not equation_regex.match(equation_str):
                return False
            defined_vars.append(equation_str.split('=')[0].replace(' ', ''))
            all_vars.append(var_regex.findall(equation_str.split('=')[1]))

            name = equation_str.split('=')[0].replace(' ', '')
            vars = var_regex.findall(equation_str.split('=')[1].replace(' ', ''))
            coeffs = var_regex.split(equation_str.split('=')[1].replace(' ', ''))
            for i in range(1, len(coeffs)):
                coeffs[i] = coeffs[i][1:]
            equations.append(Equation(name, dict(zip(vars, coeffs[:-1])), coeffs[-1]))

        for vars in all_vars:
            for var in vars:
                if not var in defined_vars:
                    return False
        return equations


def get_substitution(e: Equation):
    if e.var_name in e.a:
        alpha = e.a[e.var_name]
    else:
        alpha = False
    beta = copy.deepcopy(e.a)
    if e.var_name in e.a:
        beta.pop(e.var_name)
    return Substitution(e.var_name, alpha, beta, e.b)


def substitute(e: Equation, s: Substitution):
    for var in s.beta:
        if var in e.a:
            if e.a[var] == '(':
                e.a[var] = e.a[var][1: -1]
            e.a[var] += ' + ' + e.a[s.name] + (s.alpha + '*' if s.alpha else "") + s.beta[var]
            e.a[var] = f'({e.a[var]})'
        else:
            e.a[var] = '(' + e.a[s.name] + (s.alpha + '*' if s.alpha else "") + s.beta[var] + ')'
    if s.free:
        if e.b and e.b[0] == '(':
            e.b = e.b[1:-1]
        e.b += (" + " if e.b else '') + e.a[s.name] + (s.alpha + '*' if s.alpha else "") + s.free
        e.b = f'({e.b})'
    e.a.pop(s.name)
    return e


def solve_system(equations: [Equation]):
    for i in range(0, len(equations)):
        e = equations[i]
        substitution = get_substitution(e)
        for j in range(i + 1, len(equations)):
            ej = equations[j]
            if e.var_name in ej.a:
                ej = substitute(ej, substitution)
    for i in range(len(equations) - 1, -1, -1):
        e = equations[i]
        substitution = get_substitution(e)
        for j in range(i - 1, -1, -1):
            ej = equations[j]
            if e.var_name in ej.a:
                ej = substitute(ej, substitution)


def check_tests(dir_path):
    tests = os.listdir(dir_path)
    for test in tests:
        equations = read_input(f"{dir_path}/{test}")
        print(f"NAME = {test}")
        print('\n')
        if not equations:
            print("Система некорректна")
        else:
            solve_system(equations)
            for e in equations:
                s = get_substitution(e)
                if s.alpha:
                    print(f'{s.name} = {s.alpha}*{s.free}')
                else:
                    print(f'{s.name} = {s.free}')
        print("===============")


if __name__ == '__main__':
    check_tests('./tests')
