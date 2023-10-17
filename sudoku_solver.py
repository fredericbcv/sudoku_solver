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

    # CHECK VALUE
    if 0 != get_value(sudoku,num_tuple):
        return False

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

    # Create unique list
    unique_list = list()
    for tmp_couple in couple_list:
        tmp_block = int(tmp_couple[0]/3)*3+int(tmp_couple[1]/3)

        if block_list.count(tmp_block) == 1:
            unique_list.append(tmp_couple)

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

    return unique_list

def check_num_value_possiblity_by_line(sudoku,couple_list,num_value):
    # Create unique list
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

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

    return unique_list

def check_num_value_possiblity_by_row(sudoku,couple_list,num_value):
    # Create unique list
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

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

    return unique_list

def check_num_value_in_row_n_column(sudoku,couple_list,num_value):
    # Create unique list
    unique_list = list()
    for tmp_couple in couple_list:
        
        # Get line & row
        x,y = tmp_couple
        line = get_line(sudoku,x)
        row = get_row(sudoku,y)
        tmp_list = set(line+row)
        tmp_list.remove(0)

        if len(tmp_list) == 8:
            unique_list.append(tmp_couple)

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

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

    for algo in range(4):
        if algo == 1:
            # Check per line if num is possible in others cases
            unique_list = check_num_value_possiblity_by_line(sudoku,couple_list,num_value)

        elif algo == 2:
            # Check per row if num is possible in others cases
            unique_list = check_num_value_possiblity_by_row(sudoku,couple_list,num_value)

        elif algo == 3:
            # Check if all number are used in row & column
            unique_list = check_num_value_in_row_n_column(sudoku,couple_list,num_value)

        # Filter per block
        if algo == 0:
            unique_list = check_unique_couple_per_block(sudoku,couple_list)
        else:
            unique_list = check_unique_couple_per_block(sudoku,unique_list)

        # Set unique couples
        for unique_couple in unique_list:
            set_value(sudoku, num_value, unique_couple)

        # Update list
        couple_list = list(filter(lambda x: 0 == get_value(sudoku,x), couple_list))
        couple_list = list(filter(lambda x: check_couple_validity(sudoku,num_value,x), couple_list))

        # Set couple if only one left
        if len(couple_list) == 1:
            set_value(sudoku, num_value, couple_list[0])
            couple_list.remove(couple_list[0])
            break

    # Return untreat valid list
    return couple_list

def get_num_per_couples(num_dict):
    # Create new dict
    ret_dict = dict()
    for num_value in num_dict.keys():
        for tmp_couple in num_dict[num_value]:
            if not tmp_couple in ret_dict.keys():
                ret_dict[tmp_couple] = list()
            ret_dict[tmp_couple].append(num_value)

    # Apply unique possibility
    unique_list = list()
    for tmp_couple in ret_dict.keys():
        if len(ret_dict[tmp_couple]) == 1:
            unique_list.append(tmp_couple)
            if get_value(sudoku_list,tmp_couple) == 0:
                set_value(sudoku_list, ret_dict[tmp_couple][0], tmp_couple)

    # Update ret_dict
    for tmp_couple in unique_list:
        ret_dict.pop(tmp_couple)

    return ret_dict

def get_duplicates_num_per_couples(couple_dict):
    # Keep only duplicates num
    tmp_dict = dict()
    for key in couple_dict.keys():
        if len(couple_dict[key]) == 2:
            tmp_dict[key] = couple_dict[key]

    # Reverse keys/values
    reverse_dict = dict()
    for key in tmp_dict.keys():
        if not str(tmp_dict[key]) in reverse_dict.keys():
            reverse_dict[str(tmp_dict[key])] = list()
        reverse_dict[str(tmp_dict[key])].append(key)

    # Keep duplicate num with at least 2 couples possible
    tmp_dict = dict()
    for key in reverse_dict.keys():
        if len(reverse_dict[key]) > 1:
            tmp_dict[key] = reverse_dict[key]

    return tmp_dict

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

        num_dict    = dict()
        # For each num get couples
        for num_value in range(1,10):
            remain_couples = scan_num(sudoku_list,num_value)
            # Save couple possibility for each num
            num_dict[num_value] = remain_couples

        # For each couple get nums possibility
        couple_dict = get_num_per_couples(num_dict)

        # Keep duplicate num
        duplicate_dict = get_duplicates_num_per_couples(couple_dict)

        # Keep couples in the same block
        for key in duplicate_dict.keys():
            # Create new dict to filter per block
            tmp_dict = dict()
            for tmp_couple in duplicate_dict[key]:
                tmp_block = int(tmp_couple[0]/3)*3+int(tmp_couple[1]/3)
                if not tmp_block in tmp_dict.keys():
                    tmp_dict[tmp_block] = list()
                tmp_dict[tmp_block].append(tmp_couple)

            # Keep element which have at least 2 couple
            keep_list = list()
            for key in tmp_dict.keys():
                if len(tmp_dict[key]) > 1:
                    keep_list.append(tmp_dict[key])

            for item in keep_list:
                print(str(item)+"   "+str(couple_dict[item[0]] ) )


        #for key in couple_dict.keys():
        #    print(str(key)+": "+str(couple_dict[key]))

        #print('----')

        #for key in duplicate_dict.keys():
        #    print(str(key)+": "+str(duplicate_dict[key]))



        # Check triplet per block

        # Check combinaison



        print('--------------------------------')
        print_sudoku(sudoku_list)
        print_remain_values(sudoku_list)
        print("")

        # Check if remain_values
        tmp_dict = get_remain_values(sudoku_list)
        if sum(tmp_dict.values()) == 0:
            break