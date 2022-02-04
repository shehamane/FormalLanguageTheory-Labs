import os
import re
import graphviz


class Transition:
    def __init__(self, state_f, letter, stack_s, state_t, stack_s_new):
        self.state_f = state_f
        self.letter = letter
        self.stack_s = stack_s
        self.state_t = state_t
        self.stack_s_new = stack_s_new


class PDA:
    def get_unique_states(self):
        states = []
        stack_symbols = []
        for t in self.transitions:
            if t.state_f not in states:
                states.append(t.state_f)
            if t.state_t not in states:
                states.append(t.state_t)
            if t.stack_s not in stack_symbols:
                stack_symbols.append(t.stack_s)
            for symbol in t.stack_s_new:
                if symbol not in stack_symbols:
                    stack_symbols.append(symbol)
        return states, stack_symbols

    def __init__(self, start, bottom, transitions):
        self.start = start
        self.bottom = bottom
        self.transitions = transitions
        self.states, self.stack_symbols = self.get_unique_states()

    def create_graph(self, path):
        dot = graphviz.Digraph(comment='Stack Automate')
        for state in self.states:
            dot.node(state, label=state)
        for t in self.transitions:
            dot.edge(t.state_f, t.state_t, label=f'{t.letter}, {t.stack_s}/{t.stack_s_new}')
        dot.render(path)


def read_PDA(path):
    with open(path, 'r') as input_file:
        first_line = input_file.readline()
        start = re.findall('[q-u][0-9]?', first_line)[0]
        bottom = re.findall('[A-Z][0-9]?', first_line)[0]
        transitions_lines = input_file.read().split('\n')
        transitions = []

        for t_line in transitions_lines:
            t1, t2 = t_line.split('->')
            t1 = t1[1:-1]
            t2 = t2[1:-1]
            state_f, letter, stack_s = t1.split(',')
            state_t, stack_s_new = t2.split(',')
            transitions.append(Transition(state_f, letter, stack_s, state_t, stack_s_new))
        return PDA(start, bottom, transitions)


class CFG:
    def __init__(self, N, rules, start):
        self.names_map = None
        self.non_terms = N
        self.rules = rules
        self.start = start


class Rule:
    def __init__(self, f, t):
        self.fr = f
        self.to = t

    def toString(self, names):
        fr_string = names[self.fr.to_string() if type(self.fr) == Triple else self.fr]
        to_string = ''
        for i in self.to:
            if type(i) == str:
                to_string += i
            else:
                to_string += names[i.to_string()]
        return fr_string + ' -> ' + to_string


class Triple:
    def __init__(self, p, x, q):
        self.p = p
        self.x = x
        self.q = q

    def to_string(self):
        return str(self.p) + str(self.x) + str(self.q)


def get_non_terminals(pda):
    non_terminals = []
    for p in pda.states:
        for A in pda.stack_symbols:
            for q in pda.states:
                non_terminals.append(Triple(p, A, q))
    return non_terminals + ['S']


def permute(n, m):
    a = [0 for i in range(n if n > m else m)]
    yield a[:m]

    while True:
        j = m - 1
        while j >= 0 and a[j] == n - 1:
            j -= 1
        if j < 0:
            return
        if a[j] >= n - 1:
            j -= 1
        a[j] += 1
        if j == m - 1:
            yield a[:m]
        else:
            for k in range(j + 1, m):
                a[k] = 0
            yield a[:m]


def get_rules(pda):
    rules = []
    for p in pda.states:
        rules.append(Rule('S', [Triple(pda.start, pda.bottom, p)]))
    for t in pda.transitions:
        if t.stack_s_new == '':
            r_from = Triple(t.state_f, t.stack_s, t.state_t)
            rules.append(Rule(r_from, [t.letter]))
        else:
            permutations = permute(len(pda.states), len(t.stack_s_new))
            for idx, permutation in enumerate(permutations):
                r_from = Triple(t.state_f, t.stack_s, pda.states[permutation[-1]])
                r_to = [t.letter, Triple(t.state_t, t.stack_s_new[0], pda.states[permutation[0]])]
                for i, index in enumerate(permutation):
                    if i == 0:
                        continue
                    r_to.append(Triple(pda.states[permutation[i - 1]],
                                       t.stack_s_new[i],
                                       pda.states[index]))
                rules.append(Rule(r_from, r_to))
    return rules


