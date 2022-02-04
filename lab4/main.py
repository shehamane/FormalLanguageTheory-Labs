import os
import FA

from input_read import read_grammar

if __name__ == '__main__':
    tests = os.listdir('tests')
    for test in tests:
        print(f'========={test}==========')
        cfg, extractions = read_grammar(f"tests/{test}")

        fa = FA.make_LR0(cfg)
        while extractions > 0:
            if fa.__class__ != tuple:
                break
            else:
                n1, n2 = fa
                extractions -= cfg.attach_right_context(n1)
                if n1 != n2 and extractions>0:
                    extractions -= cfg.attach_right_context(n2)
            cfg.delete_epsilon_rules()
            fa = FA.make_LR0(cfg)


        if extractions < 1:
            print('Подгонка не удалась')
        else:
            fa.create_graph(f'graphs/{test}.gv')

        for left, rights in cfg.rules.items():
            for right in rights:
                print(f'{left} ::= {right}')

