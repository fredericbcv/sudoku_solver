#!/usr/bin/python3

import os, sys
from sudoku import *
from solver import *

def generic_test(filename,num_tuple,num_value,print_matrix=True):
    sudoku_obj = sudoku_solver(filename)
    sudoku_obj.run()
    if sudoku_obj.matrix[num_tuple[0]*9+num_tuple[1]].value == num_value: 
        print('  => OK')
    else: 
        print('  => KO')

    sudoku_obj.print_matrix()

if __name__ == '__main__':
    print('TEST1: Scan')
    generic_test("./tests/example_scan.json",(1,6),1)

    print('TEST2: Filling1')
    generic_test("./tests/example_filling1.json",(0,7),9)

    print('TEST3: Filling2')
    generic_test("./tests/example_filling2.json",(0,7),9)

    print('TEST4: Intersection1')
    generic_test("./tests/example_intersection1.json",(3,2),3)

    print('TEST5: Ghost1')
    generic_test("./tests/example_ghost1.json",(0,7),9)

    print('TEST6: Duplicates1')
    generic_test("./tests/example_duplicates1.json",(1,4),2)

    print('TEST7: Duplicates2')
    generic_test("./tests/example_duplicates2.json",(4,4),1)

    print('TEST8: Duplicates3')
    generic_test("./tests/example_duplicates3.json",(8,0),9)

    print('TEST9: Triplet')
    generic_test("./tests/example_triplet.json",(0,2),1)

    print('TEST10: Combinations1')
    generic_test("./tests/example_combinations1.json",(6,8),2)

    print('TEST11: Combinations2')
    generic_test("./tests/example_combinations2.json",(8,6),8)

    print('TEST12: Combinations3')
    generic_test("./tests/example_combinations3.json",(0,8),1)
