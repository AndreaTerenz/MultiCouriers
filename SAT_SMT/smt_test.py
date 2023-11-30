from io import StringIO
from multiprocessing import freeze_support
from pysmt.shortcuts import *
from pysmt.logics import QF_UFLIRA
import logging

from pysmt.smtlib.parser import SmtLibParser


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

def main_file_test():
    DEMO_SMTLIB = \
        """
        (set-logic QF_LIA)
        (declare-fun p () Int)
        (declare-fun q () Int)
        (declare-fun x () Bool)
        (declare-fun y () Bool)
        (define-fun .def_1 () Bool (! (and x y) :cost 1))
        (assert (=> x (> p q)))
        (check-sat)
        (push)
        (assert (=> y (> q p)))
        (check-sat)
        (assert .def_1)
        (check-sat)
        (pop)
        (check-sat)"""

    # We read the SAT_SMT-LIB Script by creating a Parser.
    # From here we can get the SAT_SMT-LIB script.
    parser = SmtLibParser()

    # The method SmtLibParser.get_script takes a buffer in input. We use StringIO to simulate an open file.
    # See SmtLibParser.get_script_fname() if to pass the path of a file.
    script = parser.get_script(StringIO(DEMO_SMTLIB))

    with Portfolio(solvers_set=["z3"],
                   logic=QF_UFLIRA,
                   incremental=True,
                   generate_models=True) as s:
        print(type(s))
        print(script.evaluate(solver=s))
    return

    # The SmtLibScript provides an iterable representation of the commands
    # that are present in the SAT_SMT-LIB file.
    #
    # Printing a summary of the issued commands
    for cmd in script:
        print(cmd.name)
    print("*" * 50)

    # SmtLibScript provides some utilities to perform common operations: e.g,
    #
    # - Checking if a command is present
    assert script.contains_command("check-sat")

    # - Counting the occurrences of a command
    assert script.count_command_occurrences("assert") == 3

    # - Obtain all commands of a particular type
    decls = script.filter_by_command_name("declare-fun")
    for d in decls:
        print(d)
    print("*" * 50)

    # Most SAT_SMT-LIB scripts define a single SAT call. In these cases, the
    # result can be obtained by conjoining multiple assertions. The
    # method to do that is SmtLibScript.get_strict_formula() that, raises
    # an exception if there are push/pop calls. To obtain the formula at
    # the end of the execution of the Script (accounting for push/pop) we
    # use get_last_formula
    #
    f = script.get_last_formula()
    print(f)

    # Finally, we serialize the script back into SAT_SMT-Lib format. This can
    # be dumped into a file (see SmtLibScript.to_file). The flag daggify,
    # specifies whether the printing is done as a DAG or as a tree.
    buf_out = StringIO()
    script.serialize(buf_out, daggify=True)
    print(buf_out.getvalue())
    print("*" * 50)

    # Expressions can be annotated in order to provide additional
    # information. The semantic of annotations is solver/problem
    # dependent. For example, VMT uses annotations to identify two
    # expressions as 1) the Transition Relation and 2) Initial Condition
    #
    # Here we pretend that we make up a ficticious Weighted SAT_SMT format
    # and label .def1 with cost 1
    #
    # The class pysmt.smtlib.annotations.Annotations deals with the
    # handling of annotations.
    #
    ann = script.annotations
    print(ann.all_annotated_formulae("cost"))
    print("*" * 50)

    # Annotations are part of the SAT_SMT-LIB standard, and are the
    # recommended way to perform inter-operable operations. However, in
    # many cases, we are interested in prototyping some algorithm/idea and
    # need to write the input files by hand. In those cases, using an
    # extended version of SAT_SMT-LIB usually provides a more readable input.
    # We provide now an example on how to define a symbolic transition
    # system as an extension of SAT_SMT-LIB.
    # (A more complete version of this example can be found in :
    # pysmt.tests.smtlib.test_parser_extensibility.py)
    #
    EXT_SMTLIB = """\
    (declare-fun A () Bool)
    (declare-fun B () Bool)
    (init (and A B))
    (trans (=> A (next A)))
    (exit)
    """



if __name__ == '__main__':
    freeze_support()
    main_file_test()