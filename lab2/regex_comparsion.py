import time
import re
from random import randrange


#Функция, выдающая рандомное кратное числа divider в диапазоне (min, max) (если multiple=False, то функция выдает некратное
#Число выдается в двоичном виде в формате строки
def get_random_multiple(divider, multiple=True, min=2 ** 100, max=2 ** 100000):
    if multiple:
        number = randrange(min, max)
        number -= number % divider
        return bin(number)[2:]
    else:
        number = randrange(min, max)
        if not number % divider:
            number += randrange(divider)
        return bin(number)[2:]


#Запускаем n тестов
#Результат теста в виде словаря: id - номер теста, len - длина исходной строки, match - результаты работ регулярок, times - времена работ регулярок
#Половина тестов производится на строках, для которых регулярка должна вернуть true, половина -,,- false
def run_tests(n=10):
    results = []
    for i in range(n):
        bin_number = get_random_multiple(3, False) if i < n // 2 else get_random_multiple(3)
        result = {'id': i, 'len': len(bin_number), 'match': [], 'times': []}

        for rex in re_academic, re_denial, re_lazy:
            start = time.clock()
            if rex.match(bin_number):
                result['match'].append(True)
            else:
                result['match'].append(False)
            end = time.clock()
            result['times'].append(end - start)
        results.append(result)
    return results


result_pattern = "test №{id}, len = {len}: academic regex - {times[0]}, denial regex = {times[1]}, lazy regex = {times[2]}"

if __name__ == '__main__':
    re_academic = re.compile('^(0|1(01*0)*1)+$')
    re_denial = re.compile('^([^1]|[^0]([^1][^0]*[^1])*[^0])+$')
    re_lazy = re.compile('^([^1]|[^0]([^1][^0]*?[^1])*[^0])+?$')

    for result in run_tests(10):
        print(result_pattern.format(id=result['id'], len=result['len'], times=result['times']))
