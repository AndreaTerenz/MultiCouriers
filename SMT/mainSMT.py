"""from pysmt.shortcuts import *

tie = Symbol("tie")
shirt = Symbol("shirt")
f1 = Or(tie, shirt)
f2 = Or(Not(tie), shirt)
f3 = Or(Not(tie), Not(shirt))
f = And(f1, f2, f3)

print(f)
print(f"Satifiable: {is_sat(f)}")
print(f"Model:\n{get_model(f)}")
print(get_model(f).get_value(tie))"""
from multiprocessing import freeze_support
from pysmt.shortcuts import Symbol, Implies, TRUE, FALSE, Not, is_sat, Portfolio
from pysmt.logics import QF_UFLIRA
import logging

# Portfolio solving makes it possible to run multiple solvers in
# parallel.  As soon as the first solver completes, all other solvers
# are stopped.  Current support for portfolio is mostly focused on
# one-shot calls, with only functional incrementality: the interface
# looks incremental, but internally there is no guarantee of re-using
# the solver state.
#
def main():
    x, y = Symbol("x"), Symbol("y")
    f = Implies(x, y)

    # The first example shows how to use multiple solvers in the with the
    # is_sat shortcut

    # We enable logging to see what is going on behind the scenes:
    _info = logging.getLogger(__name__).info
    logging.basicConfig(level=logging.INFO)

    # A solver set is an iterable of solver names or pairs of
    # solvers+options (See next example)

    _info("Example 1: is_sat")
    solvers_set = ["z3"]
    res = is_sat(f, portfolio=solvers_set)
    _info(f"Example 1 res: {res}")
    assert res is True

    # Behind the scenes, pySMT launched 3 processes and solved the
    # expression in parallel.
    #
    # The is_sat shortcut is useful for prototyping and exploration, but
    # we typically need more control over the solver. The Portfolio class
    # behaves as a solver and as such implements most of the methods of a
    # regular solver.

    # The options given to the Portfolio will be passed to all solvers, in
    # particular, we are enabling incrementality and model generation.

    _info("Example 2: Portfolio()")
    with Portfolio(solvers_set,
                   logic=QF_UFLIRA,
                   incremental=True,
                   generate_models=True) as s:
        print(s.__dict__)
        s.add_assertion(f)
        s.push()
        s.add_assertion(x)
        res = s.solve()
        _info(f"Example 2 res1: {res}")
        v_y = s.get_value(y)
        assert v_y is TRUE()

        s.pop()
        s.add_assertion(Not(y))
        res = s.solve()
        _info(f"Example 2 res2: {res}")
        v_x = s.get_value(x)
        assert v_x is FALSE()


    # Portfolio can also be useful to tweak heuristics of the solvers.
    # For supported solver options, please refer to the solver
    # documentation. This is an area of pySMT that could use additional
    # feedback and help!
    """
    NOT WORKING CAUSE WHO KNOWS WHAT OPTIONS z3 HAS
    
    _info("Example 3: Portfolio w options")
    with Portfolio(solvers_set=["z3"],
                   logic=QF_UFLIRA,
                   incremental=False,
                   generate_models=False) as s:
        res = s.is_sat(f)
        _info(msg=f"Example 3 res: {res}")
        assert res is True"""

if __name__ == '__main__':
    freeze_support()
    main()