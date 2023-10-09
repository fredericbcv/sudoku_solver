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
    if num_value in tmp_block:
        return False

    # CHECK ROW
    tmp_row = get_row(sudoku,num_tuple[1])
    if num_value in tmp_block:
        return False

    # ELSE
    return True

# def check_value(sudoku,num_value,num_tuple):
#     # Return true by default
#     # Check only wrong cases
# 
# 
#     # Get positions
#     block_line = int(num_tuple[0]/3)
#     block_row  = int(num_tuple[1]/3)
#     relative_line = num_tuple[0]%3
#     relative_row  = num_tuple[1]%3
# 
#     # CHECK BLOCK
#     tmp_block = flatten_list(get_block(sudoku,block_line,block_row))
#     if num_value in tmp_block:
#         return False
#     if tmp_block.count(0) == 1:
#         return True
# 
#     # CHECK LINES
#     valid_line = 0
#     block_lines = list(range(3))
#     block_lines.remove(relative_line)
# 
#     # Get row
#     tmp_row   = get_block(sudoku,block_line,block_row)
#     tmp_row   = list(map(lambda x: x[relative_row],tmp_row))
# 
#     for num_line in block_lines:
#         # Is other lines occupied in the same block ?
#         if 0 != tmp_row[num_line]:
#             valid_line += 1
#             continue
# 
#         # Is other lines occupied in the complete line ? 
#         if num_value in get_line(sudoku,block_line*3+num_line):
#             valid_line += 1
# 
#     # Cannot decide, skip couple
#     if valid_line != 2:
#         return False
# 
#     # CHECK ROWS
#     valid_row = 0
#     block_rows = list(range(3))
#     block_rows.remove(relative_row)
# 
#     # Get line
#     tmp_line = get_block(sudoku,block_line,block_row)[relative_line]
# 
#     for num_row in block_rows:
#         # Is other rows occupied in the same block ?
#         if 0 != tmp_line[num_row]:
#             valid_row += 1
#             continue
# 
#         # Is other rows occupied in the complete line ?
#         if num_value in get_row(sudoku,block_row*3+num_row):
#             valid_row += 1
# 
#     # If cannot decide, skip couple
#     if valid_row != 2:
#         return False
#     else:
#         return True

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
    block_list  = list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), couple_list))

    # Keep unique possibility per block
    unique_list = list()
    for tmp_couple in couple_list:
        tmp_block = int(tmp_couple[0]/3)*3+int(tmp_couple[1]/3)
        if block_list.count(tmp_block) == 1:
            unique_list.append(tmp_couple)
            couple_list.remove(tmp_couple)

    # Set unique couples
    for unique_couple in unique_list:
        set_value(sudoku, num_value, unique_couple)

    # Set couple if only one left
    if len(couple_list) == 1:
        set_value(sudoku, num_value, couple_list[0])
        couple_list.remove(couple_list[0])

    if num_value == 1:
        print(couple_list)

    # Return untreat valid list
    return len(couple_list)

    #print(couple_list)
    #print(block_list)
    #print(unique_list)
    #print('***')

#    print(couple_list)
#    print(list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), couple_list)))

#    # Treat unique couples
#    for x in range(len(couple_list)):
#        # Check couple validity
#        tmp_list   = list(filter(lambda x: check_value(sudoku,num_value,x),couple_list))
#        block_list = list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), tmp_list))
#
#        print(tmp_list)
#        print(block_list)
#        print('$')
#
#        # Keep unique couples per block
#        unique_list = list()
#
#        for tmp_couple in tmp_list:
#            tmp_block = int(tmp_couple[0]/3)*3+int(tmp_couple[1]/3)
#            if block_list.count(tmp_block) == 1:
#                unique_list.append(tmp_couple)
#
#        print(unique_list)
#        print('---')
#
#        # Apply values & update couple_list
#        for valid_couple in unique_list:
#            set_value(sudoku, num_value, valid_couple)
#            couple_list.remove(valid_couple)
#
#        break


        # for tmp_couple in tmp_list:
        #   tmp_list2 = deepcopy(tmp_list)
        #   tmp_list2.remove(tmp_couple)
            
        #   # Get position
        #   tmp_x = tmp_couple[0]
        #   tmp_y = tmp_couple[1]
        #   tmp_block = int(tmp_x/3)*3+int(tmp_y/3)
            
        #   # Check block
        #   #block_unique = False
        #   #if not tmp_block in list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), tmp_list2)):
        #   #   block_unique = True

        #   # Alone in block ?
        #   #if num_value == 9:
        #   #   print(tmp_block)
        #   if list(map(lambda x: int(x[0]/3)*3+int(x[1]/3), tmp_list)).count(tmp_block) == 1:
        #       valid_list.append(tmp_couple)
        #       continue

        #   x_unique = False
        #   if not tmp_x in list(map(lambda x: x[0],tmp_list2)):
        #       x_unique = True

        #   y_unique = False
        #   if not tmp_y in list(map(lambda x: x[1],tmp_list2)):
        #       y_unique = True

        #   if x_unique and y_unique:
        #       valid_list.append(tmp_couple)

        # if len(valid_list) == 0:
        #   break

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
        for x in range(1,10):
            previous_remain = 0
            # Scan num at most 9 times
            for retry in range(9):
                remain_values = scan_num(sudoku_list,x)
                if remain_values == 0:
                    break
                # current remain = last remain
                if retry > 0:
                    if previous_remain  == remain_values:
                        break
                # Save remain
                previous_remain = remain_values

        tmp_dict = get_remain_values(sudoku_list)
        if sum(tmp_dict.values()) == 0:
            break

    print('--------------------------------')
    print_sudoku(sudoku_list)
    print_remain_values(sudoku_list)
    print("")
