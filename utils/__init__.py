import functools
import json
import pathlib
import re
from enum import Enum
from timeit import default_timer as timer

import numpy as np


class ModelResult(Enum):
    Unknown = -1
    Satisfied = 0
    Unsatisfied = 1
    Feasible = 2


def print_heading(f):
    """
    Prints 50 asterisks to separate outputs neatly.
    """
    @functools.wraps(f)
    def foo(*args, **kwargs):
        print("*" * 50)  # + f" {name}")
        return f(*args, **kwargs)

    return foo


@print_heading
def load_MCP(path: str):
    """
    Loads instances from absolute or relative path.

    Arguments:
        path: str, path to the desired Instance.

    Returns:
        int: number of couriers;
        int: number of packages;
        list: maximum load size for each courier;
        list: size of each package;
        matrix: distances between houses;
        dict: all the above in standard form
    """
    print(f"Loading instance from: {path}")
    with open(path) as f:
        lines = f.readlines()
    lines = [l.strip() for l in lines]
    count = len(lines)

    data = {"n_couriers": int(lines[0]), "n_items": int(lines[1]),
            "load_sizes": [int(l) for l in re.split(r"\s+", lines[2])],
            "item_sizes": [int(l) for l in re.split(r"\s+", lines[3])],
            "distances": [[int(d) for d in re.split(r"\s+", lines[i])] for i in range(4, count)]}

    m = data["n_couriers"]
    n = data["n_items"]

    assert n >= m, \
        f"Too few items (should be at least n_couriers+1 = {m + 1})"

    loads = data['load_sizes']

    assert m == len(loads), \
        f"Mismatch between load sizes ({len(loads)}) and courier count ({m})"

    sizes = data['item_sizes']

    assert n == len(sizes), \
        f"Mismatch between item sizes ({len(sizes)}) and item count ({n})"

    dist_table = data["distances"]

    print("Couriers:", m)
    print("Packages:", n)
    print("Max load sizes:", loads)
    print("Packages size:", sizes)
    print("Distances matrix:", *dist_table, sep="\n")

    return m, n, loads, sizes, dist_table, data


@print_heading
def run_solver(s, solve_lambda, name=""):
    """
    Runs a solving process with given solver.

    Arguments:
        s: solver object
        solve_lambda: a lambda expression that runs a given solver and returns its result
        name: str, the name of the solver to show in the output, if any (defaults to "")

    Returns:
        ModelResult: result produced of the solver (usually some solver-dependent value to indicate optimal, feasible, unsatisfied, ecc...)
    """
    if name != "":
        print(f"Solving with {name}...", end="")
    else:
        print(f"Solving...", end="")

    start = timer()
    res = solve_lambda(s)
    end = timer()

    print(f"done in {end - start:.3f} seconds")

    return res


