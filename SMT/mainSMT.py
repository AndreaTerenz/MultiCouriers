from itertools import combinations
from multiprocessing import freeze_support
from pysmt.shortcuts import *
from pysmt.logics import QF_UFLIRA
import logging

try:
    from loader import load_MCP
except:
    from ..loader import load_MCP

def to_symbol_array(values, name):
    symbs = Symbol(name, ArrayType(INT, INT))
    for i, v in enumerate(values):
        symbs = Store(symbs, Int(i), Int(v))

    return symbs

def If(cond, iftrue, iffalse):
    t = Implies(cond, iftrue)
    f = Implies(Not(cond), iffalse)

    return And(t,f)

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

    rn = range(n)
    rm = range(m)

    EMPTY = -1

    load_sizes = to_symbol_array(load_sizes_inst, "load_sizes")
    item_sizes = to_symbol_array(item_sizes_inst, "item_sizes")

    # X_ik := which distrib point should courier I be at for their K-th stop?
    # In other words, which should be the K-th item delivered by courier I?
    # X_ik = 0 --> k-th stop is starting point
    X = [[Symbol(f"x_{i}_{k}", INT) for k in rn] for i in rm]
    # X_ik should be between 0 and n
    domain_constr = And([fix_symb_range(X[i][k], EMPTY, n) for k in rn for i in rm])
    # X_i0 and X_i(n-1) should be 0
    #start_constr = And([X[i][0].Equals(0) for i in rm])
    #end_constr   = And([X[i][n-1].Equals(0) for i in rm])
    #se_constr    = And(start_constr, end_constr)

    start_constr = And([X[i][0].NotEquals(EMPTY) for i in rm])
    # Once the courier is back at the start (0) they cannot leave again
    # i.e., all non-zero values in each row of X must be consecutive
    consec_constr = [Implies(X[i][k].Equals(EMPTY), X[i][k+1].Equals(EMPTY)) for i in rm for k in range(n-1)]
    consec_constr = And(consec_constr)

    # max load constraints
    ml_constr = []
    for i in rm:
        carried_weight = Plus([item_sizes.Select(c) for c in X[i]])
        ml_constr.append(LE(carried_weight, load_sizes.Select(Int(i))))
    ml_constr = And(ml_constr)

    # Each item should be delivered only once
    deliver_once_constr = []
    for j in rn:
        vs = [X[i][k].Equals(j) for k in rn for i in rm]
        doc_at_least = [Or(vs)]
        doc_at_most = [Not(And(p0, p1)) for p0, p1 in combinations(vs, 2)]

        deliver_once_constr.append(And(doc_at_least + doc_at_most))

    deliver_once_constr = And(deliver_once_constr)

    s = Solver()
    s.add_assertion(domain_constr)
    # s.add_assertion(start_constr)
    # s.add_assertion(consec_constr)
    s.add_assertion(ml_constr)
    s.add_assertion(deliver_once_constr)

    res = s.solve()
    print(f"Satisfiable: {res}")

    if not res:
        return

    for i in rm:
        tot = 0
        for k in rn:
            v = s.get_value(X[i][k]).constant_value()
            if v != -1:
                tot += item_sizes_inst[v]
            print(f"{v:2}", end = " ")
        print(f"\t {tot}")
        #assert tot <= load_sizes_inst[i], f"Load constraint violated ({tot} > {load_sizes_inst[i]})"

if __name__ == '__main__':
    freeze_support()
    main()