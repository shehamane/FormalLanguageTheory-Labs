import os


def is_overlap(s1: str, s2: str = None):
    if s2:
        for i in range(1, min(len(s1), len(s2))):
            if s1[:i] == s2[-i:]:
                return True
        return False
    else:
        for i in range(1, len(s1)):
            if s1[:i] == s1[-i:]:
                return True
        return False


def find_overlap(rules):
    for i in range(0, len(rules)):
        for j in range(0, len(rules)):
            if i == j:
                if is_overlap(rules[i]):
                    print(f"Перекрытие внутри {rules[i]}")
                    return
            elif is_overlap(rules[i], rules[j]):
                print(f"Перекрытие в {rules[i]} и {rules[j]}")
                return
    print(f"Система конфлюэнтна")


def read_input(path):
    with open(path, "r") as input_file:
        return [rule.split("->")[0].strip() for rule in input_file.readlines()]


def check_tests(dir_path):
    tests = os.listdir(dir_path)
    for test in tests:
        print(f"===============\ntest {test}")
        rules = read_input(f"{dir_path}/{test}")
        find_overlap(rules)


if __name__ == "__main__":
    check_tests("./test2")
