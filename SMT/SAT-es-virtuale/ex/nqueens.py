from SMT.constraints import *

def display_nqueens(sol):
    board = [[0] * len(sol) for i in range(len(sol))]
    for x, y in sol:
        board[x][y] = 1
    for i in range(len(board)):
        for j in range(len(board[0])):
            symbol = '♛' if board[i][j] == 1 else '.'
            print(symbol, end=' ')
        print()

def sat_nqueens(n):
    s = Solver()

    board = [[Bool(f"p_{i}_{j}") for j in range(n)] for i in range(n)]

    # Exactly one queen on each row and column
    for i in range(n):
        s.add(exactly_one([board[i][j] for j in range(n)]))
        s.add(exactly_one([board[j][i] for j in range(n)]))

    # At most one queen in each diagonal
    for i in range(n - 1):
        diag_ru_ll = []
        diag_lu_rl = []
        diag_ll_ru = []
        diag_rl_lu = []
        for j in range(n - i):
            diag_ll_ru += [board[i + j][j]]
            diag_lu_rl += [board[n - 1 - (i + j)][j]]
            diag_rl_lu += [board[i + j][n - 1 - j]]
            diag_ru_ll += [board[n - 1 - (i + j)][n - 1 - j]]
        s.add(at_most_one(diag_ru_ll))
        s.add(at_most_one(diag_lu_rl))
        s.add(at_most_one(diag_rl_lu))
        s.add(at_most_one(diag_ll_ru))

    s.check()

    m = s.model()
    return [(i, j) for i in range(n) for j in range(n) if m.evaluate(board[i][j])]

display_nqueens(sat_nqueens(20))