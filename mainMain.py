import argparse
import pathlib

from MILP import MILP
from Minizinc import Minizinc
from SAT_SMT import z3_SAT, z3_SMT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='MCPsolve',
                    description='Solve the Multiple Couriers Problem with different solvers & methods')

    #TODO: make sure the definition of each method is correct and makes sense
    parser.add_argument("-m", "--method",
                        choices=["Minizinc", "MIP", "MILP", "SAT", "SMT"],
                        help="Solving method (Minizinc for constraint programming, MIP or MILP for mixed int programming, SAT or SMT for logic something something", required=True)
    parser.add_argument("-i", "--instance_id",
                        type=int, help="ID of .dat file (in the Instances folder) containing the target problem instance", required=True)
    parser.add_argument("-s", "--solver",
                        help="select solver algorithm (only for Minizinc or MILP). If not provided, each method will use its default solver", default="")

    args = parser.parse_args()

    method = args.method
    inst_id = args.instance_id
    solver = args.solver

    std_path = pathlib.Path.cwd()
    instance_path = std_path.joinpath("Instances")
    instance_file = f"inst{inst_id:02d}.dat"
    instance_arg = instance_path.joinpath(instance_file)

    print(f"Method: {method}, instance: {instance_file}")
    if solver != "":
        print(f"solver: {solver}")

    match method:
        case "Minizinc":
            Minizinc.main(instance_arg, solver)
        case "MIP" | "MILP":
            MILP.main(instance_arg, solver)
        case "SAT":
            z3_SAT.main(instance_arg)
        case "SMT":
            z3_SMT.main(instance_arg)