@print_heading
def check_solver(result: ModelResult, vars_values: list, instance: dict, optim_value: int = 0, expected_res : list =None, check_constrs=True):
    """
    Checks if the results of the solving process is within the bounds of the problem and prints the output.
    :param ModelResult result: output of the solving process;
    :param list vars_values: 2D array with the tours of each courier;
    :param dict instance: data of the given problem;
    :param int optim_value: if positive, the optimal solution of the problem - if non positive (defaults to 0), it will be computed from the courier tours
    :param list expected_res: if known, the expected tours for the couriers;
    :param bool check_constrs: toggle checks on the solution data (defaults to True)
    :return: the final value found by the solver
    :rtype int:
    """
    n = instance["n_items"]
    m = instance["n_couriers"]
    load_sizes = instance["load_sizes"]
    item_sizes = instance["item_sizes"]
    dists = instance["distances"]

    print(str(result).split(".")[-1].upper())

    if not check_constrs:
        print("(skipping constraint checks)")
    else:
        assert expected_res is None or result == expected_res, f"Incorrect result (expected {expected_res})"

    if result in [ModelResult.Unknown, ModelResult.Unsatisfied]:
        return

    if np.max(vars_values) == n:
        vars_values = np.array(vars_values) - 1
    delivered = []
    obj = 0

    for i in range(m):
        print(f"Courier {i}: ", end="")

        tot = 0
        last_stop = -1
        travelled = 0

        for k in range(n - m + 1):
            v = vars_values[i][k]

            if v != -1:
                delivered.append(v)
                tot += item_sizes[v]
                print(f"{v+1:2}", end=" ")
            else:
                print("--", end=" ")

            travelled += dists[last_stop][v]
            last_stop = v

        travelled += dists[last_stop][-1]
        obj = max(travelled, obj)

        print(f"\t carried: {tot:2} - travelled: {travelled}")
        if check_constrs:
            assert tot <= load_sizes[i], f"Load constraint violated for courier {i}"

    if check_constrs:
        print("Load sizes respected")

    deliv_len = len(delivered)
    deliv_set_len = len(set(delivered))

    if check_constrs:
        assert deliv_len == deliv_set_len, "Items delivered more than once"
        assert deliv_set_len == n, "Not all items were delivered"

        print("All items delivered exactly once")

    if optim_value != 0:
        print(f"Optimized Z: {optim_value}")
    else:
        optim_value = obj

    return optim_value


def print_json(sol, obj, status, approach, instance_n, elapsed_time):
    """
    Saves to a JSON file the results of a solver with a given approach and time.

    Arguments:
        sol: list, tours of the couriers;
        obj: int, value of the objective function;
        status: ModelResult, optimality value for the solution found;
        approach: str, the solving technique employed;
        instance_n: int, ID of the instance;
        elapsed_time: int, time in seconds for preprocessing + solving
    """
    optimality = status == ModelResult.Satisfied
    if elapsed_time >= 300:
        optimality = False
        elapsed_time = 300

    root = pathlib.Path.cwd()
    path = root.joinpath("res").joinpath(approach[0:3].strip())
    json_path = path.joinpath(f'{instance_n}.json')

    empty = np.min(np.stack(sol))
    if empty != 0:
        sol = list(np.array(sol) + 1)
    sol = [list(filter(lambda a: a != empty, sol[c])) for c in range(len(sol))]
    data = {str(approach): {"time": int(elapsed_time), "optimal": optimality, "obj": obj, "sol": sol}}

    if json_path.exists():
        with open(json_path, 'r+') as file:
            js = json.load(file)
            if approach in js:
                if js[approach]["time"] <= int(elapsed_time) and js[approach]["obj"] <= obj and js[approach]["optimal"]:
                    return
                del js[approach]
            js[approach] = data[approach]
            file.seek(0)
            json.dump(js, file, ensure_ascii=False)
    else:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


def print_empty_json(approach, instance_n):
    """
    Prints to a JSON file the result of a failed execution.

    Arguments:
        approach: str, the solving technique employed;
        instance_n: int, the ID of the instance}
    """
    data = {str(approach): {"time": 300, "optimal": False, "obj": None, "solution": []}}
    root = pathlib.Path.cwd()
    path = root.joinpath("res").joinpath(approach[0:3].strip())
    json_path = path.joinpath(f'{instance_n}.json')
    if json_path.exists():
        with open(json_path, 'r+') as file:
            js = json.load(file)
            if approach in js:
                return
            js[approach] = data[approach]
            file.seek(0)
            json.dump(js, file, ensure_ascii=False)
    else:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


def move_zeros_to_end(arr):
    """
    Moves all 0s present in an array to its tail.

    Arguments:
        arr: list, array of numbers to be separated from 0s

    Returns:
        array with 0s moved to the tail
    """
    for i in range(arr.shape[0]):
        non_zeros = arr[i, arr[i] != 0]
        zeros = arr[i, arr[i] == 0]
        arr[i] = np.concatenate((non_zeros, zeros))
    return arr
