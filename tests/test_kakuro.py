import unittest
import os
import sys
from io import StringIO

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from kakuro_logic import Cell, Solver, Kakuro
import table_creator
import kakuro


class TableCreatorTest(unittest.TestCase):
    def test_main(self):
        sys.argv[1:] = ['--name',
                        'tests/test_create_table.txt',
                        '--numSys',
                        '10']
        table_creator.main()

    def test_replace_nums(self):
        nums = table_creator.replace_nums(list(range(1, 11)))
        actual_result = list(map(str, nums))
        expected_result = list(map(str, range(1, 10)))
        expected_result.append('a')
        self.assertEqual(actual_result, expected_result)

    def test_find_regular_nums(self):
        actual_result = table_creator.find_regular_nums([[1, 2], [2, 3]], 2)
        self.assertEqual([2], actual_result[0])
        self.assertEqual([], actual_result[1])

    def test_create_table(self):
        actual_result = table_creator.create_table(4)
        self.assertEqual([[1, 2]], actual_result[(2, 3)])
        self.assertEqual([[1, 3]], actual_result[(2, 4)])
        self.assertEqual([[2, 3]], actual_result[(2, 5)])
        self.assertEqual([[1]], actual_result[(1, 1)])

    def test_combine_part(self):
        table = table_creator.create_table(10)
        actual_result = table_creator.combine_part(table, (1, 5), 10)
        expected_result = "1 5\n5\n12346789\n5\n"
        self.assertEqual(expected_result, actual_result)


