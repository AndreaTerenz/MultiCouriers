from z3 import *

# B is the set of all boolean values (i.e., T and F)
B = BoolSort()
# Z is the set of all integers
Z = IntSort()

# Define a function f that maps from B to Z
f = Function("f", B, Z)
# Define a function g that maps from Z to B
g = Function("g", Z, B)

# Declare a single boolean variable a
a = Bool("a")

# Find a value of a that makes g(1+f(a)) == true
solve(g(1+f(a)))