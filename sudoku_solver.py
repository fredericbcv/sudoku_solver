#!/usr/bin/python3

import os, sys, json, argparse
from itertools import product
from copy import deepcopy

################################################################
#
# ########     ###     ######  ####  ######
# ##     ##   ## ##   ##    ##  ##  ##    ##
# ##     ##  ##   ##  ##        ##  ##
# ########  ##     ##  ######   ##  ##
# ##     ## #########       ##  ##  ##
# ##     ## ##     ## ##    ##  ##  ##    ##
# ########  ##     ##  ######  ####  ######
#
################################################################
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

def get_num_per_couples(num_dict):
    # Create new dict
    ret_dict = dict()
    for num_value in num_dict.keys():
        for tmp_couple in num_dict[num_value]:
            if not tmp_couple in ret_dict.keys():
                ret_dict[tmp_couple] = list()
            ret_dict[tmp_couple].append(num_value)
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

################################################################
#
#  ######  ##     ## ########  ######  ##    ##
# ##    ## ##     ## ##       ##    ## ##   ##
# ##       ##     ## ##       ##       ##  ##
# ##       ######### ######   ##       #####
# ##       ##     ## ##       ##       ##  ##
# ##    ## ##     ## ##       ##    ## ##   ##
#  ######  ##     ## ########  ######  ##    ##
#
################################################################
def check_is_num_exist_for_tuple(sudoku,num_value,num_tuple):
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

################################################################
#
#  ######   ######     ###    ##    ##         ##    ## ##     ## ##     ##
# ##    ## ##    ##   ## ##   ###   ##         ###   ## ##     ## ###   ###
# ##       ##        ##   ##  ####  ##         ####  ## ##     ## #### ####
#  ######  ##       ##     ## ## ## ##         ## ## ## ##     ## ## ### ##
#       ## ##       ######### ##  ####         ##  #### ##     ## ##     ##
# ##    ## ##    ## ##     ## ##   ###         ##   ### ##     ## ##     ##
#  ######   ######  ##     ## ##    ## ####### ##    ##  #######  ##     ##
#
################################################################
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
    couple_list = list(filter(lambda x: check_is_num_exist_for_tuple(sudoku,num_value,x), couple_list))

    # Return untreat valid list
    return couple_list

################################################################
#
# ##     ## ##    ## ####  #######  ##     ## ######## 
# ##     ## ###   ##  ##  ##     ## ##     ## ##       
# ##     ## ####  ##  ##  ##     ## ##     ## ##       
# ##     ## ## ## ##  ##  ##     ## ##     ## ######   
# ##     ## ##  ####  ##  ##  ## ## ##     ## ##       
# ##     ## ##   ###  ##  ##    ##  ##     ## ##       
#  #######  ##    ## ####  ##### ##  #######  ######## 
#
################################################################
def process_unique_per_num(sudoku,num_value,couple_list):
    ret_value = False

    for algo in range(4):
        if algo == 1:
            # Check per line if num is possible in others cases
            unique_list = process_unique_per_line(sudoku,couple_list,num_value)

        elif algo == 2:
            # Check per row if num is possible in others cases
            unique_list = process_unique_per_row(sudoku,couple_list,num_value)

        elif algo == 3:
            # Check if all number are used in row & column
            unique_list = process_unique_per_line_and_row(sudoku,couple_list,num_value)

        # Filter per block
        if algo == 0:
            unique_list = process_unique_per_block(sudoku,couple_list)
        else:
            unique_list = process_unique_per_block(sudoku,unique_list)

        # Set unique couples
        for unique_couple in unique_list:
            ret_value = True
            set_value(sudoku, num_value, unique_couple)

        # Update list
        couple_list = list(filter(lambda x: check_is_num_exist_for_tuple(sudoku,num_value,x), couple_list))

        # Set couple if only one left
        if len(couple_list) == 1:
            set_value(sudoku, num_value, couple_list[0])
            couple_list.remove(couple_list[0])
            break

    return ret_value, couple_list

def process_unique_per_line(sudoku,couple_list,num_value):
    # Create unique list
    unique_list = list()
    for tmp_couple in couple_list:
        x,y  = tmp_couple
        line = get_line(sudoku,x)

        count_validity = 0
        for row_idx, row_value in enumerate(line):
            if row_idx == y:
                continue
            if check_is_num_exist_for_tuple(sudoku, num_value, (x,row_idx)):
                count_validity += 1

        if count_validity == 0:
            unique_list.append(tmp_couple)

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

    return unique_list

def process_unique_per_row(sudoku,couple_list,num_value):
    # Create unique list
    unique_list = list()
    for tmp_couple in couple_list:
        x,y = tmp_couple
        row = get_row(sudoku,y)

        count_validity = 0
        for line_idx, line_value in enumerate(row):
            if line_idx == x:
                continue
            if check_is_num_exist_for_tuple(sudoku, num_value, (line_idx,y)):
                count_validity += 1

        if count_validity == 0:
            unique_list.append(tmp_couple)

    # Update couple list
    for unique_couple in unique_list:
        couple_list.remove(unique_couple)

    return unique_list

def process_unique_per_line_and_row(sudoku,couple_list,num_value):
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

