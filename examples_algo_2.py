#!/usr/bin/python3

import json
from sudoku_2 import *

def run_test(filepath):
    with open(filepath,'r') as file:
        print( run_and_verify(json.loads(file.read())) )

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
