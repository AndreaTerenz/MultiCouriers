from z3 import *

# Z3 enables OMT via the Optimize class

x, y = Reals("x y")
A1, A2 = Bools("A1 A2")

o = Optimize()
# The following formulae will be concatenated with ANDs
o.add(Or(Not(A1), 2 * x + y >= -2))
o.add(Or(A1, x + y >= 3))
o.add(Or(Not(A2), 4 * x - y >= -4))
o.add(Or(A2, 2 * x - y >= -6))
z = o.minimize(Abs(x)*2)   # Objective function: f(x)=x

print(o.check())
print(o.model())
print(f"Optimal value: {z.value()}")