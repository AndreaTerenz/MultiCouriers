import datetime
from timeit import default_timer as timer
from minizinc import Instance, Model, Solver
import sys
sys.path.append('../MultiCouriers')
import mcutils


def main():
    m, n, load, size, dist_table = mcutils.read_inst(sys.argv[1])

    model = Model("BaseModel Improved.mzn")
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

    if str(result.status) is not "UNKNOWN":
        mcutils.print_result(result["Tours"], result.status, instance)
        mcutils.print_json(result["Tours"], result.status, "CP with " + solver, sys.argv[1][-6:-4], end - start)
    else:
        mcutils.print_empty_json("CP with " + solver, sys.argv[1][-6:-4])


if __name__ == '__main__':
    main()
