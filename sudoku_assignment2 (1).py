"""
Advanced Algorithm - Assignment 2
1. Check whether a puzzle is a standard Sudoku.
2. Solve it with (a) backtracking and (b) constraint propagation.
Grids are plain 9x9 lists of lists (0 = empty cell).
"""
import time

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

N = 9
CELLS = [(r, c) for r in range(N) for c in range(N)]

# Units: 9 rows, 9 columns, 9 boxes (each a list of 9 (row, col) cells)
UNITS = [[(r, c) for c in range(N)] for r in range(N)]
UNITS += [[(r, c) for r in range(N)] for c in range(N)]
UNITS += [[(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3)]
          for br in range(0, N, 3) for bc in range(0, N, 3)]

# UNITS_OF[r][c] = the 3 units of a cell; PEERS[r][c] = its 20 peer cells
UNITS_OF = [[[u for u in UNITS if (r, c) in u] for c in range(N)] for r in range(N)]
PEERS = [[list({x for u in UNITS_OF[r][c] for x in u} - {(r, c)})
          for c in range(N)] for r in range(N)]


def candidates(grid, r, c):
    """Digits that can legally go in cell (r, c)."""
    used = set(grid[r]) | {grid[i][c] for i in range(N)}
    br, bc = r // 3 * 3, c // 3 * 3
    used |= {grid[i][j] for i in range(br, br + 3) for j in range(bc, bc + 3)}
    return [d for d in range(1, 10) if d not in used]


def is_valid_solution(grid):
    return all(sorted(grid[r][c] for r, c in u) == list(range(1, 10)) for u in UNITS)


# ---------------- Task 1: standard Sudoku check ----------------
def count_solutions(grid, limit=2):
    """Count solutions, stopping at `limit` (used for the uniqueness test)."""
    g = [row[:] for row in grid]
    count = 0

    def search():
        nonlocal count
        best = None
        for r, c in CELLS:                      # empty cell with fewest options
            if g[r][c] == 0:
                opts = candidates(g, r, c)
                if best is None or len(opts) < len(best[1]):
                    best = ((r, c), opts)
        if best is None:
            count += 1
            return
        (r, c), opts = best
        for d in opts:
            g[r][c] = d
            search()
            g[r][c] = 0
            if count >= limit:
                return

    search()
    return count


def check_standard_sudoku(grid):
    """Returns (True/False, reason). Checks shape, values, conflicts, uniqueness."""
    if len(grid) != N or any(len(row) != N for row in grid):
        return False, "grid is not 9 x 9"
    for row in grid:
        for v in row:
            if not isinstance(v, int) or not 0 <= v <= 9:
                return False, f"invalid value {v!r}"
    for u in UNITS:
        vals = [grid[r][c] for r, c in u if grid[r][c] != 0]
        if len(vals) != len(set(vals)):
            return False, "a digit repeats in a row, column or box"
    n = count_solutions(grid)
    if n == 0:
        return False, "no solution"
    if n > 1:
        return False, "more than one solution"
    return True, "9 x 9, no conflicts, exactly one solution"


# ---------------- Task 2(a): backtracking ----------------
def solve_backtracking(grid):
    """Returns (solution or None, number of recursive calls, number of backtracks)."""
    g = [row[:] for row in grid]
    calls = backtracks = 0

    def solve():
        nonlocal calls, backtracks
        calls += 1
        for r, c in CELLS:
            if g[r][c] == 0:
                for d in candidates(g, r, c):
                    g[r][c] = d
                    if solve():
                        return True
                    g[r][c] = 0
                    backtracks += 1
                return False
        return True

    ok = solve()
    return (g if ok else None), calls, backtracks


# ---------------- Task 2(b): constraint propagation ----------------
# cands[r][c] is the set of digits still possible in cell (r, c).
def assign(cands, r, c, d):
    """Fix (r, c) to d by eliminating its other digits. False = contradiction."""
    return all(eliminate(cands, r, c, x) for x in list(cands[r][c] - {d}))


def eliminate(cands, r, c, d):
    """Remove d from (r, c) and propagate. False = contradiction."""
    if d not in cands[r][c]:
        return True
    cands[r][c].discard(d)
    if not cands[r][c]:
        return False
    if len(cands[r][c]) == 1:                   # only one digit left: remove it from peers
        only = next(iter(cands[r][c]))
        if not all(eliminate(cands, pr, pc, only) for pr, pc in PEERS[r][c]):
            return False
    for unit in UNITS_OF[r][c]:                 # digit fits only one cell of a unit: place it
        places = [(ur, uc) for ur, uc in unit if d in cands[ur][uc]]
        if not places:
            return False
        if len(places) == 1 and not assign(cands, places[0][0], places[0][1], d):
            return False
    return True


def solve_constraint_propagation(grid):
    """Returns (solution or None, number of guesses)."""
    cands = [[set(range(1, 10)) for _ in range(N)] for _ in range(N)]
    for r, c in CELLS:
        if grid[r][c] and not assign(cands, r, c, grid[r][c]):
            return None, 0
    guesses = 0

    def search(state):
        nonlocal guesses
        undecided = [(r, c) for r, c in CELLS if len(state[r][c]) > 1]
        if not undecided:
            return state
        r, c = min(undecided, key=lambda x: len(state[x[0]][x[1]]))   # fewest candidates
        for d in sorted(state[r][c]):
            guesses += 1
            trial = [[set(s) for s in row] for row in state]
            if assign(trial, r, c, d):
                result = search(trial)
                if result:
                    return result
        return None

    final = search(cands)
    if final is None:
        return None, guesses
    return [[next(iter(final[r][c])) for c in range(N)] for r in range(N)], guesses


# ---------------- Main ----------------
if __name__ == "__main__":
    print("Task 1:", check_standard_sudoku(PUZZLE))

    t = time.perf_counter()
    sol_bt, calls, backtracks = solve_backtracking(PUZZLE)
    t_bt = (time.perf_counter() - t) * 1000
    print("\nBacktracking solution:")
    print(sol_bt)
    print(f"calls={calls}, backtracks={backtracks}, time={t_bt:.2f} ms")

    t = time.perf_counter()
    sol_cp, guesses = solve_constraint_propagation(PUZZLE)
    t_cp = (time.perf_counter() - t) * 1000
    print("\nConstraint propagation solution:")
    print(sol_cp)
    print(f"guesses={guesses}, time={t_cp:.2f} ms")

    print("\nSame solution:", sol_bt == sol_cp, "| Valid:", is_valid_solution(sol_cp))
