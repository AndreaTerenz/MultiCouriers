import datetime
import os
from timeit import default_timer as timer
from minizinc import Instance, Model, Solver
import sys

#sys.path.append('../MultiCouriers')
#import mcutils as utils
import mcputils as utils


def main():
    m, n, load, size, dist_table, _ = utils.load_MCP(sys.argv[1])

    file_dir = os.path.dirname(os.path.abspath(__file__))
    model = Model(os.path.join(file_dir, "BaseModel Improved.mzn"))

    solver = "chuffed"
    gecode = Solver.lookup(solver)
    instance = Instance(gecode, model)
    instance["n_couriers"] = m
    instance["n_items"] = n
    instance["load_sizes"] = load
    instance["item_sizes"] = size
    instance["distances"] = dist_table

    start = timer()
    load.sort()
    result = instance.solve(processes=8, optimisation_level=2, timeout=datetime.timedelta(seconds=300-(timer()-start)))
    end = timer()
    print(f"Done in {end - start:.3f} seconds")
    res = str(result.status)

    match res:
        case "OPTIMAL_SOLUTION": res = utils.ModelResult.Satisfied
        case "UNSATISFIABLE": res = utils.ModelResult.Unsatisfied
        case "SATISFIED": res = utils.ModelResult.Feasible
        case "UNKNOWN": res = utils.ModelResult.Unknown

    if res != "UNKNOWN":
        obj = utils.check_solver(res, result["Tours"], instance)
        utils.print_json(result["Tours"], obj, result.status, "CP with " + solver, sys.argv[1][-6:-4], end - start)
    else:
        utils.print_empty_json("CP with " + solver, sys.argv[1][-6:-4])


if __name__ == '__main__':
    main()
