import os
import numpy as np
import math
import itertools
import json
import time
import math

INSTANCE = 4
Inst = os.listdir("../Instances")
inst_n = str(INSTANCE)
if INSTANCE < 10:
    inst_n = "0" + inst_n
f = open("../Instances/inst" + inst_n + ".dat", "r")
Lines = f.readlines()
TIME_START = time.time()
m = int(Lines[0])  # N. of couriers
n = int(Lines[1])  # N. of packages
if m > n:
    m = n  # No need for extra couriers
load = [int(x) for x in Lines[2].split()]
load.sort()
size = [int(x) for x in Lines[3].split()]

dist_table = np.zeros(shape=(len(Lines) - 4, len([int(x) for x in Lines[4].split()]))).astype(int)
for j in range(4, len(Lines)):
    dist_table[j - 4, :] = [int(x) for x in Lines[j].split()]
f.close()

from minizinc import Instance, Model, Solver

model = Model("BaseModel Improved.mzn")
gecode = Solver.lookup("gecode")
instance = Instance(gecode, model)

print(type(m), type(n), type(load), type(size), type(dist_table))

instance["m"] = m
instance["n"] = n
instance["load"] = load
instance["size"] = size
instance["dist"] = dist_table

print(m, n, load, size, dist_table)

result = instance.solve(processes=8, optimisation_level=2)
print(result)
