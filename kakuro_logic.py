import itertools
import argparse
import copy
import re
import sys
import table_creator
import functools

SUM_PATTERN = re.compile(r'^\[(.{1,2})\\(.{1,2})\]$')
CELL_PATTERN = re.compile(r'^\[[a-fA-F0-9](-[a-fA-F0-9])*\]$')
HORIZONTAL = 'hor'
VERTICAL = 'vert'


class Solver:
    def __init__(self, count_of_digits, table=None):
        self.count_of_digits = count_of_digits
        self.table = table
        self.count_results = 0
        self.solutions = []

    @staticmethod
    def _process_regular_digits(digits):
        digits = list(re.sub(r'[\.\n]', '', digits))
        return digits

    @staticmethod
    def _get_range_digits(n):
        result = list(map(str, range(1, n)))
        for i in range(9, len(result)):
            if int(result[i]) >= 10:
                result[i] = chr(ord('a') + int(result[i]) % 10)
        return result

    def _get_possible_values(self, j):
        if j.hor_length != 1 and j.hor_sum:
            data = self._get_regular_nums(j.hor_length,
                                          j.hor_sum)
            eliminated_hor, used_hor = data
        else:
            used_hor = Solver._get_range_digits(self.count_of_digits)
            eliminated_hor = []
        if j.vert_length != 1 and j.vert_sum:
            data = self._get_regular_nums(j.vert_length,
                                          j.vert_sum)
            eliminated_vert, used_vert = data
        else:
            used_vert = Solver._get_range_digits(self.count_of_digits)
            eliminated_vert = []
        intersection_digits = list(set(used_hor).intersection(used_vert))
        union_digits = list(set(eliminated_hor).union(eliminated_vert))
        options = list(map(lambda x: int(x) if x.isdigit() else x,
                           j.options_cell))
        if options:
            intersection_digits = list(
                set(options).intersection(intersection_digits)
            )
            digits = Solver._get_range_digits(self.count_of_digits)
            digits = map(lambda x: int(x) if x.isdigit() else x, digits)
            eliminated = set(digits).difference(options)
            union_digits = list(set(union_digits).union(eliminated))
        return intersection_digits, union_digits

    @functools.lru_cache(maxsize=None)
    def _get_regular_nums(self, length, sum_):
        if not self.table:
            combs = Solver._get_combinations(sum_,
                                             length,
                                             self.count_of_digits)
        else:
            combs = self.table[length][sum_][0]
            combs = list(map(
                lambda x: list(map(
                    lambda y: int(y, self.count_of_digits), x)), combs))
        result = table_creator.find_regular_nums(combs, self.count_of_digits)
        return (result[1], result[0])

    @staticmethod
    def _get_combinations(sum_combs, count, numeral_system):
        nums = list(range(1, numeral_system))
        combs = []
        for j in itertools.combinations(nums, count):
            if sum(j) == sum_combs:
                combs.append(list(j))
        return combs

    def _set_single_possible_values(self, map_):
        for i in map_:
            for j in i:
                if (isinstance(j, str) or not j.hor_length
                        or not j.vert_length
                        or (not j.hor_sum and not j.vert_sum)):
                    continue
                data = self._get_possible_values(j)
                intersection_digits, union_digits = data
                if intersection_digits:
                    j.possible_values = intersection_digits
                else:
                    digits = Solver._get_range_digits(self.count_of_digits)
                    union_digits = map(str, union_digits)
                    uniq_digits = set(digits).difference(union_digits)
                    j.possible_values = list(uniq_digits)
                if len(j.possible_values) == 1:
                    j.value = '[{0}]'.format(j.possible_values[0])

    def print_solutions(self, kakuro, n=sys.maxsize):
        self._set_single_possible_values(kakuro.map_)
        startX, startY = Solver._find_next_empty_cell(kakuro.map_)
        self._solve(kakuro, startX, startY, n)
        for solution in self.solutions:
            print(solution + '\n')

    def _solve(self, original_kakuro, x, y, n):
        if self.count_results == n:
            return
        for value in original_kakuro.map_[x][y].possible_values:
            kakuro = copy.deepcopy(original_kakuro)
            map_ = kakuro.map_
            Solver._set_value_to_cell(map_, x, y, value)
            if not kakuro.check_lines():
                continue
            nextX, nextY = Solver._find_next_empty_cell(map_)
            if nextX == -1 and nextY == -1:
                kakuro.map_ = map_
                self.solutions.append(str(kakuro))
                self.count_results += 1
                return
            self._solve(kakuro, nextX, nextY, n)
        return

    @staticmethod
    def _set_value_to_cell(map_, x, y, value):
        value = str(value)
        map_[x][y].value = '[{0}]'.format(value)
        for i in map_[x][y].vert_neighbours:
            i.possible_values = list(set(i.possible_values) - {value})
        for i in map_[x][y].hor_neighbours:
            i.possible_values = list(set(i.possible_values) - {value})

    @staticmethod
    def _find_next_empty_cell(map_):
        for i in range(len(map_)):
            for j in range(len(map_[0])):
                if isinstance(map_[i][j], Cell) and map_[i][j].value == '[*]':
                    return i, j
        return -1, -1


