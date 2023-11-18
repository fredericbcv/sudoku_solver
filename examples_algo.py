#!/usr/bin/python3

from solver import *

def run_test(filepath):
    test = sudoku_solver(filepath)
    test.run()

    # print(filepath,end=" \t")
    if test.solved:
        print('{: <32} => Solved'.format(filepath))
    # else:
    if not test.solved:
        print('{: <32} => Not solved, error = {}'.format(filepath,test.error))

    test.print_matrix()
    # test.print_remain_values()

if __name__ == '__main__':
    # run_test("examples/empty.json")
    # run_test("examples/example_bug.json")
    # run_test("examples/example1.json")
    # run_test("examples/example100.json")
    # run_test("examples/example104.json")
    # run_test("examples/example_challenge.json")
    # run_test("examples/example_evil1.json")
    # run_test("examples/example_evil2.json")
    # run_test("examples/example_evil3.json")
    # run_test("examples/example_evil4.json")
    # run_test("examples/example_expert1.json")
    # run_test("examples/example_expert2.json")
    # run_test("examples/example_expert3.json")
    # run_test("examples/examplexx.json")
    # run_test("examples/examplezzz.json")
    run_test("examples/example_hardcore.json")
