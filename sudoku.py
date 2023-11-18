#!/usr/bin/python3

import os, sys, json
from copy import deepcopy

# TODO
# One big array rather a double array
# Use array vs list ?
# Counter possibility
# options_counter a implementer détecte directement les doublons

class cell(object):
    def __init__(self, couple):
        self.value = 0
        self.possibility = list(range(1,10))
        self.couple = couple
        self.block_idx = int(couple[0]/3) + 3*int(couple[1]/3)

class sudoku(object):
    def __init__(self, *args, **kwargs):        
        json_arg=kwargs.get('json', None)

        # Init
        self.line_matrix  = [ [cell((x,y)) for y in range(9)] for x in range(9) ]

        self.row_matrix = list()
        for y in range(9):
            self.row_matrix.append(list(map(lambda line: line[y], self.line_matrix)))

        self.block_matrix = list()
        for block in range(9):
            self.block_matrix.append(list())
        for x in range(9):
            for y in range(9):
                self.block_matrix[int(x/3) + int(y/3)*3].append( self.line_matrix[x][y] )

        self.remain = dict()
        for num in range(1,10):
            self.remain[num] = 9

        self.line_possibility = [ list(range(1,10)) for x in range(9) ]

        # Load
        if json_arg != None:
            self.load(json_arg)
        elif len(args) > 0:
            with open(args[0],'r') as file:
                json_values = json.loads(file.read())
                self.load(json_values)

        # Check feasability
        return self.check_feasability()

    def check_feasability(self):
        # Check remain vs possiblity
        for num_value in self.get_remain_values():
            # Ignore is all num set
            if self.remain[num_value] == 0:
                continue

            # Line without possiblity
            for line_num in range(9):
                if not num_value in self.line_possibility[line_num]:
                    continue

                # Check possibility conflict
                tmp_possiblity = self.flatten_list(list(map(lambda x: x.possibility, self.line_matrix[line_num])))
                if not num_value in tmp_possiblity:
                    return False


            # for tmp_list in [self.get_line(num_idx),self.get_row(num_idx),self.get_block(num_idx)]:
            #     num_values       = list(map(lambda x: x.value, tmp_list))
            #     num_values       = list(filter(lambda x: x != 0, num_values))
            #     duplicates_list += self.get_duplicates(num_values)

            #     # Update possibility
            #     possibility_list = self.flatten_list(list(map(lambda x: x.possibility, tmp_list)))
            #     possibility_list = [x for x in possibility_list if possibility_list.count(x) == 1]
                
            #     for cell in tmp_list:
            #         for unique_possibility in possibility_list:
            #             if unique_possibility in cell.possibility:
            #                 cell.possibility = [unique_possibility]

            #     if return_duplicates:
            #         for num_row in range(9):
            #             if self.get_value((num_line,num_row)) in duplicates_list:
            #                 ret_list.append((num_line,num_row))


        return True

    def print_matrix(self,matrix_type="line"):
        if matrix_type == "line":
            matrix = self.line_matrix
        else:
            matrix = self.row_matrix

        for i, item in enumerate(matrix):
            item_values = list(map(lambda x: x.value,item))
            print(str(item_values[:3])+" "+str(item_values[3:6])+" "+str(item_values[6:9]) )
            if i % 3 == 2:
                print("")

    def print_possibility(self):
        for x in range(9):
            for y in range(9):
                print( str((x,y))+": "+str(self.line_matrix[x][y].possibility) )

    def print_remain_values(self,):
        print("Remain values:")
        remain_values = self.get_remain_values()
        for key in remain_values:
            print("  * "+str(key)+": "+str(remain_values[key]))

    def load(self,json_content):
        for x in range(9):
            for y in range(9):
                if json_content[x][y] != 0:
                    self.set_value(json_content[x][y], (x,y))

    def get_duplicates(self, num_values):
        return [x for x in num_values if num_values.count(x) > 1]

    def is_valid(self,return_duplicates=False):
        for num_idx in range(9):
            if sum(list(map(lambda x: x.value, self.get_line(num_idx)))) != 45 :
                return False
        return True

    def get_line(self,num_line):
        return self.line_matrix[num_line]

    def get_row(self,num_row):
        return self.row_matrix[num_row]

    def get_block(self,num_block):
        return self.block_matrix[num_block]

    def get_cell(self,num_tuple):
        num_line,num_row = num_tuple
        return self.line_matrix[num_line][num_row]

    def set_value(self,num_value,num_tuple):
        self.remain[num_value] -= 1

        num_line,num_row = num_tuple
        self.line_matrix[num_line][num_row].value = num_value

        # Update possibility
        for x_case in list(filter(lambda x: x.value == 0, self.get_line(num_line))):
            if num_value in x_case.possibility:
                if len(x_case.possibility) == 1: raise RuntimeError('Impossible sudoku')
                x_case.possibility.remove(num_value)
        for y_case in list(filter(lambda x: x.value == 0, self.get_row(num_row))):
            if num_value in y_case.possibility:
                if len(y_case.possibility) == 1: raise RuntimeError('Impossible sudoku')
                y_case.possibility.remove(num_value)
        for b_case in list(filter(lambda x: x.value == 0, self.get_block( self.line_matrix[num_line][num_row].block_idx ))):
            if num_value in b_case.possibility:
                if len(b_case.possibility) == 1: raise RuntimeError('Impossible sudoku')
                b_case.possibility.remove(num_value)

        # Clear possiblity
        self.line_matrix[num_line][num_row].possibility  = list()

        # Update possiblity line
        if num_value in self.line_possibility[num_line]:
            self.line_possibility[num_line].remove(num_value)

    def flatten_list(self,list_example):
        ret_list = list()
        for item in list_example:
            if type(item) == list:
                ret_list += self.flatten_list(item)
            else:
                ret_list.append(item)
        return ret_list

    def get_remain_values(self,):
        return self.remain

    def copy(self,matrix_to_copy):
        self.remain           = deepcopy(matrix_to_copy.remain)
        self.line_possibility = deepcopy(matrix_to_copy.line_possibility)

        self.line_matrix  = deepcopy(matrix_to_copy.line_matrix)
        
        self.row_matrix   = list()
        for y in range(9):
            self.row_matrix.append(list(map(lambda line: line[y], self.line_matrix)))

        self.block_matrix = list()
        for block in range(9):
            self.block_matrix.append(list())
        for x in range(9):
            for y in range(9):
                self.block_matrix[int(x/3) + int(y/3)*3].append( self.line_matrix[x][y] )

if __name__ == '__main__':
    test  = sudoku("./examples/example_hardcore.json")
    test.print_matrix("line")
    print(test.is_valid())

    test.print_possibility()
    test.print_remain_values()
