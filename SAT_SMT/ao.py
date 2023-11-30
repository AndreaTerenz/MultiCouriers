# The last part of the example requires a QF_LIA solver to be installed.
#
#
# This example shows how to interact with files in the SAT_SMT-LIB
# format. In particular:
#
# 1. How to read a file in SAT_SMT-LIB format
# 2. How to write a file in SAT_SMT-LIB format
# 3. Formulas and SAT_SMT-LIB script
# 4. How to access annotations from SAT_SMT-LIB files
# 5. How to extend the parser with custom commands
#
from io import StringIO

from pysmt.shortcuts import Solver
from pysmt.smtlib.parser import SmtLibParser

# We read the SAT_SMT-LIB Script by creating a Parser.
# From here we can get the SAT_SMT-LIB script.
parser = SmtLibParser()

# The method SmtLibParser.get_script takes a buffer in input. We use
# StringIO to simulate an open file.
# See SmtLibParser.get_script_fname() if to pass the path of a file.
script = parser.get_script_fname("ao.smt2")
script.evaluate(script.commands[9])
f = script.get_last_formula()
print(f)

s = Solver(name="z3")

s.add_assertion(f)

print(s.solve())
