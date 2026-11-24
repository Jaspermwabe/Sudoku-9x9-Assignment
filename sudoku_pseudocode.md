Sudoku Assignment — Pseudocode

Helper Functions (used everywhere)

FUNCTION is_ok(grid, row, col, num):
    FOR c = 0 to 8:
        IF grid[row][c] == num THEN RETURN False        // row check
    FOR r = 0 to 8:
        IF grid[r][col] == num THEN RETURN False        // column check
    box_row = row - (row mod 3)
    box_col = col - (col mod 3)
    FOR r = box_row to box_row + 2:
        FOR c = box_col to box_col + 2:
            IF grid[r][c] == num THEN RETURN False      // box check
    RETURN True

FUNCTION find_empty(grid):
    FOR r = 0 to 8:
        FOR c = 0 to 8:
            IF grid[r][c] == 0 THEN RETURN (r, c)       // found an empty cell
    RETURN None                                          // board is full


 Task 1 — Check if it is a Standard Sudoku

FUNCTION check_standard_sudoku(grid):
    // 1. check the shape
    IF length(grid) != 9 THEN RETURN (False, "not 9 x 9")
    FOR each row in grid:
        IF length(row) != 9 THEN RETURN (False, "not 9 x 9")

    // 2. check the values
    FOR each row in grid:
        FOR each v in row:
            IF v is not an integer OR v < 0 OR v > 9:
                RETURN (False, "invalid value")

    // 3. check no digit repeats (temporarily remove the digit first!)
    FOR r = 0 to 8:
        FOR c = 0 to 8:
            IF grid[r][c] != 0:
                num = grid[r][c]
                grid[r][c] = 0
                ok = is_ok(grid, r, c, num)
                grid[r][c] = num
                IF not ok THEN RETURN (False, "digit repeats")

    // 4. count solutions (stop early at 2)
    n = count_solutions(copy of grid, stop_at = 2)
    IF n == 0 THEN RETURN (False, "no solution")
    IF n > 1 THEN RETURN (False, "more than one solution")
    RETURN (True, "9 x 9, no conflicts, exactly one solution")


 Sub-function: count_solutions


FUNCTION count_solutions(grid, stop_at):
    empty = find_empty(grid)
    IF empty == None THEN RETURN 1        // board full = one solution found

    (row, col) = empty
    total = 0
    FOR num = 1 to 9:
        IF is_ok(grid, row, col, num):
            grid[row][col] = num                     // try it
            total = total + count_solutions(grid, stop_at)
            grid[row][col] = 0                       // undo
            IF total >= stop_at THEN RETURN total    // no need to count more
    RETURN total


 Task 2a — Solve with Backtracking

FUNCTION solve_backtracking(grid):
    calls = 0
    backtracks = 0

    FUNCTION solve():                     // the recursive part
        calls = calls + 1
        empty = find_empty(grid)
        IF empty == None THEN RETURN True         // solved!

        (row, col) = empty
        FOR num = 1 to 9:
            IF is_ok(grid, row, col, num):
                grid[row][col] = num              // place the number
                IF solve() == True:
                    RETURN True                   // it worked, keep it
                grid[row][col] = 0                // didn't work, undo it
                backtracks = backtracks + 1
        RETURN False                              // no number worked here

    IF solve() == True:
        RETURN (grid, calls, backtracks)
    ELSE:
        RETURN (None, calls, backtracks)


Main idea: try a number in the first empty cell, recurse to solve the rest,
if it fails, undo and try the next number.

Task 2b — Solve with Constraint Propagation

FUNCTION solve_constraint_propagation(grid):
    guesses = 0

    // PART 1: fill in every cell that has only ONE possible number
    changed = True
    WHILE changed == True:
        changed = False
        FOR r = 0 to 8:
            FOR c = 0 to 8:
                IF grid[r][c] == 0:
                    possible = empty list
                    FOR num = 1 to 9:
                        IF is_ok(grid, r, c, num):
                            add num to possible
                    IF possible is empty:
                        RETURN (None, guesses)      // contradiction
                    IF possible has exactly 1 number:
                        grid[r][c] = that number    // only choice!
                        changed = True              // keep looping

    // PART 2: if cells are still empty, we must guess
    empty = find_empty(grid)
    IF empty != None:
        (row, col) = empty
        FOR num = 1 to 9:
            IF is_ok(grid, row, col, num):
                guesses = guesses + 1
                copy = copy of grid
                copy[row][col] = num
                (result, extra) = solve_constraint_propagation(copy)
                guesses = guesses + extra
                IF result != None:
                    RETURN (result, guesses)
        RETURN (None, guesses)                       // every guess failed

    RETURN (grid, guesses)                           // nothing left to fill

is_valid_solution (checker at the end)

FUNCTION is_valid_solution(grid):
    IF find_empty(grid) != None THEN RETURN False    // not fully solved
    FOR r = 0 to 8:
        FOR c = 0 to 8:
            num = grid[r][c]
            grid[r][c] = 0
            ok = is_ok(grid, r, c, num)
            grid[r][c] = num
            IF not ok THEN RETURN False
    RETURN True
