from z3 import *

# Z is the set of all integers
Z = IntSort()

# Define a function f that maps from Z to Z
f = Function("f", Z, Z)

# Define three integers x,y,z
x, y, z = Ints("x y z")
# Define an array A (it's more like a dictionary),
# where indices are integers (Z) and so are the values stored (Z)
A = Array("A", Z, Z)

# Define a formula fml as an implication
# In the RHS, the Store(Arr, i, v) function sets Arr[i] to v
# accessing index [y-2] after the store means accessing the element at index y-2
# in the array AFTER it has been updated with store
fml = Implies(x + 2 == y, f(Store(A, x, 3)[y-2]) == f(y-x+1))

# Check if the NEGATION of fml is satisfiable (it isn't)
# Assuming x+2==y -> x == y-2 -> the RHS becomes f(Store(A, x, 3)[x]) == f(3)
# Since we use Store to set A[x]:=3, it follows that f(A[x]) == f(3) REGARDLESS OF f ITSELF
# Therefore, fml is satisfied for any f -> Not(fml) is never satisfied
solve(Not(fml))