def PDA_to_CFG(pda):
    non_terms = get_non_terminals(pda)
    rules = get_rules(pda)
    return CFG(non_terms, rules, 'S')


def contains(x, arr):
    if type(x) == str:
        return x in arr

    for t in arr:
        if type(t) == Triple and x.q == t.q and x.p == t.p and x.x == t.x:
            return True
    return False


def get_effective_nvars(cfg):
    effective_vars = []
    for rule in cfg.rules:
        flag = True
        for i in rule.to:
            if type(i) == Triple:
                flag = False
        if flag and not contains(rule.fr, effective_vars):
            effective_vars.append(rule.fr)
    flag = True
    while flag:
        flag = False
        for rule in cfg.rules:
            flag1 = True
            for i in rule.to:
                if type(i) == Triple and not contains(i, effective_vars):
                    flag1 = False
            if flag1 and not contains(rule.fr, effective_vars):
                effective_vars.append(rule.fr)
                flag = True
    return effective_vars


def get_attainable_nvars(cfg):
    attainable = ['S']
    flag = True
    while flag:
        flag = False
        for rule in cfg.rules:
            if contains(rule.fr, attainable):
                for i in rule.to:
                    if contains(i, cfg.non_terms) and \
                            not contains(i, attainable) and (type(i) == Triple or i == "S"):
                        attainable.append(i)
                        flag = True
    return attainable


def intersect(l, r):
    ans = []
    for i in l:
        if contains(i, r):
            ans.append(i)
    return ans

def clean(cfg):
    w_flag = True

    while w_flag:
        w_flag = False

        att = get_attainable_nvars(cfg)
        eff = get_effective_nvars(cfg)
        cfg.non_terms = intersect(att, eff)

        rules = []
        for rule in cfg.rules:
            flag = True
            for right in rule.to:
                if type(right) == Triple and not contains(right, cfg.non_terms):
                    flag = False
            if flag and contains(rule.fr, cfg.non_terms):
                rules.append(rule)

        if rules != cfg.rules:
            w_flag = True
        cfg.rules = rules

    return cfg


def gen_name():
    for i in range(65, 91):
        for j in range(0, 10):
            yield chr(i) + str(j)


def rename(cfg):
    name_gen = gen_name()
    cfg.names_map = {}
    for var in cfg.non_terms:
        key = var.to_string() if type(var) == Triple else var
        cfg.names_map[key] = name_gen.__next__()
    cfg.names_map['S'] = 'S'


def check_tests(dir_path):
    tests = os.listdir(dir_path)
    for test in tests:
        print(f'==========={test}==========')
        pda = read_PDA(f'{dir_path}/{test}')
        pda.create_graph(f'graphs/{test[:-4]}.gv')
        cfg = PDA_to_CFG(pda)
        rename(cfg)
        print('Полученная CFG (до очистки):')
        print(
            f'Нетерминалы: {[cfg.names_map[non_term.to_string() if type(non_term) == Triple else non_term] for non_term in cfg.non_terms]}')
        print(f'Правила: ')
        for rule in cfg.rules:
            print(rule.toString(cfg.names_map))
        cfg = clean(cfg)
        print('Полученная CFG (после очистки):')
        print(
            f'Нетерминалы: {[cfg.names_map[non_term.to_string() if type(non_term) == Triple else non_term] for non_term in cfg.non_terms]}')
        print(f'Правила: ')
        for rule in cfg.rules:
            print(rule.toString(cfg.names_map))


if __name__ == '__main__':
    check_tests('tests')
