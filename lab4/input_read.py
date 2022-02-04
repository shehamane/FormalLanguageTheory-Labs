import re
from CFG import CFG

CFG_regex = re.compile(
    '^\$EXTRACTIONS\s*=\s*([1-9][0-9]*)'
    '(\n\[[A-z]+\]\s*::=\s*(\[[A-z]+\]|[0-9]|[a-z]|_|\*|\+|\=|\(|\)|\$|;|:)+)+$'
)


def get_symbols_list(s):
    flag = False
    tmp = ''
    l = []
    for c in s:
        if c == '[':
            tmp = '['
            flag = True
        elif c == ']':
            flag = False
            tmp += ']'
            l.append(tmp)
        elif flag:
            tmp += c
        else:
            l.append(c)
    return l


def read_grammar(path):
    with open(path, 'r') as input_file:
        input_text = input_file.read()

        if not CFG_regex.match(input_text):
            raise Exception("Invalid input format")

    with open(path, 'r') as input_file:
        cfg = CFG()

        extractions = int(re.compile("[1-9][0-9]*").findall(input_file.readline())[0])
        rules = list(map(lambda s: s.strip(), input_file.readlines()))
        for rule in rules:
            left, right = rule.split('::=')
            right_symbols = get_symbols_list(right)
            for s in right_symbols:
                if s[0] == '[' and s not in cfg.nterms:
                    cfg.nterms.append(s)
                if len(s) == 1 and s not in cfg.terms:
                    cfg.terms.append(s)
            if left not in cfg.nterms:
                cfg.nterms.append(left)
            if left in cfg.rules.keys():
                cfg.rules[left].append(right)
            else:
                cfg.rules[left] = [right]

        return cfg, extractions
