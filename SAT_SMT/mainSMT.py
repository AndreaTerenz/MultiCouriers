from itertools import combinations
from multiprocessing import freeze_support
from timeit import default_timer as timer

from pysmt.shortcuts import *

from mcputils import load_MCP, check_solver

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one(bool_vars):
    return at_most_one(bool_vars) + [at_least_one(bool_vars)]


def to_symbol_array(values, name):
    symbs = Symbol(name, ArrayType(INT, INT))
    for i, v in enumerate(values):
        symbs = Store(symbs, Int(i), Int(v))

    return symbs

def If(cond, iftrue, iffalse):
    t = Implies(cond, And(iftrue, Not(iffalse)))
    f = Implies(Not(cond), And(Not(iftrue), iffalse))

    return t #And(t,f)

def Symbols(names_str: str, dtype):
    return [Symbol(n, dtype) for n in names_str.split()]

def fix_symb_range(symb, minV, maxV, include_min = True, include_max = False):
    l = GE if include_min else GT
    u = LE if include_max else LT

    return And(l(symb, Int(minV)), u(symb, Int(maxV)))

def main():
    try:
        inst = load_MCP("instance.mcp")
    except:
        inst = load_MCP("../instance.mcp")

    m = inst["n_couriers"]
    n = inst["n_items"]
    load_sizes_inst = inst["load_sizes"]
    item_sizes_inst = inst["item_sizes"]

    print(f"Couriers: {m}")
    print(f"Items: {n}")
    print(f"Load limits: {load_sizes_inst}")
    print(f"Item sizes: {item_sizes_inst}")

    max_items_per_courier = n - m + 1
    rk = range(max_items_per_courier)
    ri = range(m)

    ORIGIN = -1

    load_sizes = to_symbol_array(load_sizes_inst, "load_sizes")
    item_sizes = to_symbol_array(item_sizes_inst, "item_sizes")

    # X_ik := which distrib point should courier I be at for their K-th stop?
    # In other words, which should be the K-th item delivered by courier I?
    # X_ik = 0 --> k-th stop is starting point
    X = [[Symbol(f"x_{i}_{k}", INT) for k in rk] for i in ri]

    domain_constr = [And(ORIGIN <= X[i][k], X[i][k] < n) for i in ri for k in rk]
    consec_constr = [Implies(X[i][k].Equals(ORIGIN), X[i][k + 1].Equals(ORIGIN)) for k in range(n - m) for i in ri]

    ml_constr = [GE(Select(load_sizes, Int(i)), Plus(*[Select(item_sizes, c) for c in X[i]])) for i in ri]

    # pisello_constr = Select(item_sizes, Int(-1)).NotEquals(Int(0)) #LE(Plus(*[Select(item_sizes, c) for c in X[0]]), Int(15))

    deliver_once_constr = [And(exactly_one([X[i][k].Equals(j) for k in rk for i in ri])) for j in range(n)]
    at_least_one_constr = [And(at_least_one([X[i][k].NotEquals(ORIGIN) for k in rk])) for i in ri]

    solver_name = "z3"
    s = Solver(name=solver_name, logic="QF_UFLRA")

    s.add_assertion(And(domain_constr))
    s.add_assertion(And(consec_constr))
    s.add_assertion(And(ml_constr))
    # s.add_assertion(pisello_constr)
    s.add_assertion(And(deliver_once_constr))
    s.add_assertion(And(at_least_one_constr))

    print("*" * 50)
    print(f"Solving with {solver_name}...", end="")

    start = timer()
    res = s.solve()
    end = timer()

    print(f"done in {end - start:.3f} seconds")

    check_solver(res, X, inst,
                 get_val_lambda=lambda x: s.get_value(x).constant_value(),
                 unsat_val=False)

if __name__ == '__main__':
    freeze_support()
    main()