def get_substitution_combinations(right_parent, left_child, right_child):
    positions = []

    symbol = ''
    is_nterm = False
    start = -1
    for i, c in enumerate(right_parent):
        if c == '[':
            start = i
            is_nterm = True
            symbol = '['
        elif c == ']':
            symbol += c
            if symbol == left_child:
                positions.append((start, i + 1))
            symbol = ''
            is_nterm = False
        elif is_nterm:
            symbol += c

    if not positions:
        return []

    new_rights = []
    for combination in range(0, 2 ** len(positions) - 1):
        new_right = right_parent[0:positions[0][0]]

        for i, pos in enumerate(positions):
            if (i + 1) & combination:
                new_right += left_child
            else:
                new_right += right_child

            if i == len(positions) - 1:
                new_right += right_parent[pos[1]:]
            else:
                new_right += right_parent[pos[1]:positions[i + 1][0]]

        new_rights.append(new_right)
    return new_rights


class CFG:
    def __init__(self):
        self.terms = []
        self.nterms = []
        self.rules = {}

    def clarify_right_context(self, rule, A):
        def get_first(B, stack):
            stack.append(B)
            ans = []
            for right in self.rules[B]:
                if right[0] == '[':
                    C = right[0:right.find(']') + 1]
                    if C in stack:
                        continue
                    ans += get_first(C, stack)
                else:
                    ans.append(right[0])
            return ans

        def replace_rules(old_nterm, new_nterm, c):
            self.rules[new_nterm] = []
            for right in self.rules[old_nterm]:
                if right[0] == c:
                    self.rules[new_nterm].append(right[1:])
                elif right[0] == '[':
                    D = right[:right.find(']') + 1]
                    new_D = f'[{c}/' + D[1:]
                    if c in get_first(D, []):
                        self.rules[new_nterm].append(new_D + right[len(D):])
                        if new_D not in self.rules.keys():
                            replace_rules(D, new_D, c)

        left, right = rule
        findpos = right.find(A)
        Bpos = right.find(']', findpos + 1) + 1
        B = right[Bpos:right.find(']', Bpos) + 1]
        firstB = get_first(B, [])
        for c in firstB:
            new_nterm = f'[{c}/' + B[1:]
            self.rules[left].append(right[:Bpos] + c + new_nterm + right[Bpos + len(B):])
            replace_rules(B, new_nterm, c)
        self.rules[left].remove(right)

    def attach_right_context(self, nterm):
        clarified = 0
        new_nterms = {}
        is_update = True

        while is_update:
            is_update = False
            for left, rights in reversed(list(self.rules.items())):
                i = 0
                while i < len(rights):
                    right = rights[i]
                    i += 1
                    findpos = right.find(nterm)
                    pos = findpos
                    if pos > -1:
                        while right[pos] != ']':
                            pos += 1
                        pos += 1

                        if pos == len(right):
                            clarified += 1
                            rules_containing = {}
                            for left1, rights1 in list(self.rules.items()):
                                for right1 in rights1:
                                    if left in right1:
                                        if left1 in rules_containing.keys():
                                            rules_containing[left1].append(right1)
                                        else:
                                            rules_containing[left1] = [right1]
                            if left in rules_containing.keys() and right in rules_containing[left]:
                                return 1000000
                            for left1, rights1 in list(rules_containing.items()):
                                for right1 in rights1:
                                    new_rights = get_substitution_combinations(right1, left, right)
                                    self.rules[left1] += new_rights
                                    is_update = True
                                self.rules[left].remove(right)

                        if pos < len(right) and right[pos] != '[':
                            i = 0
                            term = right[pos]
                            new_right = right[:pos - 1] + term + ']' + right[pos + 1:]
                            new_nterm = new_right[findpos:pos + 1]
                            self.rules[left].remove(right)
                            self.rules[left].append(new_right)
                            is_update = True

                            if nterm not in new_nterms.keys():
                                new_nterms[nterm] = [new_nterm]
                            else:
                                if new_nterm not in new_nterms[nterm]:
                                    new_nterms[nterm].append(new_nterm)
                        elif pos < len(right) and right[pos] == '[':
                            self.clarify_right_context([left, right], nterm)
                            is_update = True
                            clarified += 1

        for old, news in new_nterms.items():
            for new in news:
                self.nterms.append(new)
                self.rules[new] = []
                for right1 in self.rules[nterm]:
                    self.rules[new].append(right1 + new[-2])

        return clarified

    def get_effective_nvars(self):
        effective_vars = []
        for left, rights in self.rules.items():
            for right in rights:
                flag = True
                for c in right:
                    if c == '[':
                        flag = False
                        break
                if flag and left not in effective_vars:
                    effective_vars.append(left)

        flag = True
        while flag:
            flag = False
            for left, rights in self.rules.items():
                if left in effective_vars:
                    continue
                for right in rights:
                    flag1 = True
                    for i, c in enumerate(right):
                        if c == '[' and right[i:right.find(']', i) + 1] not in effective_vars:
                            flag1 = False

                    if flag1 and left not in effective_vars:
                        effective_vars.append(left)
                        flag = True
        return effective_vars

    def get_attainable_nvars(self):
        attainable = ['[S]']
        flag = True
        while flag:
            flag = False
            for left, rights in self.rules.items():
                if left in attainable:
                    for right in rights:
                        for i, c in enumerate(right):
                            if c == '[' and \
                                    right[i:right.find(']', i) + 1] not in attainable:
                                attainable.append(right[i:right.find(']', i) + 1])
                                flag = True
        return attainable

    def check_right_for_existance(self, right):
        symbol = ''
        is_nterm = False
        for c in right:
            if c == '[':
                is_nterm = True
                symbol = '['
            elif c == ']':
                symbol += c
                if symbol not in self.nterms:
                    return False
                symbol = ''
                is_nterm = False
            elif is_nterm:
                symbol += c
        return True

    def clean(self):
        w_flag = True

        while w_flag:
            w_flag = False

            att = self.get_attainable_nvars()
            eff = self.get_effective_nvars()
            self.nterms = list(set(att) & set(eff))

            for left, rights in list(self.rules.items()):
                if left not in self.nterms:
                    self.rules.pop(left)
                else:
                    for right in reversed(rights):
                        if not self.check_right_for_existance(right):
                            w_flag = True
                            self.rules[left].remove(right)

    def delete_epsilon_rules(self):
        def get_bad_nterms():
            bad = []

            def is_all_bad_nterms(s):
                tmp = ''
                flag = False
                for c in s:
                    if c != '[' and flag:
                        tmp += c
                    if c == '[' and not flag:
                        flag = True
                        tmp = '['
                    if c != '[' and not flag:
                        return False
                    if c == ']' and flag:
                        tmp += ']'
                        if tmp not in bad:
                            return False
                return True

            for left, rights in self.rules.items():
                if '' in rights and left not in bad:
                    bad.append(left)

            flag = False
            while flag:
                flag = False
                for left, rights in self.rules.items():
                    for right in rights:
                        if is_all_bad_nterms(right) and left not in bad:
                            flag = True
                            bad.append(left)

            return bad

        def get_rule_combinations(right, bad):
            positions = []

            symbol = ''
            is_nterm = False
            start = -1
            for i, c in enumerate(right):
                if c == '[':
                    start = i
                    is_nterm = True
                    symbol = '['
                elif c == ']':
                    symbol += c
                    if symbol in bad:
                        positions.append((start, i + 1))
                    symbol = ''
                    is_nterm = False
                elif is_nterm:
                    symbol += c

            if not positions:
                return []

            new_rights = []
            for combination in range(0, 2 ** len(positions) - 1):
                new_right = right[0:positions[0][0]]

                for i, pos in enumerate(positions):
                    if (i + 1) & combination:
                        new_right += right[pos[0]:pos[1]]

                    if i == len(positions) - 1:
                        new_right += right[pos[1]:]
                    else:
                        new_right += right[pos[1]:positions[i + 1][0]]

                new_rights.append(new_right)
            return new_rights

        bad = get_bad_nterms()
        if bad:
            for left, rights in self.rules.items():
                for right in rights:
                    self.rules[left] = list(set(self.rules[left]) | set(get_rule_combinations(right, bad)))

            for left, rights in self.rules.items():
                for right in rights:
                    if right == '':
                        self.rules[left].remove(right)

        self.clean()
