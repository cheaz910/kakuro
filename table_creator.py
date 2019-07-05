import sys
import itertools
import argparse
from collections import defaultdict


def write_table(table, count, output_name):
    with open(output_name, 'w') as f:
        for i in table:
            f.write(combine_part(table, i, count))


def write_stdout(table, count):
    for i in table:
        print(combine_part(table, i, count))


def combine_part(table, i, count):
    used, eliminated = find_regular_nums(table[i], count)
    used = ''.join(map(str, used))
    eliminated = ''.join(map(str, eliminated))
    combs = ' '.join(map(lambda x: ''.join(map(str, replace_nums(x))),
                         table[i]))
    result = '{0} {1}\n{2}\n'.format(i[0], i[1], combs)
    result += '{0}\n{1}\n'.format(eliminated, used)
    return result


def create_table(count):
    nums = list(range(1, count))
    table = defaultdict(list)
    for i in range(1, count):
        for j in itertools.combinations(nums, i):
            table[(i, sum(j))].append(list(j))
    return table


def replace_nums(nums):
    for i in range(len(nums)):
        if nums[i] >= 10:
            nums[i] = chr(ord('a') + nums[i] % 10)
    return nums


def find_regular_nums(combs, numeral_system):
    if not combs:
        return [], []
    used = set(combs[0])
    eliminated = set(range(1, numeral_system))
    current = set(combs[0])
    for i in combs[1:]:
        used = used.intersection(i)
        current = current.union(i)
    eliminated = eliminated.difference(current)
    return replace_nums(list(used)), replace_nums(list(eliminated))


def main():
    count = 10
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', nargs=1, help='Output filename')
    parser.add_argument('--numSys', nargs=1, type=int, help='Numeral system')
    args = vars(parser.parse_args())
    if args['numSys'] is not None:
        count = args['numSys'][0]
    table = create_table(count)
    if args['name'] is not None:
        write_table(table, count - 1, args['name'][0])
    else:
        write_stdout(table, count - 1)


if __name__ == '__main__':
    main()
