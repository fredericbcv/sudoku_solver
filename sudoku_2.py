import copy
import time
from abc import ABC, abstractmethod
from array import array
from typing import Tuple, List, Optional, Type


# An OptionSet is an int that has 9 bits set either to:
#  - 1 to mark a digit already used
#  - 0 to mark a digit available
class OptionSet:

    @staticmethod
    def iter_digits(bitset: int):
        b = ~bitset & 0b111111111  # For easier algorithm, flip the bits
        for d in range(1, 10):
            if b & (1 << (d - 1)):
                yield d


Coords = Tuple[int, int]


class UnresolvedCell:

    def __init__(self, idx: int, possible_digits: int):
        self.idx = idx
        self.possible_digits = possible_digits


# The sudoku class maintains several states to solve the sudoku without exploratory work
# Every time a value is inserted, the constraint is propagated to a cells one the same line, row and block
# When a cell has a single possibility, it's id is put on a list that can be used for further solving
#
# For the purpose of the algorithm, the state can be mutated. However, when exploring branches of solutions
# one is supposed to deepcopy the sudoku instead of remembering and resetting the values mutated during the exploration
class Sudoku:

    def __init__(self, is_copy=False):
        if not is_copy:
            self.grid = array('i', [0] * 81)
            self.options = array('i', [0] * 81)
            self.options_count = array('i', [9] * 81)
            self.one_option_list = []
        
    def copy(self):
        new = Sudoku(is_copy=True)
        new.grid = copy.deepcopy(self.grid)
        new.options = copy.deepcopy(self.options)
        new.options_count = copy.deepcopy(self.options_count)
        new.one_option_list = []
        
        return new

    def update_value(self, idx: int, digit: int):
        assert digit != 0
        self.grid[idx] = digit
        self.options[idx] = 0
        self.options_count[idx] = 0
        self.propagate_constraints(idx, digit)

    def propagate_constraints(self, idx: int, digit: int):
        self.propagate_line_constraints(idx, digit)
        self.propagate_row_constraints(idx, digit)
        self.propagate_block_constraints(idx, digit)

    def propagate_line_constraints(self, idx: int, digit: int):
        line_start_idx = int(idx / 9) * 9
        for idx in range(line_start_idx, line_start_idx + 9):
            self.remove_option(idx, digit)

    def propagate_row_constraints(self, idx: int, digit: int):
        row_start_idx = idx % 9
        for idx in range(row_start_idx, 81, 9):
            self.remove_option(idx, digit)

    def propagate_block_constraints(self, idx: int, digit: int):
        left_corner_idx = int(idx / 27) * 27 + int((idx % 9) / 3) * 3
        for block_line_idx in range(3):
            left_idx = left_corner_idx + (block_line_idx * 9)
            for i in range(left_idx, left_idx + 3):
                self.remove_option(i, digit)

    # Remove an option at a given cell. Check if we reach an abnormal situation.
    # If a given cell has a single possibility, keep track of it
    def remove_option(self, idx: int, digit: int):
        current_count = self.options_count[idx]
        if current_count > 0:  # do not touch already solved cells
            old_options = self.options[idx]
            new_options = old_options | (1 << (digit - 1))
            if old_options != new_options:  # Check that removing a possibility actually changed current options
                new_count = current_count - 1
                if new_count == 0:
                    raise RuntimeError('Impossible sudoku')
                if new_count == 1:
                    self.one_option_list.append(idx)  # Store this idx for further processing
                # Remember the new values
                self.options[idx] = new_options
                self.options_count[idx] = new_count

    # Find the cell that has the least possibilities for exploratory work
    def get_least_options_unresolved_cell(self) -> Optional[UnresolvedCell]:
        min_idx = -1
        min_count = 9
        for i in range(81):
            options = self.options[i]
            if options > 0:
                count = self.options_count[i]
                if count < min_count:
                    min_idx = i
                    min_count = count

        if min_idx == -1:
            return None
        else:
            return UnresolvedCell(min_idx, self.options[min_idx])

    def get_grid_idx(self, coords: Coords):
        return coords[0] * 9 + coords[1]

    def get_digit(self, coords: Coords):
        return self.grid[self.get_grid_idx(coords)]

    # Load a Sudoku from a List[List[Int]]
    def load(self, lines):
        assert len(lines) == 9
        for i in range(9):
            line = lines[i]
            assert len(line) == 9
            for j in range(9):
                digit = line[j]
                if digit != 0:
                    self.update_value(self.get_grid_idx((i, j)), digit)

    # Useful to print out a sudoku in terminal
    def __str__(self):
        s = ""
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        s += str(self.grid[self.get_grid_idx((i * 3 + j, k * 3 + l))])
                        s += " "
                    s += " "
                s += "\n"
            s += "\n"

        return s


