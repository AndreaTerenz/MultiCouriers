from z3 import *

p, q, r = Bools("p q r")
s = Solver()

s.add(Implies(p,q))
s.add(Not(q))

print(s.check())    # check the formula:    (p->q) AND !q (sat)

s.push()    # "store" the current state of the solver
s.add(p)
print(s.check())    # check the formula:    (p->q) AND !q AND p (unsat)
s.pop()     # "reload" the last saved state of the solver

print(s.check())    # check again the formula:  (p->q) AND !q (again, sat)
