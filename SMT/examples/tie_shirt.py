from z3 import *

# Create two variables Tie and Shirt
Tie, Shirt = Bools('Tie Shirt')

s = Solver()
# Define formula
s.add(
  Or(Tie, Shirt),
  Or(Not(Tie), Shirt),
  Or(Not(Tie), Not(Shirt))
)

# Check if satisfiable
print(s.check())

# Print solution
print(s.model())
