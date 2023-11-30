from SAT_SMT.constraints import *

def sudoku(instance):
    r9 = range(9)

    board = [[Int(f"v_{i}_{j}") for j in r9] for i in r9]

    # Constrain cell value
    values_rule = [And(1 <= board[i][j], board[i][j] <= 9) for i in r9 for j in r9]

    # Distinc values in rows & cols
    row_rule = [Distinct(board[i]) for i in r9]
    col_rule = [Distinct(board[i][j]) for i in r9 for j in r9]

    # Each 3x3 square contains a digit at most once
    sq_rule = [Distinct([board[3*i0 + i][3*j0 + j] for i in range(3) for j in range(3)]) for i0 in range(3) for j0 in range(3)]

    sudoku_rules = values_rule + row_rule + col_rule + sq_rule

    # The If rule takes three arguments:
    #   CONDITION
    #   IF-COND-IS-TRUE
    #   IF-COND-IS-FALSE
    # If CONDITION is true, then IF-COND-IS-TRUE is also true
    # else, if CONDITION is false, then IF-COND-IS-FALSE is true
    # In this case, we mean that:
    # If inst[i,j] is 0, then True is true (basically a nop)
    # If inst[i,j] is NOT 0, then board[i,j] is equal to it
    instance_rule = [If(instance[i][j] == 0, True, board[i][j] == instance[i][j]) for i in r9 for j in r9]

    s = Solver()
    s.add(sudoku_rules + instance_rule)
    if s.check() == sat:
        m = s.model()
        r = [ [ m.evaluate(board[i][j]) for j in r9 ] for i in r9 ]
        print_matrix(r)
    else:
        print ("failed to solve")

instance1 = ((0, 0, 0, 0, 9, 4, 0, 3, 0),
             (0, 0, 0, 5, 1, 0, 0, 0, 7),
             (0, 8, 9, 0, 0, 0, 0, 4, 0),
             (0, 0, 0, 0, 0, 0, 2, 0, 8),
             (0, 6, 0, 2, 0, 1, 0, 5, 0),
             (1, 0, 2, 0, 0, 0, 0, 0, 0),
             (0, 7, 0, 0, 0, 0, 5, 2, 0),
             (9, 0, 0, 0, 6, 5, 0, 0, 0),
             (0, 4, 0, 9, 7, 0, 0, 0, 0))

instance2 = ((0, 0, 0, 0, 9, 0, 1, 0, 0),
             (2, 8, 0, 0, 0, 5, 0, 0, 0),
             (7, 0, 0, 0, 0, 6, 4, 0, 0),
             (8, 0, 5, 0, 0, 3, 0, 0, 6),
             (0, 0, 1, 0, 0, 4, 0, 0, 0),
             (0, 7, 0, 2, 0, 0, 0, 0, 0),
             (3, 0, 0, 0, 0, 1, 0, 8, 0),
             (0, 0, 0, 0, 0, 0, 0, 5, 0),
             (0, 9, 0, 0, 0, 0, 0, 7, 0))

sudoku(instance1)
print()
sudoku(instance2)