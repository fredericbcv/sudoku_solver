#!/usr/bin/python3

import os, sys
from sudoku     import *
from random     import *
from itertools  import product

import linecache
import os
import tracemalloc

import pickle

def display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print("#%s: %s:%s: %.1f KiB"
              % (index, frame.filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

class sudoku_solver(sudoku):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.solved = False
        self.error = False

        if self.is_error():
            self.error = True
            return

    def run(self):
        # print('run')
        self.solve()

        if self.is_valid():
            self.solved = True
            return True

        if self.is_error():
            self.error = True
            return None

        # No solution found
        possible_cells     = list(filter(lambda x: x.value == 0, self.matrix))

        for len_possible in range(2,9):
            min_possible_cell = filter(lambda x: len(x.possibility) == len_possible, possible_cells)

            for tmp_cell in min_possible_cell:

                for value in tmp_cell.possibility:

                    # Create a backup copy 
                    self_copy = pickle.dumps(self)
                    tmp_sudoku = pickle.loads(self_copy)

                    tmp_sudoku.set_value(value,tmp_cell.line,tmp_cell.row)

                    try:
                        tmp_sudoku.run()
                    except RuntimeError:
                        continue

                    if tmp_sudoku.solved:
                        self.copy(tmp_sudoku)
                        self.solved = True
                        return

                    if tmp_sudoku.error:
                        continue

                return

    def solve(self):
        len_possible_cells = 9 * 81

        while True:
            self.process_unique()
            self.process_duplicates()

            if self.is_valid():
                break

            possible_cells = list(filter(lambda x: x.value == 0, self.matrix))

            if len(possible_cells) < len_possible_cells:
                len_possible_cells = len(possible_cells)
                continue

            break

    def process_unique(self):
        # List unique possibility
        possible_cells = list(filter(lambda x: x.value == 0, self.matrix))
        unique_cells = list(filter(lambda x: len(x.possibility) == 1, possible_cells))

        for cell in unique_cells:
            if len(cell.possibility) > 0:
                self.set_value(cell.possibility[0],cell.line,cell.row)

        # Set unique per line
        possible_cells = list(filter(lambda x: x.value == 0, possible_cells))
        # Check unique per line
        for line_num in range(9):
            tmp_line_cells = list(filter(lambda x: x.line == line_num, possible_cells))
            tmp_line_possiblity = self.flatten_list(list(map(lambda x: x.possibility, tmp_line_cells)))

            tmp_dict = dict()
            for num_value in list(set(tmp_line_possiblity)):
                tmp_dict[num_value] = tmp_line_possiblity.count(num_value)

            for cell in tmp_line_cells:
                for num_value in cell.possibility:
                    if tmp_dict[num_value] == 1:
                        self.set_value(num_value,cell.line,cell.row)

        # Set unique per row
        possible_cells = list(filter(lambda x: x.value == 0, possible_cells))
        # Check unique per line
        for row_num in range(9):
            tmp_line_cells = list(filter(lambda x: x.row == row_num, possible_cells))
            tmp_line_possiblity = self.flatten_list(list(map(lambda x: x.possibility, tmp_line_cells)))

            tmp_dict = dict()
            for num_value in list(set(tmp_line_possiblity)):
                tmp_dict[num_value] = tmp_line_possiblity.count(num_value)


            for cell in tmp_line_cells:
                for num_value in cell.possibility:
                    if tmp_dict[num_value] == 1:
                        self.set_value(num_value,cell.line,cell.row)

        # Set unique per block
        possible_cells = list(filter(lambda x: x.value == 0, possible_cells))
        for block_num in range(9):
            tmp_line_cells = list(filter(lambda x: x.block == block_num, possible_cells))
            tmp_line_possiblity = self.flatten_list(list(map(lambda x: x.possibility, tmp_line_cells)))

            tmp_dict = dict()
            for num_value in list(set(tmp_line_possiblity)):
                tmp_dict[num_value] = tmp_line_possiblity.count(num_value)

            for cell in tmp_line_cells:
                for num_value in cell.possibility:
                    if tmp_dict[num_value] == 1:
                        self.set_value(num_value,cell.line,cell.row)

    def process_duplicates(self):
        possible_cells = list(filter(lambda x: x.value == 0, self.matrix))
        # Filter
        for block_num in range(9):
            possible_block = list(filter(lambda x: x.block == block_num,possible_cells))
            self.filter_duplicates(possible_block)
            if self.process_duplicates_algo(possible_block): return True
        
        possible_cells = list(filter(lambda x: x.value == 0, possible_cells))
        for line_num in range(9):
            possible_line = list(filter(lambda x: x.line == line_num,possible_cells))
            self.filter_duplicates(possible_line)
            if self.process_duplicates_algo(possible_line): return True
        
        possible_cells = list(filter(lambda x: x.value == 0, possible_cells))
        for row_num in range(9):
            possible_row = list(filter(lambda x: x.row == row_num,possible_cells))
            self.filter_duplicates(possible_row)
            if self.process_duplicates_algo(possible_row): return True

        return list(filter(lambda x: x.value == 0, possible_cells))

    def filter_duplicates(self,tmp_list):
        # List all num
        num_list = self.flatten_list(list(map(lambda x: x.possibility, tmp_list)))

        # Search each num declared twice
        twice_num = list()
        for num_value in list(set(num_list)):
            if num_list.count(num_value) == 2:
                twice_num.append(num_value)

        # Is two num find twice ?
        if len(twice_num) < 2:
            return

        # List all num couples duplicates possibility
        num_couples = list()
        for i, num_value in enumerate(twice_num):
            num_couples += list(product([num_value],twice_num[i+1:]))

        # List duplicates couples possiblity
        eval_duplicate_couples = dict()
        for num_couple in num_couples:
            eval_duplicate_couples[num_couple] = list(filter(lambda x: num_couple[0] in x.possibility and num_couple[1] in x.possibility, tmp_list))

        # Update duplicate list
        for tmp_couple in eval_duplicate_couples.keys():
            if len(eval_duplicate_couples[tmp_couple]) > 1:
                for cell in eval_duplicate_couples[tmp_couple]:
                    cell.possibility = list(tmp_couple)
                break

    def process_duplicates_algo(self,tmp_list):
        # Get duplicates
        duplicate_list = list(filter(lambda x: len(x.possibility) == 2, tmp_list))

        # No duplicates found
        if len(duplicate_list) < 2: return False

        # String possibility
        str_possibility = list(map(lambda x: str(x.possibility), duplicate_list))
        str_possibility = list(set( [x for x in str_possibility if str_possibility.count(x) > 1] ))
        values_possibility = self.flatten_list(list(map(lambda x: eval(x), str_possibility )))

        # Filter duplicates found twice
        duplicate_list = list(filter(lambda x: str(x.possibility) in str_possibility, duplicate_list))

        # Others block
        others_list = list(filter(lambda x: not x in duplicate_list, tmp_list))

        # Filter duplicates values in other couples
        for cell in others_list:
            if cell.value == 0:
                for num_value in values_possibility:
                    if num_value in cell.possibility:
                        cell.possibility.remove(num_value)

        # Filter unique possibility
        others_possibility_values = self.flatten_list(list(map(lambda x: x.possibility, others_list)))
        unique_possibility_values = [x for x in others_possibility_values if others_possibility_values.count(x) == 1]

        for cell in others_list:
            if cell.value == 0 and len(cell.possibility) == 1:
                continue

            if cell.value == 0:
                for possibility_value in unique_possibility_values:
                    if possibility_value in cell.possibility:
                        cell.possibility = [possibility_value]


# def filter_combinations(sudoku_obj,possibility_dict):
#     ret_value = False

#     for block_num in range(9):
#         current_block_tuple = ((block_num%3),int(block_num/3))

#         # Parse each line
#         line_list = list(map(lambda x: x + int(block_num/3)*3, list(range(3))))

#         for line_num in line_list:
#             # Keep possibility in line
#             tmp_list   = list(filter(lambda x: x[0] == line_num, possibility_dict.keys()))
#             tmp_list   = list(filter(lambda x: block_num != int(x[0]/3)*3+int(x[1]/3), tmp_list))

#             # Get values
#             tmp_values = list(map(lambda x: possibility_dict[x], tmp_list))
#             tmp_values = list(set(sudoku_obj.flatten_list(tmp_values)))

#             # Search value not present
#             to_remove_values = list(range(1,10))
#             to_remove_values = list(filter(lambda x: not x in tmp_values, to_remove_values))

#             # Filter num set
#             to_remove_values = list(filter(lambda x: not x in sudoku_obj.get_line(line_num), to_remove_values))
            
#             if len(to_remove_values) == 0: continue

#             # Values not present should be removed in others line in the current block
#             other_line_list = list(filter(lambda x: line_num != x, line_list))

#             for other_line in other_line_list:
#                 # Filter couple to update
#                 update_list = list(filter(lambda x: x[0] == other_line, possibility_dict.keys()))
#                 update_list = list(filter(lambda x: block_num == int(x[0]/3)*3+int(x[1]/3), update_list))
#                 for tmp_couple in update_list:
#                     tmp_len = len(possibility_dict[tmp_couple])
#                     possibility_dict[tmp_couple] = list(filter(lambda x: not x in to_remove_values, possibility_dict[tmp_couple]))
#                     if tmp_len != len(possibility_dict[tmp_couple]):
#                         ret_value = True

#         # Parse each row
#         row_list = list(map(lambda x: x + int(block_num%3)*3, list(range(3))))

#         for row_num in row_list:
#             # Keep possibility in line
#             tmp_list   = list(filter(lambda x: x[1] == row_num, possibility_dict.keys()))
#             tmp_list   = list(filter(lambda x: block_num != int(x[0]/3)*3+int(x[1]/3), tmp_list))

#             # Get values
#             tmp_values = list(map(lambda x: possibility_dict[x], tmp_list))
#             tmp_values = list(set(sudoku_obj.flatten_list(tmp_values)))

#             # Search value not present
#             to_remove_values = list(range(1,10))
#             to_remove_values = list(filter(lambda x: not x in tmp_values, to_remove_values))

#             # Filter num set
#             to_remove_values = list(filter(lambda x: not x in sudoku_obj.get_row(row_num), to_remove_values))
            
#             if len(to_remove_values) == 0: continue

#             # Values not present should be removed in others line in the current block
#             other_row_list = list(filter(lambda x: row_num != x, row_list))

#             for other_row in other_row_list:
#                 # Filter couple to update
#                 update_list = list(filter(lambda x: x[1] == other_row, possibility_dict.keys()))
#                 update_list = list(filter(lambda x: block_num == int(x[0]/3)*3+int(x[1]/3), update_list))
#                 for tmp_couple in update_list:
#                     tmp_len = len(possibility_dict[tmp_couple])
#                     possibility_dict[tmp_couple] = list(filter(lambda x: not x in to_remove_values, possibility_dict[tmp_couple]))
#                     if tmp_len != len(possibility_dict[tmp_couple]):
#                         ret_value = True

#         # TODO in intersection take into account unique possibility

#     return ret_value

    def flatten_list(self,list_example):
        ret_list = list()
        for item in list_example:
            if type(item) == list:
                ret_list += self.flatten_list(item)
            else:
                ret_list.append(item)
        return ret_list

if __name__ == '__main__':

    # tracemalloc.start()

    # test  = sudoku_solver("./examples/example100.json")
    # test  = sudoku_solver("./examples/example1.json")
    test  = sudoku_solver("./examples/example_hardcore.json")
    # test  = sudoku_solver("./examples/example_evil4.json")
    # test  = sudoku_solver("./examples/example_bug.json")
    # test.print_matrix()
    # print('====')

    # print("Problem easy")
    # test  = sudoku_solver(json=[
    #     [9, 4, 1, 0, 3, 0, 7, 0, 0],
    #     [0, 0, 5, 0, 0, 8, 6, 0, 0],
    #     [7, 0, 0, 2, 0, 0, 4, 3, 5],
    #     [0, 1, 0, 0, 5, 0, 0, 4, 3],
    #     [2, 9, 0, 1, 0, 0, 0, 0, 0],
    #     [8, 5, 0, 7, 4, 0, 9, 0, 0],
    #     [1, 3, 8, 9, 0, 6, 0, 0, 0],
    #     [0, 0, 0, 0, 1, 0, 0, 8, 2],
    #     [5, 0, 2, 0, 8, 0, 0, 0, 6],
    # ])

    # print("Problem medium")
    # test  = sudoku_solver(json=[
    #     [0, 5, 3, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 6, 9],
    #     [0, 0, 0, 7, 2, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 9, 8],
    #     [4, 0, 0, 6, 0, 0, 0, 0, 7],
    #     [5, 0, 0, 4, 3, 0, 0, 0, 0],
    #     [0, 0, 2, 5, 0, 6, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 8, 1, 0, 0],
    #     [0, 8, 9, 0, 0, 7, 0, 0, 4]
    # ])

    # print("Problem hard")
    # test  = sudoku_solver(json=[
    #     [0, 8, 0, 0, 0, 4, 0, 5, 0],
    #     [0, 6, 0, 2, 0, 0, 0, 0, 0],
    #     [5, 0, 2, 0, 7, 0, 1, 0, 0],
    #     [0, 0, 6, 0, 0, 0, 0, 0, 0],
    #     [2, 0, 1, 9, 0, 0, 0, 4, 0],
    #     [0, 0, 0, 0, 8, 0, 0, 0, 9],
    #     [0, 0, 0, 0, 0, 3, 7, 0, 0],
    #     [4, 0, 9, 8, 0, 0, 0, 1, 0],
    #     [0, 5, 0, 0, 0, 0, 0, 0, 0]
    # ])

    # print("Problem master class")
    # test  = sudoku_solver(json=[
    #     [8, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 3, 6, 0, 0, 0, 0, 0],
    #     [0, 7, 0, 0, 9, 0, 2, 0, 0],
    #     [0, 5, 0, 0, 0, 7, 0, 0, 0],
    #     [0, 0, 0, 0, 4, 5, 7, 0, 0],
    #     [0, 0, 0, 1, 0, 0, 0, 3, 0],
    #     [0, 0, 1, 0, 0, 0, 0, 6, 8],
    #     [0, 0, 8, 5, 0, 0, 0, 1, 0],
    #     [0, 9, 0, 0, 0, 0, 4, 0, 0]
    # ])

    # test.print_matrix()
    test.run()

    if test.solved and not test.error:
        print('=> Solved')

    else:
        print('=> Not solved')
        print(test.error)

    # snapshot = tracemalloc.take_snapshot()
    # display_top(snapshot)
