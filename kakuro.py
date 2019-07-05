import itertools
import argparse
import copy
import re
import sys
import table_creator
import functools
from kakuro_logic import Cell, Kakuro, Solver


def main():
    data = None
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=1, help='Count of solutions')
    parser.add_argument('--numSys', type=int, default=10,
                        help='Numeral system')
    parser.add_argument('--table', nargs=1,
                        help='Name of table with combinations')
    parser.add_argument('-t', '--tor', action='store_true',
                        help='Solve torus kakuro')
    parser.add_argument('filename', type=str,
                        help='Name of file with map of kakuro')
    args = parser.parse_args()
    table = None
    if args.table is not None:
        try:
            table = load_table(args.table[0])
        except IOError as e:
            print(e, file=sys.stderr)
            sys.exit(9)
        except ValueError as e:
            print('Error: table is not valid\n', file=sys.stderr)
            sys.exit(10)
    if args.filename is not None:
        try:
            data = load_data(args.filename)
        except IOError as e:
            print(e, file=sys.stderr)
            sys.exit(7)
    try:
        myKakuro = Kakuro(data, args.tor)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(8)
    solver = Solver(args.numSys, table)
    solver.print_solutions(myKakuro, args.n)
    if not solver.count_results:
        print('No solutions', file=sys.stderr)
        sys.exit(1)


def load_data(filename):
    with open(filename) as f:
        data = f.read()
    return data.rstrip().split('\n')


def load_table(filename):
    table = {}
    with open(filename) as f:
        info = list(map(int, f.readline().split()))
        combinations = f.readline().split()
        eliminated = Solver._process_regular_digits(f.readline())
        used = Solver._process_regular_digits(f.readline())
        while info:
            if not info[0] in table:
                table[info[0]] = dict()
            if len(info) != 2:
                raise ValueError
            table[info[0]][info[1]] = (combinations, eliminated, used)
            info = list(map(int, f.readline().split()))
            combinations = f.readline().split()
            eliminated = Solver._process_regular_digits(f.readline())
            used = Solver._process_regular_digits(f.readline())
    return table


if __name__ == '__main__':
    main()
