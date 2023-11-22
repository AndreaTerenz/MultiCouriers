from z3 import *

"""
There is an island in which certain inhabitants, called knights, always 
tell the truth, and the others, called knaves, always lie. It is assumed 
that every inhabitant of this island is either a knight or a knave.

Suppose an inhabitant A says: “Either I am a knave or B is a knight.” 
What are A and B?
"""

# For both A and B, if they are a knight they cannot be a knave (and vice versa)
AKnight = Bool("AKnight")
BKnight = Bool("BKnight")

s = Solver()

AStat = Or(Not(AKnight), BKnight)
# IF A is a knight THEN their statement is TRUE (either they are a knave or b is a knight)
s.add(Implies(AKnight, AStat))
# IF A is a knave THEN their statement is FALSE (i.e., the opposite is true)
s.add(Implies(Not(AKnight), Not(AStat)))

print(s.check())
print(s.model())