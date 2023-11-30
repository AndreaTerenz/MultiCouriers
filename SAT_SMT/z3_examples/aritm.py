from z3 import *

x, y = Ints("x y")
A1, A2 = Bools("A1 A2")

s = Solver()
# The following formulae will be concatenated with ANDs
s.add(Or(Not(A1), 2*x + y >= -1))   # !A1 || 2x+y >= -1
s.add(Or(A1, x + y >= 3))           # A1 || x+y >= 3
s.add(Or(Not(A2), 4*x - y >= -4))   # !A2 || 4x-y >= -4
s.add(Or(A2, 2*x - y >= -6))        # A2 || 2x-y >= -6

print(s.check())
# The result of the model DOES NOT OPTIMIZE the values of x,y
# The model simply finds a combination of x,y,A1,A2 that satisfies the given expression
print(s.model())