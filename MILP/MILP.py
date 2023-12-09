from mip import *
import itertools
from timeit import default_timer as timer
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
import mcputils as utils


def give_arcs(M, nodes):
    res = np.array([])
    for t in itertools.combinations(nodes, 2):
        res = np.append(res, M[t])
    return res


def write_solution(m, n, Booleans):
    res = []
    for l in range(m):
        tmp = []
        for i in range(n):
            if np.sum([x.x for x in Booleans[l, i, :-1]]) + np.sum([x.x for x in Booleans[l, :-1, i]]) > 0:
                tmp.append(i)
        if tmp:
            res.append(tmp)
    return res


def print_output(assignments, status, obj, instance, instance_n, solver, time):
    tours = np.vectorize(lambda v: int(v.x))(assignments)
    tours = np.multiply(tours, np.arange(len(tours[0])) + 1)[:, :-1]  # Remove origin from results
    tours = utils.move_zeros_to_end(tours)

    res = utils.ModelResult.Unknown
    match status:
        case OptimizationStatus.FEASIBLE: res = utils.ModelResult.Feasible
        case OptimizationStatus.OPTIMAL: res = utils.ModelResult.Satisfied
        case OptimizationStatus.INFEASIBLE: res = utils.ModelResult.Unsatisfied

    utils.check_solver(res, tours, instance)
    utils.print_json(tours.tolist(), obj, res, "MIP with " + str(solver), instance_n, time)


def main(inst_path, solver):
    """
    IDEA: One Travelling salesman problem per courier
          (aka, one full connection table of booleans for selecting the path)
          -> Remove 'Assignments', use only the table and build constraints on top of it
    """
    m, n, load, size, dist_table, instance = utils.load_MCP(inst_path)
    dist_table = np.stack(dist_table)
    model = Model(sense=MINIMIZE, solver_name=solver)
    model.verbose = 0

    start = timer()
    load.sort()
    Distances = [model.add_var(name='distance ' + str(i), var_type=INTEGER, lb=0, ub=sum(dist_table[0, :])) for i in
                 range(m)]
    Booleans = np.array([model.add_var(name='bool ' + str(i), var_type=BINARY) for i in range(m * dist_table.size)])
    Booleans = np.reshape(Booleans, (m, n + 1, n + 1))
    # noinspection PyTypeChecker
    Assignments = np.reshape(
        [model.add_var(name='temp ' + str(i), var_type=BINARY) for i in range(m * len(dist_table))],
        (m, len(dist_table)))
    OBJ_VAL = model.add_var(name='final val', var_type=INTEGER, lb=0)
    MAX_DIST = 0
    for d in range(n):
        MAX_DIST = max(MAX_DIST, min(dist_table[d][n], dist_table[n][d]))

    for l in range(m):
        model += OBJ_VAL >= Distances[l]
    model += OBJ_VAL >= MAX_DIST
    model.objective = minimize(OBJ_VAL)

    for l in range(m):
        for j in range(n + 1):
            model += xsum(np.concatenate((Booleans[l, j, :], Booleans[l, :, j]))) == 2 * Assignments[l, j]
            # Every house is part of either 2 or 0 travels
            model += xsum(Booleans[l, j, :]) <= 1
            model += xsum(Booleans[l, :, j]) <= 1
            # Each courier enters & leaves each house once

    for p in range(n):
        model += xsum(np.reshape(np.concatenate((Booleans[:, p, :], Booleans[:, :, p])), -1)) == 2
        # Deliver every package, only once (checking that the sum of its indexes is 2 over all m)
    model += xsum(np.reshape(np.concatenate((Booleans[:, n, :], Booleans[:, :, n])), -1)) == 2 * m
    model += xsum(np.reshape(Assignments, -1)) == n + m  # Redundant constraint

    for l in range(m):
        for x in range(n):
            for y in range(n):
                model += Booleans[l, x, y] + Booleans[l, y, x] <= 1
            model += Booleans[l, x, x] == 0
        model += Booleans[l, n, n] == 0
        # No looping between houses

        model += xsum(np.reshape(np.multiply(Booleans[l, :, :], dist_table), -1)) == Distances[l]
        # Calculate Distances

        model += xsum(Assignments[l, :-1] * size) <= load[l]
        # Load size

        if l != 0:
            model += xsum(Assignments[l, :]) >= xsum(Assignments[l-1, :])
            # Symmetry breaking (due to ordered load_size)

    def avoid_loops(k, mip_model):
        for loop in range(2, n - m + 1):
            to_be_added = []
            for nodes in itertools.combinations(range(n), loop):  # Of size loop, in range n
                arcs = np.array([])
                for x in itertools.permutations(nodes, 2):
                    arcs = np.append(arcs, Booleans[k, :, :][x])
                to_be_added.append((xsum(arcs) <= loop - 1))
            lock.acquire()
            for eq in to_be_added:
                mip_model += eq
            lock.release()

    lock = threading.Lock()
    args_list = [(k, model) for k in range(m)]
    with ThreadPoolExecutor(max_workers=len(args_list)) as executor:  # 'with' is necessary here to wait for completion
        executor.map(lambda args: avoid_loops(*args), args_list)

    print("Preprocessing done!")
    model.threads = 8
    mid = timer() - start
    if mid > 300:
        print("Preprocessing took the whole time available.")
        utils.print_empty_json("MIP with " + str(solver), str(inst_path)[-6:-4])
        return
    status = model.optimize(max_seconds=300 - mid)
    end = timer() - start
    if status == OptimizationStatus.OPTIMAL:
        print(f'Optimal solution cost {model.objective_value} found')
    print(f'whole vector: {[i.x for i in Distances]}')
    # print(f'booleans: \n{np.reshape([b.x for b in np.reshape(Booleans, -1)], Booleans.shape)}')
    print(f"Assignments: {np.reshape([t.x for t in np.reshape(Assignments, -1)], Assignments.shape)}")
    print("Elapsed time:", round(end, 2), "seconds, of which", round(mid, 2), "were pre-processing.")

    data = {"n_couriers": m, "n_items": n, "load_sizes": load, "item_sizes": size, "distances": dist_table}
    if status.value < 5:
        print(status.value)
        print_output(Assignments, status, model.objective_value, data, str(inst_path)[-6:-4], solver, int(end))
    else:
        utils.print_empty_json("MIP with " + str(solver), str(inst_path)[-6:-4])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
