#!/usr/bin/python3

import os, sys, json
from sudoku2 import *

for root, dirs, files in os.walk('./tests/', topdown=False):
    for name in files:
        file_path = os.path.join(root, name)
        print(file_path)

        test = sudoku(file_path)

        test.print_matrix()

        wr_file = open(file_path+".bak", 'w')
        wr_file.write('[\n')
        
        for x in range(9):
            wr_file.write('    '+str(test.get_line(x)))
            if x < 8:
                wr_file.write(',')

            wr_file.write('\n')

        wr_file.write(']\n')




