import datetime
import os
from timeit import default_timer as timer
from minizinc import Instance, Model, Solver
import sys

#import mcputils as utils
import utils


def main(inst_path, solver_name):
    m, n, load, size, dist_table, _ = utils.load_MCP(inst_path)

    file_dir = os.path.dirname(os.path.abspath(__file__))
    model = Model(os.path.join(file_dir, "BaseModel Improved.mzn"))

    solver = Solver.lookup(solver_name)
    instance = Instance(solver, model)
    instance["n_couriers"] = m
    instance["n_items"] = n
    instance["load_sizes"] = load
    instance["item_sizes"] = size
    instance["distances"] = dist_table

    start = timer()
    load.sort()
    result = instance.solve(processes=8, optimisation_level=2, timeout=datetime.timedelta(seconds=0-(timer()-start)))
    end = timer()
    print(f"Done in {end - start:.3f} seconds")
    res = str(result.status)

    match res:
        case "OPTIMAL_SOLUTION": res = utils.ModelResult.Satisfied
        case "SATISFIED": res = utils.ModelResult.Satisfied
        case "UNSATISFIABLE": res = utils.ModelResult.Unsatisfied
        case "SATISFIED": res = utils.ModelResult.Feasible
        case "UNKNOWN": res = utils.ModelResult.Unknown

    if res != utils.ModelResult.Unknown:
        obj = utils.check_solver(res, result["Tours"], instance)
        utils.print_json(result["Tours"], obj, res, "CP with " + solver_name, str(inst_path)[-6:-4], end - start)
    else:
        utils.print_empty_json("CP with " + solver_name, sys.argv[1][-6:-4])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
