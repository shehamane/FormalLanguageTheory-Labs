from regex_system import solve_system, Equation, get_substitution
import re
import os

DFA_regex = re.compile('^\<[A-Z][0-9]?,\{(\<[A-Z][0-9]?,[a-z],[A-Z][0-9]?\>)+\},\{[A-Z][0-9]?(,[A-Z][0-9]?)*\}\>$')
transitions_regex = re.compile('\{(\<[A-Z][0-9]?,[a-z],[A-Z][0-9]?\>)+\}')


class Transition:
    def __init__(self, f, t, b):
        self.f = f
        self.t = t
        self.b = b


def read_input(path):
    with open(path, 'r') as input_file:
        input_line = input_file.read()
        if not DFA_regex.match(input_line):
            return False
        transitions_line = input_line[input_line.find('{') + 1:input_line.find('}')]
        start_line = input_line[1:input_line.find(',')]
        final_line = input_line[input_line.rfind('{') + 1:input_line.rfind('}')]

        transition_lines = transitions_line[1:-1].split('><')
        transitions = list(map(lambda line: line.split(','), transition_lines))
        return start_line, transitions, final_line.split(',')


def find_trans(state, transitions):
    ans = []
    for t in transitions:
        if t[0] == state:
            ans.append([t[2], t[1]])
    return ans


def get_system(start, trans, finals):
    system = []
    states_query = [start]
    for state in states_query:
        ts = find_trans(state, trans)
        a = {}
        for t in ts:
            if t[0] in a:
                a[t[0]].replace('(', '').replace(')', '')
                a[t[0]] += '+' + t[1]
                a[t[0]] = f'({a[t[0]]})'
            else:
                a[t[0]] = t[1]
            if not t[0] in states_query:
                states_query.append(t[0])
        system.append(Equation(state, a, "E" if state in finals else ""))
    return system


def check_tests(dir_path):
    tests = os.listdir(dir_path)
    for test in tests:
        start_state, transitions, final_states = read_input(f"{dir_path}/{test}")
        print(f"NAME = {test}")
        print('\n')
        system = get_system(start_state, transitions, final_states)
        solve_system(system)
        s = get_substitution(system[0])
        if s.alpha:
            print(f'{s.alpha}*{s.free}')
        else:
            print(f'{s.free}')

        print("===============")


if __name__ == '__main__':
    check_tests('tests_dfa')
