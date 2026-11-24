"""
Sudoku Assignment (Simplified Version - FIXED)
1. Check if a puzzle is a standard Sudoku
2. Solve it with backtracking and constraint propagation
"""

import time

# The puzzle we have to solve (0 = empty cell)
PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


# Helper: check if putting number 'num' in grid[row][col] is legal
def is_ok(grid, row, col, num):
    # check the row
    for c in range(9):
        if grid[row][c] == num:
            return False
    # check the column
    for r in range(9):
        if grid[r][col] == num:
            return False
    # check the 3x3 box
    box_row = row - row % 3
    box_col = col - col % 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == num:
                return False
    return True


# Helper: find an empty cell, returns (row, col) or None if board is full
def find_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None


# Check if the final grid is a valid solved sudoku
def is_valid_solution(grid):
    if find_empty(grid) is not None:
        return False
    for r in range(9):
        for c in range(9):
            num = grid[r][c]
            # temporarily remove the number, then check if it's legal
            grid[r][c] = 0
            ok = is_ok(grid, r, c, num)
            grid[r][c] = num
            if not ok:
                return False
    return True


# ---------------- Task 1: check if it's a standard sudoku ----------------
def count_solutions(grid, stop_at=2):
    """Count solutions. We stop early once we reach 'stop_at' solutions."""
    empty = find_empty(grid)
    if empty is None:
        return 1  # board is full, we found one solution

    row, col = empty
    total = 0
    for num in range(1, 10):
        if is_ok(grid, row, col, num):
            grid[row][col] = num          # try the number
            total += count_solutions(grid, stop_at)
            grid[row][col] = 0            # undo (backtrack)
            if total >= stop_at:          # no need to count further
                return total
    return total


def check_standard_sudoku(grid):
    """Returns (True/False, reason)."""
    # 1. check the shape
    if len(grid) != 9:
        return False, "grid is not 9 x 9"
    for row in grid:
        if len(row) != 9:
            return False, "grid is not 9 x 9"

    # 2. check the values
    for row in grid:
        for v in row:
            if not isinstance(v, int) or v < 0 or v > 9:
                return False, "invalid value " + str(v)

    # 3. check no number repeats in any row, column or box
    # FIX: temporarily remove the number first, otherwise is_ok
    # sees the number inside its own cell and always says "repeat"
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                num = grid[r][c]
                grid[r][c] = 0
                ok = is_ok(grid, r, c, num)
                grid[r][c] = num
                if not ok:
                    return False, "a digit repeats in a row, column or box"

    # 4. check there is exactly one solution
    copy = [row[:] for row in grid]   # work on a copy so we don't change the original
    n = count_solutions(copy)
    if n == 0:
        return False, "no solution"
    if n > 1:
        return False, "more than one solution"

    return True, "9 x 9, no conflicts, exactly one solution"


# ---------------- Task 2a: solve with backtracking ----------------
def solve_backtracking(grid):
    """Returns (solution_grid or None, calls, backtracks)."""
    calls = 0
    backtracks = 0

    def solve():
        nonlocal calls, backtracks
        calls += 1
        empty = find_empty(grid)
        if empty is None:
            return True   # no empty cells -> solved
        row, col = empty
        for num in range(1, 10):
            if is_ok(grid, row, col, num):
                grid[row][col] = num
                if solve():
                    return True
                grid[row][col] = 0    # undo
                backtracks += 1
        return False

    # FIX: always return a 3-value tuple so the caller can unpack it
    if solve():
        return grid, calls, backtracks
    return None, calls, backtracks


# ---------------- Task 2b: solve with constraint propagation ----------------
def solve_constraint_propagation(grid):
    """
    Simple version: fill in every cell that has only ONE possible number,
    and repeat until nothing changes. If the puzzle isn't solved after that,
    we fall back to guessing with backtracking.
    """
    guesses = 0

    changed = True
    while changed:
        changed = False
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    possible = []
                    for num in range(1, 10):
                        if is_ok(grid, r, c, num):
                            possible.append(num)
                    if len(possible) == 0:
                        return None, guesses   # contradiction, no solution
                    if len(possible) == 1:
                        grid[r][c] = possible[0]   # only one choice -> fill it in
                        changed = True

    # if there are still empty cells, we have to guess
    empty = find_empty(grid)
    if empty is not None:
        row, col = empty
        for num in range(1, 10):
            if is_ok(grid, row, col, num):
                guesses += 1
                copy = [r2[:] for r2 in grid]
                copy[row][col] = num
                result, extra = solve_constraint_propagation(copy)
                guesses += extra
                if result is not None:
                    return result, guesses
        return None, guesses

    return grid, guesses


# ---------------- Main ----------------
if __name__ == "__main__":
    print("Task 1:", check_standard_sudoku(PUZZLE))

    # backtracking
    grid1 = [row[:] for row in PUZZLE]
    t = time.perf_counter()
    solved1, calls, backtracks = solve_backtracking(grid1)
    t_bt = (time.perf_counter() - t) * 1000
    print("\nBacktracking solution:")
    for row in solved1:
        print(row)
    print("calls =", calls, ", backtracks =", backtracks, ", time =", round(t_bt, 2), "ms")

    # constraint propagation
    grid2 = [row[:] for row in PUZZLE]
    t = time.perf_counter()
    solved2, guesses = solve_constraint_propagation(grid2)
    t_cp = (time.perf_counter() - t) * 1000
    print("\nConstraint propagation solution:")
    for row in solved2:
        print(row)
    print("guesses =", guesses, ", time =", round(t_cp, 2), "ms")

    print("\nSame solution:", solved1 == solved2, "| Valid:", is_valid_solution(solved2))
