from z3 import *

# Declare a new type (i.e., "sort") called S
S = DeclareSort("S")
# Declare 6 constants of type S
a,b,c,d,e,s,t = Consts("a b c d e s t", S)

# f is a function from S^2 to S
f = Function("f", S, S, S)
# g is a function from S to S
g = Function("g", S, S)

# Solving this means: can we find definitions for f & g and values
# for the constants such that the equalities in the beginning (a==b, b==c, etc...)
# and f(a, g(d)) != f(g(e), b) hold?
# The answer is yes
solve([a==b, b==c, d==e, b==s, d==t, f(a, g(d)) != f(g(e), b)])

"""
Output:

[c = S!val!0,
e = S!val!1,
t = S!val!1,
d = S!val!1,
a = S!val!0,
b = S!val!0,
s = S!val!0,
f = [(S!val!2, S!val!0) -> S!val!4, else -> S!val!3],
g = [else -> S!val!2]]

every S!val!n is the n-th "placeholder" value in the domain of S

we find that 
c=a=b=s=0
e=t=d=1
f(x,y) = 4 if x=2,y=0 else 3
g(x) = 2
"""