class Solver:
    # A special value used to initiate the solution exploration
    EXPLORATION_BOOTSTRAP = None

    class ExplorationTraversal(ABC):

        def __init__(self):
            self.exploration_tuples = [Solver.EXPLORATION_BOOTSTRAP]

        def has_more(self) -> bool:
            return len(self.exploration_tuples) > 0

        def add(self, exploration_tuple: Tuple[int, int, Sudoku]):
            self.exploration_tuples.append(exploration_tuple)

        @abstractmethod
        def next(self) -> Tuple[int, int, Sudoku]:
            pass

    # Depth-First-Search traversal kind
    class DFS(ExplorationTraversal):
        def next(self) -> Tuple[int, int, Sudoku]:
            return self.exploration_tuples.pop()

    # Breadth-First-Search traversal kind
    class BFS(ExplorationTraversal):
        def next(self) -> Tuple[int, int, Sudoku]:
            return self.exploration_tuples.pop(0)

    # Resolves cells that can be resolved by pure constraint
    # returns the unresolved cell with the least number of possible options
    # None if the sudoku is solved
    #
    # Raises if the sudoku cannot be solved
    #
    # Warning: the sudoku is mutated by this method
    @staticmethod
    def resolve_constrained_cells(sudoku: Sudoku) -> Optional[UnresolvedCell]:

        while len(sudoku.one_option_list) > 0:
            single_option_idx = sudoku.one_option_list.pop()
            sudoku.update_value(single_option_idx, next(OptionSet.iter_digits(sudoku.options[single_option_idx])))

        return sudoku.get_least_options_unresolved_cell()

    # Solves a sudoku, possibly through exploration
    #
    # Returns the sudoku solution, or None if the sudoku has no solution 
    #
    # Note: the provided sudoku is mutated but the resulting mutation is not necessarily the solution
    @staticmethod
    def solve(sudoku: Sudoku, traversal_kind: Type[ExplorationTraversal] = DFS) -> Optional[Sudoku]:
        # We push Tuple[idx, digit_to_test, Sudoku] to the exploration_traversal
        # Keeping a deep copy of the sudoku is important since resolve_constrained_cells
        # mutates its state. It would be a lot harder to keep track of all values discovered through constraints
        # and reset all of them

        # Init the exploration
        exploration_traversal = traversal_kind()

        while exploration_traversal.has_more():
            exploration_tuple = exploration_traversal.next()
            if exploration_tuple != Solver.EXPLORATION_BOOTSTRAP:
                idx, digit, sudoku = exploration_tuple
                sudoku.update_value(idx, digit)

            try:
                least_options_remaining_cell = Solver.resolve_constrained_cells(sudoku)
            except RuntimeError:
                # Such sudoku has no solution, explore other branches
                continue
            if least_options_remaining_cell is None:
                # This sudoku is solved, return it
                return sudoku
            else:
                # Otherwise, we need to continue exploration
                for digit_to_test in OptionSet.iter_digits(least_options_remaining_cell.possible_digits):
                    exploration_traversal.add((least_options_remaining_cell.idx, digit_to_test, sudoku.copy()))

        # We are out of the loop, we explored everything and could not solve
        return None


