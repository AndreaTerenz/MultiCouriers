from sys import argv

from SAT_SMT.constraints import *
from utils import *
from utils.z3utils import *


def main(instance_path):
    m, n, loads, sizes, dist_table, inst = load_MCP(instance_path)

    # Every courier must deliver at least one item
    # so we know each will deliver at most N-M+1 items
    max_items_per_courier = n - m + 1
    rk = range(max_items_per_courier)
    ri = range(m)

    ORIGIN = -1

    load_sizes = to_z3array(loads, "load_sizes", IntSort())
    item_sizes = to_z3array(sizes, "item_sizes", IntSort())

    X = [[Int(f"x_{i}_{k}") for k in rk] for i in ri]

    domain_constr = [And(ORIGIN <= X[i][k], X[i][k] < n) for i in ri for k in rk]
    consec_constr = [Implies(X[i][k] == ORIGIN, X[i][k+1] == ORIGIN) for k in range(1,n-m) for i in ri]
    ml_constr = [Sum([If(c == ORIGIN, 0, item_sizes[c]) for c in X[i]]) <= load_sizes[i] for i in ri]
    deliver_once_constr = [exactly_one([X[i][k] == j for k in rk for i in ri]) for j in range(n)]
    at_least_one_constr = [X[i][0] != ORIGIN for i in ri]

    s = Optimize()
    s.add(
        *domain_constr,
        *ml_constr,
        *deliver_once_constr,
        *at_least_one_constr,
        *consec_constr,
    )

    #################

    d = Function("dist", IntSort(), IntSort(), IntSort())

    s.add(d(-1, -1) == 0) # Can't hurt...
    s.add(*[d(-1, j) == dist_table[-1][j] for j in range(n)])
    s.add(*[d(j, -1) == dist_table[j][-1] for j in range(n)])
    s.add(*[d(j1, j2) == dist_table[j1][j2] for j1 in range(n) for j2 in range(n)])

    total_dist = [Int(f"td_{i}") for i in ri]
    s.add([total_dist[i] == d(-1, X[i][0]) + Sum([d(X[i][k], X[i][k+1]) for k in range(n-m)]) + d(X[i][-1], -1) for i in ri])

    #################

    # VERY weird that this isn't the actual obj function.....
    """for i in ri:
        s.minimize(total_dist[i])"""
    z = s.minimize(max_z3(total_dist))

    res = run_solver(s, lambda _s : _s.check())

    model = s.model()

    X_values = [[model.eval(X[i][k]).as_long() for k in range(n - m + 1)] for i in range(m)]

    res = ModelResult.Satisfied if res == sat else ModelResult.Unsatisfied

    check_solver(res, X_values, inst, optim_value=z.value().as_long())

if __name__ == '__main__':
    main(argv[1])