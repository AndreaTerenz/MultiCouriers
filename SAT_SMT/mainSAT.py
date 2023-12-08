from constraints import *
from timeit import default_timer as timer
from sys import argv
from mcputils import *

def ohe_encode(value:int, bits):
    #assert bits >= value, f"Unable to OH encode {value} with {bits} bits"
    bits = max(bits, value)

    t_enc = [False] * bits

    if value != 0:
        t_enc[value-1] = True

    return t_enc

def ohe_decode(bits):
    try:
        return bits.index(True)+1
    except ValueError:
        return 0

def ohe_to_intsort(bits_z3):
    return Sum([If(bits_z3[i], i+1, 0) for i in range(len(bits_z3))])

def ohe_eq(enc, target):
    """t_enc = ohe_encode(target, len(enc))

    return And([e == t for e,t in zip(enc, t_enc)])"""
    return ohe_to_intsort(enc) == target

def ohe_noteq(enc, target):
    """
    t_enc = ohe_encode(target, len(enc))

    return And(at_least_one([e != t for e,t in zip(enc, t_enc)]))
    """
    return ohe_to_intsort(enc) != target

def ohe_select(array, ohe_idx):
    return Select(array, ohe_to_intsort(ohe_idx))

def main():
    m, n, loads, sizes, distances, inst = load_MCP(argv[1])

    #loads = sorted(loads)

    # Every courier must deliver at least one item
    # so we know each will deliver at most N-M+1 items
    max_items_per_courier = n - m + 1
    rk = range(max_items_per_courier)
    ri = range(m)

    ORIGIN = n
    rj = range(ORIGIN)

    load_sizes = to_z3array(loads, "load_sizes", IntSort())
    item_sizes = to_z3array(sizes, "item_sizes", IntSort())

    # X_ikj is True when the J-th item is the K-th to be delivered by the I-th courier
    # j==n+1 is the origin
    X = [[Bools(names=[f"x_{i}_{k}_{j}" for j in rj]) for k in rk] for i in ri]

    # Basically, each X_ik is a one-hot encoding of an item, so we constrain it to be one-hot
    ohe_constr = [And([And(at_most_one(X[i][k])) for k in rk]) for i in ri]

    consec_constr = [Implies(ohe_eq(X[i][k], ORIGIN), ohe_eq(X[i][k + 1], ORIGIN)) for k in range(n - m) for i in ri]

    sums = [Sum([If(ohe_eq(X[i][k], ORIGIN), 0, ohe_select(item_sizes, X[i][k])) for k in rk]) for i in ri]
    ml_constr = [sums[i] <= load_sizes[i] for i in ri]

    deliver_once_constr = [And(exactly_one([ohe_eq(X[i][k], j) for k in rk for i in ri])) for j in range(n)]
    at_least_one_constr = [And(at_least_one([ohe_noteq(X[i][k], ORIGIN) for k in rk])) for i in ri]

    s = Optimize()
    s.add(
        *ohe_constr,
        *ml_constr,
        *deliver_once_constr,
        *at_least_one_constr,
        *consec_constr,
    )

    #################

    d = Function("dist", IntSort(), IntSort(), IntSort())

    s.add(d(ORIGIN, ORIGIN) == 0) # Can't hurt...
    s.add(*[d(ORIGIN, j) == distances[-1][j] for j in range(n)])
    s.add(*[d(j, ORIGIN) == distances[j][-1] for j in range(n)])
    s.add(*[d(j1, j2) == distances[j1][j2] for j1 in range(n) for j2 in range(n)])

    total_dist = [Int(f"td_{i}") for i in ri]
    s.add([total_dist[i] ==
           d(ORIGIN, ohe_to_intsort(X[i][0])) +
           Sum([d(ohe_to_intsort(X[i][k]), ohe_to_intsort(X[i][k+1])) for k in range(n-m)]) +
           d(ohe_to_intsort(X[i][-1]), ORIGIN) for i in ri])

    #################

    # VERY weird that this isn't the actual obj function.....
    """for i in ri:
        s.minimize(total_dist[i])"""
    z = s.minimize(max_z3(total_dist))

    res = run_solver(s, lambda _s : _s.check())

    model = s.model()

    tmp = [[[model.eval(X[i][k][j]) for j in rj] for k in rk] for i in ri]

    X_values = []

    for c in tmp:
        X_values.append([])
        for s in c:
            v = ohe_decode(s)
            if v == n:
                v = -1
            X_values[-1].append(v)

    res = ModelResult.Satisfied if res == sat else ModelResult.Unsatisfied

    check_solver(res, X_values, inst, optim_value=z.value())

if __name__ == '__main__':
    main()