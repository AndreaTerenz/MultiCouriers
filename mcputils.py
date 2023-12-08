import functools
import json
import pathlib
import re
from enum import Enum
from timeit import default_timer as timer

import numpy as np
from z3 import *


class ModelResult(Enum):
    Unknown = -1
    Satisfied = 0
    Unsatisfied = 1
    Feasible = 2


def print_heading(f):
    @functools.wraps(f)
    def foo(*args, **kwargs):
        print("*" * 50)  # + f" {name}")
        return f(*args, **kwargs)

    return foo


@print_heading
def load_MCP(path: str):
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
def run_solver(s, solve_lambda, name="z3"):
    print(f"Solving with {name}...", end="")

    start = timer()
    res = solve_lambda(s)
    end = timer()

    print(f"done in {end - start:.3f} seconds")

    return res


@print_heading
def check_solver(result, vars_values, instance, optim_value=None, expected_res=None, print_only=False):
    n = instance["n_items"]
    m = instance["n_couriers"]
    load_sizes = instance["load_sizes"]
    item_sizes = instance["item_sizes"]
    dists = instance["distances"]

    assert expected_res is None or result == expected_res, f"Incorrect result (expected {expected_res})"

    print(str(result).split(".")[-1].upper())

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
        assert not print_only or tot <= load_sizes[i], f"Load constraint violated for courier {i}"

    print("Load sizes respected")

    deliv_len = len(delivered)
    deliv_set_len = len(set(delivered))

    assert not print_only or deliv_len == deliv_set_len, "Items delivered more than once"
    assert not print_only or deliv_set_len == n, "Not all items were delivered"

    print("All items delivered exactly once")

    if optim_value is not None:
        print(f"Optimized Z: {optim_value}")
    else:
        optim_value = obj

    return optim_value


def to_z3array(values, name, val_sort, idx_sort=IntSort()):
    output = Array(name, idx_sort, val_sort)
    for idx, ls in enumerate(values):
        output = Store(output, idx, ls)

    return output


def min_z3(values):
    m = values[0]
    for val in values[1:]:
        m = If(val < m, val, m)
    return m


def max_z3(values):
    m = values[0]
    for val in values[1:]:
        m = If(val > m, val, m)
    return m


def print_json(sol, obj, status, approach, instance_n, elapsed_time):
    optimality = str(status) == "OPTIMAL_SOLUTION"
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
            print("with")
            if approach in js:
                print("approach")
                if js[approach]["time"] <= int(elapsed_time) and js[approach]["obj"] <= obj:
                    print("return")
                    return
                print("del")
                del js[approach]
            print("data")
            js[approach] = data
            file.seek(0)
            json.dump(js, file, ensure_ascii=False)
    else:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


def print_empty_json(approach, instance_n):
    data = {str(approach): {"time": 300, "optimal": False, "obj": None, "solution": []}}
    root = pathlib.Path.cwd().parent
    path = root.joinpath("res").joinpath(approach[0:3].strip())
    if (path.joinpath(str(instance_n) + '.json')).exists():
        return
    with open(path.joinpath(str(instance_n) + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def move_zeros_to_end(arr):
    for i in range(arr.shape[0]):
        non_zeros = arr[i, arr[i] != 0]
        zeros = arr[i, arr[i] == 0]
        arr[i] = np.concatenate((non_zeros, zeros))
    return arr
