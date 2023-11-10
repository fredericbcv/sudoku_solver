#!/usr/bin/python3

import os, sys, json
from copy import deepcopy


class cell(object):
    def __init__(self, *args, **kwargs):
        self.value = 0
        self.possibility = list(range(1,10))

class sudoku(object):
    def __init__(self, *args, **kwargs):
        json_file=kwargs.get('json_file', None)

        # Init
        self.line_matrix  = [ [cell() for y in range(9)] for x in range(9) ]
        
        self.row_matrix = list()
        for y in range(9):
            self.row_matrix.append(list(map(lambda line: line[y], self.line_matrix)))

        self.block_matrix = dict()
        for block in range(9):
            self.block_matrix[block] = list()
        for x in range(9):
            for y in range(9):
                self.block_matrix[int(x/3) + int(y/3)*3].append( self.line_matrix[x][y] )

        self.num_counter = dict()
        for num in range(1,10):
            self.num_counter[num] = 9

        # Load
        if len(args) > 0:
            self.load(args[0])
        elif json_file != None:
            self.load(file)

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

    def load(self,json_file):
        with open(json_file,'r') as file:
            json_values = json.loads(file.read())

            for x in range(9):
                for y in range(9):
                    if json_values[x][y] != 0:
                        self.set_value(json_values[x][y], (x,y))

    def get_duplicates(self, num_values):
        return [x for x in num_values if num_values.count(x) > 1]

    def is_valid(self,return_duplicates=False):
        duplicates_list = list()
        ret_list = list()

        # Check lines
        for num_line in range(9):
            num_values       = list(map(lambda x: x.value, self.get_line(num_line)))
            num_values       = list(filter(lambda x: x != 0, num_values))
            duplicates_list += self.get_duplicates(num_values)

            if return_duplicates:
                for num_row in range(9):
                    if self.get_value((num_line,num_row)) in duplicates_list:
                        ret_list.append((num_line,num_row))

        # Check rows
        for num_row in range(9):
            num_values       = list(map(lambda x: x.value, self.get_row(num_row)))
            num_values       = list(filter(lambda x: x != 0, num_values))
            duplicates_list += self.get_duplicates(num_values)

            if return_duplicates:
                for num_line in range(9):
                    if self.get_value((num_line,num_row)) in duplicates_list:
                        ret_list.append((num_line,num_row))

        # Check block
        for num_block in range(9):
            num_values       = list(map(lambda x: x.value, self.block_matrix[num_block]))
            num_values       = list(filter(lambda x: x != 0, num_values))
            duplicates_list += self.get_duplicates(num_values)

            if return_duplicates:
                for i, case in enumerate(self.block_matrix[num_block]):
                    if case.value in duplicates_list:
                        ret_list.append( self.get_block_couple(num_block,i) )

        if len(duplicates_list) == 0:
            return True,None
        else:
            return False,ret_list

    def get_block_couple(self, block_num, block_index):
        if   block_num == 0:
            x, y = 0,0
        elif block_num == 1:
            x, y = 0,3
        elif block_num == 2:
            x, y = 0,6
        elif block_num == 3:
            x, y = 3,0
        elif block_num == 4:
            x, y = 3,3
        elif block_num == 5:
            x, y = 3,6
        elif block_num == 6:
            x, y = 6,0
        elif block_num == 7:
            x, y = 6,3
        elif block_num == 8:
            x, y = 6,6

        x += int(block_index / 3)
        y += block_index % 3

        return (x,y)

    def get_line(self,num_line):
        return self.line_matrix[num_line]

    def get_row(self,num_row):
        return self.row_matrix[num_row]

    def get_block(self,num_line,num_row):
        block_num = int(num_line/3) + 3*int(num_row/3)
        return self.block_matrix[block_num]

    def get_value(self,num_tuple):
        num_line,num_row = num_tuple
        return self.line_matrix[num_line][num_row]

    def set_value(self,num_value,num_tuple):
        self.num_counter[num_value] -= 1

        num_line,num_row = num_tuple
        self.line_matrix[num_line][num_row].value = num_value

        # Update possibility
        for x_case in self.get_line(num_line):
            if num_value in x_case.possibility:
                x_case.possibility.remove(num_value)
        for y_case in self.get_row(num_row):
            if num_value in y_case.possibility:
                y_case.possibility.remove(num_value)
        for b_case in self.get_block(num_line,num_row):
            if num_value in b_case.possibility:
                b_case.possibility.remove(num_value)

        self.line_matrix[num_line][num_row].possibility  = list()

    def flatten_list(self,list_example):
        ret_list = list()
        for item in list_example:
            if type(item) == list:
                ret_list += self.flatten_list(item)
            else:
                ret_list.append(item)
        return ret_list

    def get_remain_values(self,):
        return self.num_counter

    def copy(self,matrix_to_copy):
        self.line_matrix  = deepcopy(matrix_to_copy.line_matrix)
        self.row_matrix   = deepcopy(matrix_to_copy.row_matrix)
        self.block_matrix = deepcopy(matrix_to_copy.block_matrix)

if __name__ == '__main__':
    test  = sudoku("./example_hardcore2.json")
    test.print_matrix("line")
    print(test.is_valid())

    test.print_possibility()
    test.print_remain_values()
