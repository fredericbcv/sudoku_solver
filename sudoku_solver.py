#!/usr/bin/python3

import os, sys, json, argparse
from itertools import product
from copy import deepcopy

def get_block(sudoku,num_line,num_row):
    return sudoku[num_line][num_row]

def get_row(sudoku,num_row):
    tmp_list = list()

    x = int(num_row/3)
    y = num_row%3

    for idx in range(3):
        for subitem in sudoku[idx][x]:
            tmp_list.append(subitem[y])

    return tmp_list

def get_line(sudoku,num_line):
    tmp_list = list()

    x = int(num_line/3)
    y = num_line%3

    for item in sudoku[x]:
        tmp_list += item[y]
    
    return tmp_list

def get_value(sudoku,num_tuple):
    num_line,num_row = num_tuple
    tmp_line = get_line(sudoku,num_line)
    return tmp_line[num_row]

def set_value(sudoku,num_value,num_tuple):
    num_line,num_row = num_tuple
    sudoku[int(num_line/3)][int(num_row/3)][int(num_line%3)][int(num_row%3)] = num_value

def check_couple_validity(sudoku,num_value,num_tuple):
    # Get positions
    block_line = int(num_tuple[0]/3)
    block_row  = int(num_tuple[1]/3)
    relative_line = num_tuple[0]%3
    relative_row  = num_tuple[1]%3

    # CHECK BLOCK
    tmp_block = flatten_list(get_block(sudoku,block_line,block_row))
    if num_value in tmp_block:
        return False

    # CHECK LINE
    tmp_line = get_line(sudoku,num_tuple[0])
    if num_value in tmp_line:
        return False

    # CHECK ROW
    tmp_row = get_row(sudoku,num_tuple[1])
    if num_value in tmp_row:
        return False

    # ELSE
    return True

def check_unique_couple_per_block(sudoku,couple_list):
    block_list  = list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), couple_list))
    unique_list = list()
    for tmp_couple in couple_list:
        tmp_block = int(tmp_couple[0]/3)*3+int(tmp_couple[1]/3)
        if block_list.count(tmp_block) == 1:
            unique_list.append(tmp_couple)
            couple_list.remove(tmp_couple)

    return unique_list

def check_unique_couple_per_line(sudoku,couple_list,num_value):
    unique_list = list()
    for tmp_couple in couple_list:
        x,y  = tmp_couple
        line = get_line(sudoku,x)

        count_validity = 0
        for row_idx, row_value in enumerate(line):
            if row_value == 0 and row_idx != y:
                if check_couple_validity(sudoku, num_value, (x,row_idx)):
                    count_validity += 1

        if count_validity == 0:
            unique_list.append(tmp_couple)
            couple_list.remove(tmp_couple)

    return unique_list

def check_unique_couple_per_row(sudoku,couple_list,num_value):
    unique_list = list()
    for tmp_couple in couple_list:
        x,y = tmp_couple
        row = get_row(sudoku,y)

        count_validity = 0
        for line_idx, line_value in enumerate(row):
            if line_value == 0 and line_idx != x:
                if check_couple_validity(sudoku, num_value, (line_idx,y)):
                    count_validity += 1

        if count_validity == 0:
            unique_list.append(tmp_couple)
            couple_list.remove(tmp_couple)

    return unique_list

def scan_num(sudoku,num_value):
    # Search potential line
    x_list = list()
    for x in range(9):
        if not num_value in get_line(sudoku,x):
            x_list.append(x)

    # Search potential row
    y_list = list()
    for y in range(9):
        if not num_value in get_row(sudoku,y):
            y_list.append(y)

    # Get all couple
    couple_list = list(product(x_list,y_list))

    # Filter couple available
    couple_list = list(filter(lambda x: 0 == get_value(sudoku,x), couple_list))
    couple_list = list(filter(lambda x: check_couple_validity(sudoku,num_value,x), couple_list))

    for algo in range(3):
        if   algo == 0:
            # Filter per block
            unique_list = check_unique_couple_per_block(sudoku,couple_list)
        
        elif algo == 1:
            # Check per line if num is possible in others cases
            unique_list = check_unique_couple_per_line(sudoku,couple_list,num_value)
            # Filter per block
            unique_list = check_unique_couple_per_block(sudoku,unique_list)

        elif algo == 2:
            # Check per row if num is possible in others cases
            unique_list = check_unique_couple_per_row(sudoku,couple_list,num_value)
            # Filter per block
            unique_list = check_unique_couple_per_block(sudoku,unique_list)

        # Set unique couples
        for unique_couple in unique_list:
            set_value(sudoku, num_value, unique_couple)

        # Update list
        couple_list = list(filter(lambda x: check_couple_validity(sudoku,num_value,x), couple_list))

        # Set couple if only one left
        if len(couple_list) == 1:
            set_value(sudoku, num_value, couple_list[0])
            couple_list.remove(couple_list[0])
            return couple_list

    # Return untreat valid list
    return couple_list

def flatten_list(sudoku):
    ret_list = list()
    for item in sudoku:
        if type(item) == list:
            ret_list += flatten_list(item)
        else:
            ret_list.append(item)
    return ret_list

def get_remain_values(sudoku):
    flat_list = flatten_list(sudoku)
    ret_dict = dict()
    for x in range(1,10):
        ret_dict[x] = 9 - flat_list.count(x)
    return ret_dict

def print_remain_values(sudoku):
    print("Remain values:")
    flat_list = flatten_list(sudoku)
    for x in range(1,10):
        print("  * "+str(x)+" = "+str(9-flat_list.count(x)))

def print_sudoku(sudoku):
    for line in sudoku:
        for x in range(3):
            print(str(line[0][x]) + "  " + str(line[1][x]) + "  " + str(line[2][x]) )
        print("")

def get_args():
    parser = argparse.ArgumentParser(
        description="Sudoku solver"
    )
    parser.add_argument('file')
    parser.add_argument('-i', '--iteration',type=int,default=15)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    # Read json file
    with open(args.file,'r') as file:
        file_content = file.read()

    # Load json file
    sudoku_list = json.loads(file_content)

    print("Initial Matrix")
    print_sudoku(sudoku_list)
    print_remain_values(sudoku_list)

    for i in range(args.iteration):
        print('--------------------------------')
        print('Iteration {}:'.format(i))

        # For each num
        for num in range(1,10):
            remain_values = scan_num(sudoku_list,num)

        print('--------------------------------')
        print_sudoku(sudoku_list)
        print_remain_values(sudoku_list)
        print("")

        # Check if remain_values
        tmp_dict = get_remain_values(sudoku_list)
        if sum(tmp_dict.values()) == 0:
            break