class SolverTest(unittest.TestCase):
    def test_main(self):
        sys.argv[1:] = ['maps/mapKakuro2.txt',
                        '--table',
                        'tests/test_main_table.txt']
        kakuro.main()

    def test_main_errors(self):
        sys.argv[1:] = ['UNDEFINEDFILE',
                        '--table',
                        'UNDEFINEDFILE']
        sys.stderr = StringIO()
        with self.assertRaises(SystemExit):
            kakuro.main()
        sys.argv[3] = 'tests/test_bad_table.txt'
        with self.assertRaises(SystemExit):
            kakuro.main()
        sys.argv[3] = 'tests/test_main_table.txt'
        with self.assertRaises(SystemExit):
            kakuro.main()
        sys.argv[1:] = ['maps/mapKakuro_NoSolutions.txt']
        with self.assertRaises(SystemExit):
            kakuro.main()
        sys.argv[1] = 'tests/test_bad_table.txt'
        with self.assertRaises(SystemExit):
            kakuro.main()

    def test_load_data(self):
        actual_result = kakuro.load_data('maps/mapKakuro3.txt')
        expected_result = ['[-] [8\\-] [8\\-]',
                           '[-\\3] [*]   [*]',
                           '[-\\13] [*] [*]']
        self.assertEqual(actual_result, expected_result)

    def test_load_table(self):
        actual_result = kakuro.load_table('tests/test_table.txt')
        expected_result = {1: {1: (['1'], ['2', '3', '4'], ['1']),
                               2: (['2'], ['1', '3', '4'], ['2'])}}

        self.assertEqual(expected_result, actual_result)

    def test_load_bad_data(self):
        with self.assertRaises(IOError):
            kakuro.load_data('nonexistentfile.txt')

    def test_load_bad_table(self):
        with self.assertRaises(IOError):
            table = kakuro.load_table('nonexistenttable.txt')

    def test_get_range_digits(self):
        actual_result = Solver._get_range_digits(11)
        expected_result = list(map(str, range(1, 10)))
        expected_result.append('a')
        self.assertEqual(actual_result, expected_result)

    def test_find_next_empty_cell(self):
        input_ = ['[-\\13] [*] [*]', '[-\\12] [*] [*]']
        kakuro = Kakuro(input_, False)
        solver = Solver(10, False)
        solver.print_solutions(kakuro, 1)
        self.assertEqual(Solver._find_next_empty_cell(kakuro.map_), (0, 1))
        Solver._set_value_to_cell(kakuro.map_, 0, 1, 6)
        self.assertEqual(Solver._find_next_empty_cell(kakuro.map_), (0, 2))
        Solver._set_value_to_cell(kakuro.map_, 0, 2, 6)
        self.assertEqual(Solver._find_next_empty_cell(kakuro.map_), (1, 1))
        Solver._set_value_to_cell(kakuro.map_, 1, 1, 6)
        self.assertEqual(Solver._find_next_empty_cell(kakuro.map_), (1, 2))
        Solver._set_value_to_cell(kakuro.map_, 1, 2, 6)
        self.assertEqual(Solver._find_next_empty_cell(kakuro.map_), (-1, -1))

    def test_get_possible_values(self):
        cell = Cell('*', 0, 0, [], [], 15, 7, 2, 2)
        solver = Solver(10, False)
        intersection_digits, union_digits = solver._get_possible_values(cell)
        self.assertEqual(intersection_digits, [])
        self.assertEqual(union_digits, [1, 2, 3, 4, 5, 7, 8, 9])

    def test_get_regular_nums(self):
        solver = Solver(10, False)
        eliminated_digits, used_digits = solver._get_regular_nums(2, 15)
        self.assertEqual(eliminated_digits, [1, 2, 3, 4, 5])
        self.assertEqual(used_digits, [])
        eliminated_digits, used_digits = solver._get_regular_nums(2, 7)
        self.assertEqual(eliminated_digits, [8, 9, 7])
        self.assertEqual(used_digits, [])

    def test_set_value_to_cell(self):
        input_ = ['[-\\36] [*] [*] [*] [*] [*] [*] [*] [*]']
        kakuro = Kakuro(input_, False)
        solver = Solver(10, False)
        solver._set_single_possible_values(kakuro.map_)
        for j in range(8):
            for i in range(1 + j, 9):
                expected_result = set(map(str, range(1, 9 - j)))
                self.assertEqual(set(kakuro.map_[0][i].possible_values),
                                 expected_result)
            solver._set_value_to_cell(kakuro.map_, 0, 1 + j, 8 - j)

    def test_set_single_possible_values(self):
        input_ = ['[-] [11\\-] [7\\-]',
                  '[-\\15] [*] [*]',
                  '[-\\3] [*] [*]']
        kakuro = Kakuro(input_, False)
        solver = Solver(10, False)
        solver._set_single_possible_values(kakuro.map_)
        out = StringIO()
        sys.stdout = out
        print(kakuro)
        out = out.getvalue().strip()
        expected_result = '[-]     [11\\-]  [7\\-]\n[-\\15]  '
        expected_result += '[*]     [6]\n[-\\3]   [2]     [*]'
        self.assertEqual(out, expected_result)

    def test_process_regular_digits(self):
        actual_result = Solver._process_regular_digits('1.4.5.66.8......234')
        expected_result = ['1', '4', '5', '6', '6', '8', '2', '3', '4']
        self.assertEqual(actual_result, expected_result)

    def test_create_map(self):
        input_ = ['[-] [13\\-] [7\\-]',
                  '[*] [-\\15] [*]',
                  '[-\\5] [*] [*]']
        kakuro = Kakuro(input_, False)
        out = StringIO()
        sys.stdout = out
        print(kakuro)
        out = out.getvalue().strip()
        expected_result = '[-]     [13\\-]  [7\\-]\n[*]     '
        expected_result += '[-\\15]  [*]\n[-\\5]   [*]     [*]'
        self.assertEqual(out, expected_result)

    def test_create_bad_map(self):
        input_ = ['[-] [13\\-] [7\\-]',
                  '[-\\15\\13] [*] [*]',
                  '[-\\5] [*] [*]']
        with self.assertRaises(ValueError):
            kakuro = Kakuro(input_, False)

    def test_solve2x2(self):
        input_ = ['[-] [13\\-] [7\\-]',
                  '[-\\15] [*] [*]',
                  '[-\\5] [*] [*]']
        kakuro = Kakuro(input_, False)
        solver = Solver(10, False)
        out = StringIO()
        sys.stdout = out
        solver.print_solutions(kakuro, 1)
        out = out.getvalue().strip()
        expected_result = '[-]     [13\\-]  [7\\-]\n[-\\15]  '
        expected_result += '[9]     [6]\n[-\\5]   [4]     [1]'
        self.assertEqual(out, expected_result)

    def test_solve3x3_tor(self):
        input_ = ['[-\\3] [*]     [*]',
                  '[-]    [3\\-]  [6\\-]',
                  '[-\\6]    [*]     [*]']
        kakuro = Kakuro(input_, True)
        solver = Solver(10)
        out = StringIO()
        sys.stdout = out
        solver.print_solutions(kakuro, 1)
        out = out.getvalue().strip()
        expected_result1 = '[-\\3]   [1]     [2]\n[-]     '
        expected_result1 += '[3\\-]   [6\\-]\n[-\\6]   [2]     [4]'
        expected_result2 = '[-\\3]   [2]     [1]\n[-]     '
        expected_result2 += '[3\\-]   [6\\-]\n[-\\6]   [1]     [5]'
        self.assertTrue(out == expected_result1 or out == expected_result2)

    def test_check_lines(self):
        input_ = ['[-] [13\\-] [7\\-]',
                  '[-\\15] [*] [*]',
                  '[-\\5] [*] [*]']
        kakuro = Kakuro(input_, False)
        Solver._set_value_to_cell(kakuro.map_, 1, 1, 9)
        self.assertEqual(kakuro.check_lines(), True)
        Solver._set_value_to_cell(kakuro.map_, 2, 1, 5)
        self.assertEqual(kakuro.check_lines(), False)
        Solver._set_value_to_cell(kakuro.map_, 2, 1, 4)
        self.assertEqual(kakuro.check_lines(), True)
        Solver._set_value_to_cell(kakuro.map_, 1, 2, 6)
        self.assertEqual(kakuro.check_lines(), True)
        Solver._set_value_to_cell(kakuro.map_, 2, 2, 6)
        self.assertEqual(kakuro.check_lines(), False)
        Solver._set_value_to_cell(kakuro.map_, 2, 2, 1)
        self.assertEqual(kakuro.check_lines(), True)


if __name__ == '__main__':
    unittest.main()
