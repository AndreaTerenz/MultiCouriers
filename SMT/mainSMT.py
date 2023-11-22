from multiprocessing import freeze_support
from pysmt.shortcuts import *
from pysmt.logics import QF_UFLIRA
import logging

def values_for_vars(solver, vars):
    return {var: solver.get_value(var) for var in vars}

# Portfolio solving makes it possible to run multiple solvers in
# parallel.  As soon as the first solver completes, all other solvers
# are stopped.  Current support for portfolio is mostly focused on
# one-shot calls, with only functional incrementality: the interface
# looks incremental, but internally there is no guarantee of re-using
# the solver state.
#
def main():
    # We enable logging to see what is going on behind the scenes:
    _info = logging.getLogger(__name__).info
    logging.basicConfig(level=logging.INFO)

    solvers_set = ["z3"]#, "msat"]

    # The first example shows how to use multiple solvers in the with the
    # is_sat shortcut

    # A solver set is an iterable of solver names or pairs of
    # solvers+options (See next example)

    tie = Symbol("tie")
    shirt = Symbol("shirt")
    f1 = Or(tie, shirt)
    f2 = Or(Not(tie), shirt)
    f3 = Or(Not(tie), Not(shirt))
    f = And(f1, f2, f3)

    res = is_sat(f, portfolio=solvers_set)
    _info("Example 1: is_sat")
    _info(f)
    _info(f"Satifiable: {res}")
    _info(f"Model:\n{get_model(f)}")
    _info(f"Value for '{tie}': {get_model(f).get_value(tie)}")

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
        s.add_assertion(f)

        res = s.solve()
        _info(f"Satifiable: {res}")
        # _info(f"Model:\n{s.get_model()}") # This is not working like get_model() for some reason
        for var in [tie, shirt]:
            _info(f"Value for '{var}': {s.get_value(var)}")

if __name__ == '__main__':
    freeze_support()
    main()