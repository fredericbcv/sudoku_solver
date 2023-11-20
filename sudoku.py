#!/usr/bin/python3

import os, sys, json
# from copy import deepcopy, copy
import pickle

class cell(object):
    def __init__(self, line, row):
        self.value       = 0
        self.possibility = list(range(1,10))
        self.line        = line
        self.row         = row
        self.block       = int(line/3) + 3*int(row/3)

class sudoku(object):
    def __init__(self, *args, **kwargs):        
        json_arg=kwargs.get('json', None)

        # Init array
        self.matrix = list()
        for x in range(9):
            for y in range(9):
                self.matrix.append(cell(x,y))

        self.remainder = dict()
        self.possibility = dict()
        for x in range(1,10):
            self.remainder[x] = 9
            self.possibility[x] = 81

        # Load
        if json_arg != None:
            self.load(json_arg)
        elif len(args) > 0:
            with open(args[0],'r') as file:
                json_values = json.loads(file.read())
                self.load(json_values)

        if self.is_error:
            return None

    def load(self,json_content):
        for x in range(9):
            for y in range(9):
                if json_content[x][y] != 0:
                    self.set_value(json_content[x][y],x,y)

    def get_line(self,num_line):
        return self.matrix[9*num_line:9*num_line+9]

    def get_row(self,num_row):
        return [ self.matrix[num_row],
                 self.matrix[num_row+9],
                 self.matrix[num_row+9*2],
                 self.matrix[num_row+9*3],
                 self.matrix[num_row+9*4],
                 self.matrix[num_row+9*5],
                 self.matrix[num_row+9*6],
                 self.matrix[num_row+9*7],
                 self.matrix[num_row+9*8]
                ]

    def get_block(self,num_line,num_row):
        tmp_line = int(num_line/3)
        tmp_row = int(num_row/3)
        return [self.matrix[9*(3*tmp_line)  +(3*tmp_row)],
                self.matrix[9*(3*tmp_line)  +(3*tmp_row)+1],
                self.matrix[9*(3*tmp_line)  +(3*tmp_row)+2],
                self.matrix[9*(3*tmp_line+1)+(3*tmp_row)],
                self.matrix[9*(3*tmp_line+1)+(3*tmp_row)+1],
                self.matrix[9*(3*tmp_line+1)+(3*tmp_row)+2],
                self.matrix[9*(3*tmp_line+2)+(3*tmp_row)],
                self.matrix[9*(3*tmp_line+2)+(3*tmp_row)+1],
                self.matrix[9*(3*tmp_line+2)+(3*tmp_row)+2]
                ]

    def set_value(self, value, num_line, num_row):
        # Set value & possibility
        self.matrix[num_line*9+num_row].value = value
        for tmp_possibility in self.matrix[num_line*9+num_row].possibility:
            self.possibility[tmp_possibility] -= 1
        self.matrix[num_line*9+num_row].possibility = list()
        self.remainder[value] -= 1

        # Update possibility in line
        for line_cell in filter(lambda x: x.value == 0, self.get_line(num_line)):
            if value in line_cell.possibility:
                if len(line_cell.possibility) == 1:
                    raise RuntimeError('Impossible sudoku')
                line_cell.possibility.remove(value)
                self.possibility[value] -= 1

        # Update possibility in row
        for row_cell in filter(lambda x: x.value == 0, self.get_row(num_row)):
            if value in row_cell.possibility:
                if len(row_cell.possibility) == 1:
                    raise RuntimeError('Impossible sudoku')
                row_cell.possibility.remove(value)
                self.possibility[value] -= 1

        # Update possibility in block
        for block_cell in filter(lambda x: x.value == 0, self.get_block(num_line,num_row)):
            if value in block_cell.possibility:
                if len(block_cell.possibility) == 1:
                    raise RuntimeError('Impossible sudoku')
                block_cell.possibility.remove(value)
                self.possibility[value] -= 1

    def get_block_idx(self,num_line,num_row):
        return int(num_line/3) + 3*int(num_row/3)

    def print_matrix(self):
        line = list(map(lambda c: c.value, self.matrix))
        for x in range(9):
            print(str(line[9*x:9*x+3])+" "+str(line[9*x+3:9*x+6])+" "+str(line[9*x+6:9*x+9]) )
            if x % 3 == 2:
                print("")

    def print_remainder(self):
        for x in range(1,10):
            print(str(x)+" "+str(self.remainder[x]))

    def print_possibilities(self):
        for x in range(1,10):
            print(str(x)+" "+str(self.possibility[x]))

    def print_possibility_per_cell(self):
        for x in range(9):
            for y in range(9):
                print( str((x,y))+": "+str(self.matrix[x*9+y].possibility) )

    def copy(self,sudoku_src):
        self.matrix = pickle.loads(pickle.dumps(sudoku_src.matrix))
        self.remainder = pickle.loads(pickle.dumps(sudoku_src.remainder))
        self.possibility = pickle.loads(pickle.dumps(sudoku_src.possibility))

    def get_cell(self,x,y):
        return self.matrix[9*x+y]

    def get_value(self,x,y):
        return self.get_cell(x,y).value

    def is_valid(self):
        for x in range(9):
            if sum(map(lambda x: x.value,self.get_line(x))) != 45:
                return False
        return True

    def is_error(self):
        for x in range(1,10):
            if self.possibility[x] == 0 and self.remainder[x] > 0:
                return True
        return False

    def is_bad_input(self):
        ret_couple = list()

        for num_line in range(9):
            tmp_line = list(filter(lambda x: x.value != 0, self.get_line(num_line)))
            tmp_values = list(map(lambda x: x.value, tmp_line))
            tmp_duplicate = list(set([value for value in tmp_values if tmp_values.count(value) > 1]))
            for cell in tmp_line:
                if cell.value in tmp_duplicate:
                    ret_couple.append((cell.line,cell.row))

        for num_row in range(9):
            tmp_row = list(filter(lambda x: x.value != 0, self.get_row(num_row)))
            tmp_values = list(map(lambda x: x.value, tmp_row))
            tmp_duplicate = list(set([value for value in tmp_values if tmp_values.count(value) > 1]))
            for cell in tmp_row:
                if cell.value in tmp_duplicate:
                    ret_couple.append((cell.line,cell.row))

        for num_block_x in range(3):
            for num_block_y in range(3):
                tmp_block = list(filter(lambda x: x.value != 0, self.get_block(num_block_x*3,num_block_y*3)))
                tmp_values = list(map(lambda x: x.value, tmp_block))
                tmp_duplicate = list(set([value for value in tmp_values if tmp_values.count(value) > 1]))
                for cell in tmp_block:
                    if cell.value in tmp_duplicate:
                        ret_couple.append((cell.line,cell.row))

        return ret_couple

if __name__ == '__main__':
    # test  = sudoku("./examples/example_bug.json")
    test  = sudoku("./examples/example_hardcore.json")
    # test.print_matrix()
    # print(test.is_valid())
    # print(test.is_error())