def process_unique_per_block(sudoku,couple_list):
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

def process_unique_per_couples(sudoku,possibility_dict):
    # Create unique list
    unique_list = list()
    for tmp_couple in possibility_dict.keys():
        if len(possibility_dict[tmp_couple]) == 1:
            unique_list.append(tmp_couple)
            set_value(sudoku, possibility_dict[tmp_couple][0], tmp_couple)

    # Update ret_dict
    for tmp_couple in unique_list:
        possibility_dict.pop(tmp_couple)

    if len(unique_list) > 0:
        print('process_unique_num')
        return True
    else:
        return False

################################################################
#
# ########  ##     ## ########  ##       ####  ######     ###    ######## ########  ######  
# ##     ## ##     ## ##     ## ##        ##  ##    ##   ## ##      ##    ##       ##    ## 
# ##     ## ##     ## ##     ## ##        ##  ##        ##   ##     ##    ##       ##       
# ##     ## ##     ## ########  ##        ##  ##       ##     ##    ##    ######    ######  
# ##     ## ##     ## ##        ##        ##  ##       #########    ##    ##             ## 
# ##     ## ##     ## ##        ##        ##  ##    ## ##     ##    ##    ##       ##    ## 
# ########   #######  ##        ######## ####  ######  ##     ##    ##    ########  ######  
#
################################################################
def process_duplicates(sudoku_list,possibility_dict):
    return process_duplicates_per_block(sudoku_list,possibility_dict)

def process_duplicates_per_block(sudoku_list,possibility_dict):
    ret_value = False

    # Scan per block
    for block_num in range(9):
        # Filter possibility per block
        couple_list = list(filter(lambda x: block_num == int(x[0]/3)*3+int(x[1]/3), possibility_dict.keys()))

        # List all num
        num_list = flatten_list(list(map(lambda x: possibility_dict[x], couple_list)))

        # Search each num declared twice
        twice_num = list()
        for num_value in list(set(num_list)):
            if num_list.count(num_value) == 2:
                twice_num.append(num_value)

        # Is two num find twice ?
        if len(twice_num) < 2:
            continue

        # List all num couples duplicates possibility
        num_couples = list()
        for i, num_value in enumerate(twice_num):
            num_couples += list(product([num_value],twice_num[i+1:]))

        # List duplicates couples possiblity
        duplicate_couples = dict()
        for num_couple in num_couples:
            duplicate_couples[num_couple] = list()
            for tmp_couple in couple_list:
                if num_couple[0] in possibility_dict[tmp_couple] and num_couple[1] in possibility_dict[tmp_couple]:
                    duplicate_couples[num_couple].append(tmp_couple)

        # Update duplicate list
        remove_num = list()
        remove_couples = list()
        for tmp_couple in duplicate_couples.keys():
            if len(duplicate_couples[tmp_couple]) > 1:
                remove_num = tmp_couple
                remove_couples = duplicate_couples[tmp_couple]
                break # Limit possibilities ?

        # Update couple_list in block
        couple_list = list(filter(lambda x: not x in remove_couples, couple_list))

        num_list = flatten_list(list(map(lambda x: possibility_dict[x], couple_list)))
        unique_num = list()
        for num_value in list(set(num_list)):
            if num_list.count(num_value) == 1:
                unique_num.append(num_value)

        # Apply unique possibility
        for tmp_couple in couple_list:
            for unique_value in unique_num:
                if unique_value in possibility_dict[tmp_couple]:
                    ret_value = True
                    if get_value(sudoku_list,tmp_couple) == 0:
                        print("set_value "+str(tmp_couple)+" = "+str(unique_value))
                        set_value(sudoku_list, unique_value, tmp_couple)

    if ret_value:
        print('process_duplicates_per_block')
    return ret_value

################################################################
#
# ##     ##    ###    #### ##    ##
# ###   ###   ## ##    ##  ###   ##
# #### ####  ##   ##   ##  ####  ##
# ## ### ## ##     ##  ##  ## ## ##
# ##     ## #########  ##  ##  ####
# ##     ## ##     ##  ##  ##   ###
# ##     ## ##     ## #### ##    ##
#
################################################################
def get_args():
    parser = argparse.ArgumentParser(
        description="Sudoku solver"
    )
    parser.add_argument('file')
    parser.add_argument('-i', '--iteration',type=int,default=50)
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
        rescan      = False
        # For each num get couples possibility
        for num_value in range(1,10):
            remain_couples = scan_num(sudoku_list,num_value)
            tmp_ret, remain_couples = process_unique_per_num(sudoku_list,num_value,remain_couples)
            num_dict[num_value] = remain_couples
            if tmp_ret: rescan = True
        if rescan: continue

        # For each couple get nums possibility
        possibility_dict = get_num_per_couples(num_dict)

        # Process unique per couples
        rescan = process_unique_per_couples(sudoku_list,possibility_dict)
        if rescan: continue

        # Process duplicates
        rescan = process_duplicates_per_block(sudoku_list,possibility_dict)
        if rescan: continue

        # No more idea
        break

    print_sudoku(sudoku_list)
    print_remain_values(sudoku_list)
    print('--------------------------------')
    print("")
