import datetime
import os
from timeit import default_timer as timer
from minizinc import Instance, Model, Solver
import sys

sys.path.append('../MultiCouriers')
#import mcutils as utils
import mcputils as utils


def main():
    m, n, load, size, dist_table, _ = utils.load_MCP(sys.argv[1])

    file_dir = os.path.dirname(os.path.abspath(__file__))
    model = Model(os.path.join(file_dir, "BaseModel Improved.mzn"))

    solver = "gecode"
    gecode = Solver.lookup(solver)
    instance = Instance(gecode, model)
    instance["m"] = m
    instance["n"] = n
    instance["load"] = load
    instance["size"] = size
    instance["dist"] = dist_table

    start = timer()
    load.sort()
    result = instance.solve(processes=8, optimisation_level=2, timeout=datetime.timedelta(seconds=300-(timer()-start)))
    end = timer()
    print(f"Done in {end - start:.3f} seconds")

    res = str(result.status)

    if res != "UNKNOWN":
        # CHE SCHIFOOOOOOOOOOOOOOOOOOOOOOOO
        data = {
            "n_items": instance["n"],
            "n_couriers": instance["m"],
            "load_sizes": instance["load"],
            "item_sizes": instance["size"],
            "distances": instance["dist"]
        }

        match res:
            case "OPTIMAL_SOLUTION" : res = utils.ModelResult.Satisfied
            case "UNSATISFIABLE" : res = utils.ModelResult.Unsatisfied
            case "SATISFIED" : res = utils.ModelResult.Feasible
            case "UNKOWN" : res = utils.ModelResult.Unknown

        obj = utils.check_solver(res, result["Tours"], data, dumb_indexes=True)
        utils.print_json(result["Tours"], obj, result.status, "CP with " + solver, sys.argv[1][-6:-4], end - start)
    else:
        utils.print_empty_json("CP with " + solver, sys.argv[1][-6:-4])


if __name__ == '__main__':
    main()