class Cell:
    def __init__(self, value, x, y, hor_neighbours,
                 vert_neighbours, hor_sum=0, vert_sum=0,
                 hor_length=0, vert_length=0):
        self.value = value
        self.x = x
        self.y = y
        self.hor_sum = hor_sum
        self.vert_sum = vert_sum
        self.hor_length = hor_length
        self.vert_length = vert_length
        self.possible_values = []
        self.options_cell = []
        self.hor_neighbours = hor_neighbours
        self.vert_neighbours = vert_neighbours

    def __str__(self):
        return self.value


class Kakuro:
    def __init__(self, data, is_torus):
        self.map_ = self._create_map(data)
        if is_torus:
            self._process_tor()
        self.width = len(self.map_[0])
        self.height = len(self.map_)
        self.columns = self._create_columns()

    def _create_columns(self):
        columns = [[], []]
        added_hor_cells = set()
        added_ver_cells = set()
        for row in self.map_:
            for cell in row:
                if isinstance(cell, Cell):
                    if cell not in added_hor_cells:
                        to_append = (cell.hor_neighbours + [cell])
                        columns[0].append(to_append)
                        added_hor_cells = added_hor_cells.union(columns[0][-1])
                    if cell not in added_ver_cells:
                        columns[1].append(cell.vert_neighbours + [cell])
                        added_ver_cells = added_ver_cells.union(columns[1][-1])
        return columns

    def __str__(self):
        return '\n'.join(map(Kakuro._format_line, self.map_))

    @staticmethod
    def _format_line(line):
        return ''.join(map(lambda x: str(x).ljust(8), line)).rstrip()

    def _create_map(self, lines):
        map_ = []
        y = 0
        for i in range(len(lines)):
            lines[i] = lines[i].split()
        vert_sums = list(itertools.repeat(0, len(lines[0])))
        vert_lengths = copy.copy(vert_sums)
        vert_neighbours = []
        for i in range(len(lines[0])):
            vert_neighbours.append([])
        for line in lines:
            Kakuro._process_line(
                map_, y, line, vert_sums, vert_lengths, vert_neighbours)
            y += 1
        return map_

    @staticmethod
    def _process_line(map_, y, line, vert_sums, vert_lengths, vert_neighbours):
        x = 0
        map_.append([])
        hor_sum = 0
        hor_length = 0
        hor_neighbours = []
        for cell in line:
            no_empty_cell = CELL_PATTERN.search(cell)
            if cell == '[*]' or no_empty_cell:
                if no_empty_cell:
                    options_cell = no_empty_cell.group()[1:-1].split('-')
                else:
                    options_cell = []
                data = Kakuro._process_empty_cell(
                    map_,
                    x,
                    y,
                    hor_length,
                    vert_lengths[x],
                    hor_neighbours,
                    vert_neighbours,
                    hor_sum,
                    vert_sums[x],
                    options_cell)
                vert_lengths[x], hor_length = data
            else:
                map_[-1].append(cell)
                if cell == '[-]':
                    hor_sum = 0
                    vert_sums[x] = 0
                else:
                    vert_sums[x], hor_sum = Kakuro._process_sums(cell, x, y)
                vert_lengths[x] = 0
                hor_length = 0
                hor_neighbours = []
                vert_neighbours[x] = []
            x += 1

    @staticmethod
    def _process_empty_cell(map_,
                            x,
                            y,
                            hor_length,
                            vert_length,
                            hor_neighbours,
                            vert_neighbours,
                            hor_sum,
                            vert_sum,
                            variants_cell):
        hor_length += 1
        vert_length += 1
        map_[-1].append(Cell('[*]',
                             x,
                             y,
                             copy.copy(hor_neighbours),
                             copy.copy(vert_neighbours[x]),
                             hor_sum,
                             vert_sum,
                             hor_length,
                             vert_length))
        map_[-1][-1].options_cell = variants_cell
        Kakuro._add_neighbours(map_, x, y, HORIZONTAL, hor_length)
        Kakuro._add_neighbours(map_, x, y, VERTICAL, vert_length)
        hor_neighbours.append(map_[-1][-1])
        vert_neighbours[x].append(map_[-1][-1])
        return vert_length, hor_length

    @staticmethod
    def _process_sums(cell, x, y):
        sums = SUM_PATTERN.search(cell)
        result = [0, 0]
        if sums is None:
            raise ValueError(
                "Error: undefined cell '{}' ({},{})".format(cell, x, y))
        for i in [1, 2]:
            if sums.group(i) != '-':
                result[i - 1] = int(sums.group(i))
        return result

    @staticmethod
    def _add_neighbours(map_, x, y, direction, length):
        dir_length = direction + '_length'
        for i in range(1, length):
            if direction == HORIZONTAL:
                indice_1 = y
                indice_2 = x - i
            else:
                indice_1 = y - i
                indice_2 = x
            setattr(map_[indice_1][indice_2], dir_length,
                    getattr(map_[indice_1][indice_2], dir_length) + 1)
            getattr(map_[indice_1][indice_2],
                    direction + '_neighbours').append(map_[-1][-1])

    def _process_tor(self):
        self._process_direction_lines(HORIZONTAL)
        self._process_direction_lines(VERTICAL)

    def _process_direction_lines(self, direction):
        attr = direction + '_sum'
        for i in range(len(self.map_)):
            if direction == VERTICAL:
                cell_1 = self.map_[0][i]
                cell_2 = self.map_[-1][i]
            else:
                cell_1 = self.map_[i][0]
                cell_2 = self.map_[i][-1]
            if (isinstance(cell_1, Cell) and isinstance(cell_2, Cell)):
                if not getattr(cell_1, attr):
                    setattr(cell_1, attr, getattr(cell_2, attr))
                else:
                    setattr(cell_2, attr, getattr(cell_1, attr))
                Kakuro._exchange_neighbours(cell_1, cell_2, direction)
                Kakuro._exchange_neighbours(cell_2, cell_1, direction)
            elif (isinstance(cell_1, Cell)
                  and cell_2 != '[*]'
                  and cell_2 != '[-]'):
                sums = SUM_PATTERN.search(cell_2)
                if sums.group(2) != '-':
                    setattr(cell_1, attr, int(sums.group(2)))
                    for j in getattr(cell_1, direction + '_neighbours'):
                        setattr(j, attr, getattr(cell_1, attr))

    @staticmethod
    def _exchange_neighbours(cell_1, cell_2, direction):
        attr = direction + '_neighbours'
        neighbours_1 = getattr(cell_1, attr)
        neighbours_2 = getattr(cell_2, attr)
        setattr(cell_1, attr, list(set(neighbours_1
                                       + neighbours_2
                                       + [cell_2]) - {cell_1}))

    def check_lines(self):
        return self._check_line(0) and self._check_line(1)

    def _check_line(self, direction):
        for column in self.columns[direction]:
            sum_ = 0
            needBreak = False
            for j in column:
                if j.value[1:-1] == '*':
                    needBreak = True
                    break
                sum_ += Kakuro._get_int_from_str(j.value[1:-1])
            if (((direction == 1 and sum_ != column[0].vert_sum
                  and column[0].vert_sum)
                or (not direction and sum_ != column[0].hor_sum
                    and column[0].hor_sum)) and not needBreak):
                return False
        return True

    @staticmethod
    def _get_int_from_str(string):
        if string.isdigit():
            return int(string)
        return ord(string) - ord('a') + 10
