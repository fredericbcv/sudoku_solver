#!/usr/bin/python3

import os, sys
from sudoku     import *
from random     import *
from itertools  import product

class sudoku_solver(sudoku):
    def __init__(self, *args, **kwargs):
        super(sudoku_solver, self).__init__(*args, **kwargs)
        self.solved = False
        self.error  = False

    def run(self):
        # print('run')

        # self.print_matrix()
        # self.print_possibility()

        # Run Solver
        self.solver()

        # Solved or Error ?
        if self.solved:
            # print('solved')
            return

        if self.error:
            # print('error')
            return

        # No solution found
        else:
            # print('No solution found')

            cells = map(lambda x: x, self.flatten_list(self.line_matrix) )
            cells = list(filter(lambda x: x.value == 0, cells))
            possibility_len = list(map(lambda x: len(x.possibility), cells))

            if len(possibility_len) == 0:
                self.error = True
                return

            # For each possiblity len
            for tmp_len in range(min(possibility_len),max(possibility_len)+1):
                possibility_list = list(filter(lambda x: len(x.possibility) == tmp_len, cells))

                # For each cells with specific possibility len
                for tmp_cell in possibility_list:

                    # For each possibility value
                    for tmp_value in tmp_cell.possibility:
                        # print(tmp_value)

                        # Copy sudoku
                        tmp_sudoku = deepcopy(self)

                        # Set value
                        tmp_sudoku.set_value(tmp_value,tmp_cell.couple)

                        # print('couple: '+str(tmp_cell.couple))
                        # print('value:  '+str(tmp_value))
                        # tmp_sudoku.print_matrix()
                        # print('----')

                        # Run solver
                        tmp_sudoku.run()

                        if tmp_sudoku.error:
                            continue

                        if tmp_sudoku.solved:
                            self.copy(tmp_sudoku)
                            self.solved = True
                            return

            # self.print_matrix()
            # self.print_possibility()
            # self.print_remain_values()
            # print('----')

    def solver(self):
        retry = False

        while True:
            if not self.is_valid()[0]:
                self.error = True
                return

            # Check remain vs possiblity
            # possibility_values = self.flatten_list(list(map(lambda x: x.possibility, self.flatten_list(self.line_matrix))))
            # possibility_values = list(set(possibility_values))
            # for num_value in self.get_remain_values():
            #     if self.remain[num_value] > 0 and not num_value in possibility_values:
            #         self.error = True
            #         return

            # print('process_unique')
            retry = self.process_unique()
            if self.error: return
            if retry: continue

            # print('process_duplicates')
            retry = self.process_duplicates()
            if self.error: return
            if retry: continue

            # retry = self.filter_combinations()
            # if retry: continue
            # if self.error: return

            break

        # Solved ?
        if list(self.get_remain_values().values()).count(0) == 9:
            self.solved = self.is_valid()[0]

    def process_unique(self):
        ret_value = False

        # List unique possibility
        unique_cells = list(filter(lambda x: len(x.possibility) == 1, self.flatten_list(self.line_matrix)))
        unique_cells = list(filter(lambda x: x.value == 0, unique_cells))

        # Unique in intersection
        for cell in unique_cells:

            if len(cell.possibility) == 0:
                self.error = True
                return False

            cell_intersection  = list()
            cell_intersection += self.get_line(cell.couple[0])
            cell_intersection += self.get_row(cell.couple[1])
            cell_intersection += self.get_block(cell.block_idx)
            cell_intersection  = list(map(lambda x: x.value, cell_intersection))

            # Is value already set ?
            if cell.possibility[0] in cell_intersection:
                self.error = True
                return False

            # Set value
            self.set_value(cell.possibility[0],cell.couple)
            ret_value = True

        return ret_value

    def process_duplicates(self):
        ret_value = False

        # Filter
        for block_num in range(9):
            self.filter_duplicates(self.get_block(block_num))
            if self.process_duplicates_algo(self.get_block(block_num)): return True
        for line_num in range(9):
            self.filter_duplicates(self.get_line(line_num))
            if self.process_duplicates_algo(self.get_line(line_num)): return True
        for row_num in range(9):
            self.filter_duplicates(self.get_row(row_num))
            if self.process_duplicates_algo(self.get_row(row_num)): return True

        return False

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
                ret_value = True
                for cell in eval_duplicate_couples[tmp_couple]:
                    cell.possibility = list(tmp_couple)
                break

    def process_duplicates_algo(self,tmp_list):
        ret_value = False

        # Get duplicates
        duplicate_list = list(filter(lambda x: len(x.possibility) == 2, tmp_list))

        # No duplicates found
        if len(duplicate_list) < 2: return False

        # String possibility
        str_possibility = list(map(lambda x: str(x.possibility), duplicate_list))
        str_possibility = list(set(self.get_duplicates(str_possibility)))
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
                ret_value = True
                continue

            if cell.value == 0:
                for possibility_value in unique_possibility_values:
                    if possibility_value in cell.possibility:
                        cell.possibility = [possibility_value]
                        ret_value = True

        return ret_value

if __name__ == '__main__':
    test  = sudoku_solver("./examples/example_evil4.json")

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

    test.print_matrix()
    test.run()

    if test.solved and not test.error:
        print(test.is_valid())
        test.print_remain_values()
        print('=> Solved')
        test.print_matrix()

        print(test.is_valid())

    else:
        print('=> Not solved')
        test.print_matrix()
        # test.print_possibility()
        # print('caca')
        # test.print_remain_values()


        # possibility_values = test.flatten_list(list(map(lambda x: x.possibility, test.flatten_list(test.line_matrix))))
        # possibility_values = list(set(possibility_values))

        # print(possibility_values)

        # for num_value in test.get_remain_values():
        #     if test.remain[num_value] > 0 and not num_value in possibility_values:
        #         print(num_value)
        #         break
