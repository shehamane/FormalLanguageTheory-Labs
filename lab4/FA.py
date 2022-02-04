import CFG
import graphviz


class Situation:
    def __init__(self, left, right_before, right_after):
        self.left = left
        self.right_before = right_before
        self.right_after = right_after

    def __str__(self):
        return self.left + ' -> ' + self.right_before + '.' + self.right_after

    def get_next_symbol(self):
        if not len(self.right_after):
            return False
        if self.right_after[0] == '[':
            return self.right_after[:self.right_after.find(']') + 1]
        else:
            return self.right_after[0]

    def get_goto(self):
        if not len(self.right_after):
            raise Exception('endmarker at the end pos!')
        return Situation(self.left, self.right_before + self.get_next_symbol(),
                         self.right_after[len(self.get_next_symbol()):])

    def __eq__(self, other):
        return self.left == other.left and self.right_before == other.right_before and self.right_after == other.right_after


class Transition:
    def __init__(self, fr: [Situation], to: [Situation], by):
        self.fr = fr
        self.to = to
        self.by = by


def gen_name():
    for i in range(65, 91):
        for j in range(0, 10):
            yield chr(i) + str(j)


class FA:
    def __init__(self):
        self.states = [
            [Situation('[S!]', '', '[S]$')]
        ]
        self.transitions = []

    def create_graph(self, path):
        dot = graphviz.Digraph(comment='LR(0) Automata')
        names = {}
        name_gen = gen_name()
        for state in self.states:
            name = name_gen.__next__()
            state_str = '\n'.join([str(sit) for sit in state])
            names[state_str] = name
            dot.node(name, state_str, **{'width':str(1), 'height':str(2), 'shape':'polygon'})
        for t in self.transitions:
            fr_str = '\n'.join([str(sit) for sit in t.fr])
            to_str = '\n'.join([str(sit) for sit in t.to])
            dot.edge(names[fr_str], names[to_str],
                     label=t.by)
        dot.render(path)


def make_LR0(cfg: CFG):
    fa = FA()

    def get_conflict_nterms(state: [Situation]):
        for i in range(0, len(state)):
            sit = state[i]
            if not sit.get_next_symbol():
                for j in range(0, len(state)):
                    if j == i:
                        continue
                    if state[j].right_before == sit.right_before:
                        return sit.left, state[j].left
        return False

    def find_situations_where_startswith(state: [Situation], symbol):
        return [situation for situation in state if situation.get_next_symbol() == symbol]

    def closure(state: [Situation]):
        for situation in state:
            next_symbol = situation.get_next_symbol()
            if not next_symbol:
                continue
            if next_symbol[0] == '[':
                old_len = len(state)
                new_situations = [Situation(next_symbol, '', right_part) for right_part in cfg.rules[next_symbol]]
                state += [situation for situation in new_situations if situation not in state]
                if len(state) > old_len:
                    closure(state)

    def goto(state: [Situation]):
        handled_symbols = []
        for situation in state:
            next_symbol = situation.get_next_symbol()
            if not next_symbol:
                continue

            if next_symbol in handled_symbols:
                continue
            else:
                handled_symbols.append(next_symbol)
                old_states = find_situations_where_startswith(state, next_symbol)
                new_state = [situation.get_goto() for situation in old_states]
                closure(new_state)
                if new_state not in fa.states:
                    conflicts = get_conflict_nterms(new_state)
                    if conflicts:
                        return conflicts
                    fa.states.append(new_state)
                    fa.transitions.append(Transition(state, fa.states[-1], next_symbol))
                else:
                    fa.transitions.append(Transition(state, fa.states[fa.states.index(new_state)], next_symbol))

    for state in fa.states:
        closure(state)
        conflicts = goto(state)
        if conflicts:
            return conflicts

    return fa
