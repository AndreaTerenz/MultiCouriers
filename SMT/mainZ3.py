from constraints import *
from timeit import default_timer as timer
from sys import argv

try:
    from mcputils import load_MCP
except:
    from ..mcputils import load_MCP

def to_z3array(values, name, val_sort, idx_sort=IntSort()):
    output = Array(name, idx_sort, val_sort)
    for idx, ls in enumerate(values):
        output = Store(output, idx, ls)

    return output

def min_z3(values):
    m = values[0]
    for val in values[1:]:
        m = If(val < m, val, m)
    return m

def max_z3(values):
    m = values[0]
    for val in values[1:]:
        m = If(val > m, val, m)
    return m

def check_solver(s, vars, instance, optim_res, expected_sat = True):
    print("*" * 50)

    n = instance["n_items"]
    m = instance["n_couriers"]
    load_sizes = instance["load_sizes"]
    item_sizes = instance["item_sizes"]
    dists = instance["distances"]

    start = timer()
    res = s.check()
    end = timer()

    exp = sat if expected_sat else unsat

    assert res == exp, f"Incorrect result (expected {exp})"

    if res == unsat:
        print("UNSATISFIABLE")
        return

    print("SATISFIABLE")
    print(f"Done in {end - start:.3f} seconds")

    model = s.model()

    delivered = []

    print(f"Optimized Z: {optim_res.value()}")

    for i in range(m):
        print(f"Courier {i}: ", end="")

        tot = 0
        last_stop = -1
        travelled = 0

        for k in range(n-m+1):
            v = model.evaluate(vars[i][k]).as_long()
            if v != -1:
                delivered.append(v)
                tot += item_sizes[v]
                print(f"{v:2}", end=" ")
            else:
                print("--", end=" ")

            travelled += dists[last_stop][v]
            last_stop = v

        travelled += dists[last_stop][-1]

        print(f"\t carried: {tot:2} - travelled: {travelled}")
        assert tot <= load_sizes[i], f"Load constraint violated for courier {i}"
    print("Load limits satisfied")

    deliv_len = len(delivered)
    deliv_set_len = len(set(delivered))

    assert deliv_len == deliv_set_len, "Items delivered more than once"
    assert deliv_set_len == n, "Not all items were delivered"

    print("All items delivered exactly once")

def main():
    inst_path = argv[1]
    inst = load_MCP(inst_path)

    m = inst["n_couriers"]
    n = inst["n_items"]

    print(f"Couriers: {m}")
    print(f"Items: {n}")
    print(f"Load limits: {inst['load_sizes']}")
    print(f"Item sizes: {inst['item_sizes']}")
    print("Distances:")
    print(*inst["distances"], sep="\n")

    # Every courier must deliver at least one item
    # so we know each will deliver at most N-M+1 items
    max_items_per_courier = n - m + 1
    rk = range(max_items_per_courier)
    ri = range(m)

    ORIGIN = -1

    load_sizes = to_z3array(inst["load_sizes"], "load_sizes", IntSort())
    item_sizes = to_z3array(inst["item_sizes"], "item_sizes", IntSort())

    X = [[Int(f"x_{i}_{k}") for k in rk] for i in ri]

    domain_constr = [And(ORIGIN <= X[i][k], X[i][k] < n) for i in ri for k in rk]
    consec_constr = [Implies(X[i][k] == ORIGIN, X[i][k+1] == ORIGIN) for k in range(n-m) for i in ri]
    ml_constr = [Sum([If(c == ORIGIN, 0, item_sizes[c]) for c in X[i]]) <= load_sizes[i] for i in ri]
    deliver_once_constr = [And(exactly_one([X[i][k] == j for k in rk for i in ri])) for j in range(n)]
    at_least_one_constr = [And(at_least_one([X[i][k] != ORIGIN for k in rk])) for i in ri]

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
    s.add(*[d(-1, j) == inst["distances"][-1][j] for j in range(n)])
    s.add(*[d(j, -1) == inst["distances"][j][-1] for j in range(n)])
    s.add(*[d(j1, j2) == inst["distances"][j1][j2] for j1 in range(n) for j2 in range(n)])

    total_dist = [Int(f"td_{i}") for i in ri]
    s.add([total_dist[i] == d(-1, X[i][0]) + Sum([d(X[i][k], X[i][k+1]) for k in range(n-m)]) + d(X[i][-1], -1) for i in ri])

    #################

    # VERY weird that this isn't the actual obj function.....
    """for i in ri:
        s.minimize(total_dist[i])"""
    z = s.minimize(max_z3(total_dist))

    check_solver(s, X, inst, z)

if __name__ == '__main__':
    main()