def verify_solution_matches_problem(problem: List[List[int]], solution: Sudoku):
    for i in range(9):
        for j in range(9):
            problem_digit = problem[i][j]
            solution_digit = solution.get_digit((i, j))
            if problem_digit != 0 and solution_digit != problem_digit:
                raise RuntimeError(
                    f"The solution does not match the problem at cell {(i, j)}. "
                    f"Expected {problem_digit}, got {solution_digit}"
                )


def verify_sudoku_correctness(solution: Sudoku):
    import itertools
    lines = {}
    rows = {}
    blocks = {}
    for i in range(9):
        for j in range(9):
            digit = solution.get_digit((i, j))
            lines.setdefault(i, []).append(digit)
            rows.setdefault(j, []).append(digit)
            blocks.setdefault(int(i / 3) * 3 + int(j / 3), []).append(digit)
    for digit_list in itertools.chain(lines.values(), rows.values(), blocks.values()):
        if len(digit_list) != len(set(digit_list)):
            raise RuntimeError("The solution is invalid")


def run_and_verify_with_traversal(problem, traversal_kind):
    start_time = time.time()
    sudoku = Sudoku()
    sudoku.load(problem)
    solver = Solver()
    solved_sudoku = solver.solve(sudoku, traversal_kind=traversal_kind)
    end_time = time.time()
    verify_solution_matches_problem(problem, solved_sudoku)
    verify_sudoku_correctness(solved_sudoku)
    duration = end_time - start_time
    print(f"Tests duration using {traversal_kind}: {duration} seconds")


def run_and_verify(problem):
    run_and_verify_with_traversal(problem, Solver.DFS)
    run_and_verify_with_traversal(problem, Solver.BFS)


if __name__ == '__main__':
    print("Problem easy")
    run_and_verify([
        [9, 4, 1, 0, 3, 0, 7, 0, 0],
        [0, 0, 5, 0, 0, 8, 6, 0, 0],
        [7, 0, 0, 2, 0, 0, 4, 3, 5],
        [0, 1, 0, 0, 5, 0, 0, 4, 3],
        [2, 9, 0, 1, 0, 0, 0, 0, 0],
        [8, 5, 0, 7, 4, 0, 9, 0, 0],
        [1, 3, 8, 9, 0, 6, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 8, 2],
        [5, 0, 2, 0, 8, 0, 0, 0, 6],
    ])
    print("Problem medium")
    run_and_verify([
        [0, 5, 3, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 6, 9],
        [0, 0, 0, 7, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 9, 8],
        [4, 0, 0, 6, 0, 0, 0, 0, 7],
        [5, 0, 0, 4, 3, 0, 0, 0, 0],
        [0, 0, 2, 5, 0, 6, 0, 0, 0],
        [0, 0, 0, 0, 0, 8, 1, 0, 0],
        [0, 8, 9, 0, 0, 7, 0, 0, 4]
    ])
    print("Problem hard")
    run_and_verify([
        [0, 8, 0, 0, 0, 4, 0, 5, 0],
        [0, 6, 0, 2, 0, 0, 0, 0, 0],
        [5, 0, 2, 0, 7, 0, 1, 0, 0],
        [0, 0, 6, 0, 0, 0, 0, 0, 0],
        [2, 0, 1, 9, 0, 0, 0, 4, 0],
        [0, 0, 0, 0, 8, 0, 0, 0, 9],
        [0, 0, 0, 0, 0, 3, 7, 0, 0],
        [4, 0, 9, 8, 0, 0, 0, 1, 0],
        [0, 5, 0, 0, 0, 0, 0, 0, 0]
    ])
    print("Problem master class")
    run_and_verify([
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0]
    ])
