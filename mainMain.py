import pathlib
import sys
from Minizinc import Minizinc
from MILP import MILP
# from SAT_SMT import mainZ3

std_path = pathlib.Path.cwd()
instance_path = std_path.joinpath("Instances")
instance_arg = instance_path.joinpath(f"inst{int(sys.argv[2]) :02d}.dat")
method = sys.argv[1]
solver = sys.argv[3]
print(f"Method: {method}, instance: inst{int(sys.argv[2]) :02d}.dat, solver: {solver}")

match method:
    case "Minizinc": Minizinc.main(instance_arg, solver)
    case "MIP" | "MILP": MILP.main(instance_arg, solver)
    # case "SAT": mainZ3.main(instance_arg, solver)
    case "SMT": print("No, sorry.")


