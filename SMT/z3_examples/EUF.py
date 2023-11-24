from z3 import *

# See:
# https://theory.stanford.edu/~nikolaj/programmingz3.html#sec-euf--equality-and-uninterpreted-functions:~:text=of%20the%20citations.-,3.1,-.%E2%80%82EUF%3A%20Equality


S = DeclareSort('S')
f = Function('f', S, S)
x = Const('x', S)

# This is solvable if f is the identiy function:
# Since f(f(x)) = x, then f(f(f(x))) = f(x)
# Since we also say that f(f(f(x))) = x, we then have f(x) = x
solve(f(f(x)) == x, f(f(f(x))) == x)

# This is not solvable - the first two propositions
# imply that f is the identity function (see above)
# so the whole formula would be f(x) = x AND f(x) != x (impossible)
solve(f(f(x)) == x, f(f(f(x))) == x, f(x) != x)