import pathlib
import json
import re
import numpy as np
import os


def print_json(sol, obj, status, approach, instance_n, elapsed_time):
    optimality = str(status) == "OPTIMAL_SOLUTION"
    if elapsed_time >= 300:
        optimality = False
        elapsed_time = 300

    root = pathlib.Path.cwd().parent
    path = root.joinpath("res").joinpath(approach[0:3].strip())
    if (path.joinpath(str(instance_n)+'.json')).exists():
        with open(path.joinpath(str(instance_n)+'.json'), 'r') as file:
            data = json.load(file)
            if approach in data:
                if data[approach]["time"] <= int(elapsed_time) and data[approach]["obj"] <= obj:
                    return
                else:
                    os.remove(path.joinpath(str(instance_n)+'.json'))

    empty = np.min(np.stack(sol))
    for c in range(len(sol)):
        sol[c] = list(filter(lambda a: a != empty, sol[c]))
    data = {str(approach): {"time": int(elapsed_time), "optimal": optimality, "obj": obj, "sol": sol}}

    with open(path.joinpath(str(instance_n)+'.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def print_empty_json(approach, instance_n):
    data = {str(approach): {"time": 300, "optimal": False, "obj": None, "solution": []}}
    root = pathlib.Path.cwd().parent
    path = root.joinpath("res").joinpath(approach[0:3].strip())
    if (path.joinpath(str(instance_n) + '.json')).exists():
        return
    with open(path.joinpath(str(instance_n) + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def load_MCP(path: str) -> dict:
    print(f"Loading instance from: {path}")
    with open(path) as f:
        lines = f.readlines()
    lines = [l.strip() for l in lines]
    count = len(lines)

    output = {"n_couriers": int(lines[0]), "n_items": int(lines[1]),
              "load_sizes": [int(l) for l in re.split(r"\s+", lines[2])],
              "item_sizes": [int(l) for l in re.split(r"\s+", lines[3])],
              "distances": [[int(d) for d in re.split(r"\s+", lines[i])] for i in range(4, count)]}

    assert output["n_items"] >= output["n_couriers"],\
        f"Too few items (should be at least n_couriers+1 = {output['n_couriers']})"
    assert output["n_couriers"] == len(output["load_sizes"]),\
        f"Mismatch between load sizes ({len(output['load_sizes'])}) and courier count ({output['n_couriers']})"
    assert output["n_items"] == len(output["item_sizes"]),\
        f"Mismatch between item sizes ({len(output['item_sizes'])}) and item count ({output['n_items']})"

    return output


def read_inst(inst_path):
    inst = load_MCP(inst_path)

    m = inst["n_couriers"]
    n = inst["n_items"]
    load = inst['load_sizes']
    size = inst['item_sizes']
    dist_table = inst["distances"]

    print("Couriers:", m)
    print("Packages:", n)
    print("Max load sizes:", load)
    print("Packages size:", size)
    print("Distances matrix:", *dist_table, sep="\n")
    return m, n, load, size, dist_table


def print_result(results, status, instance):
    print("*" * 50)

    n = instance["n"]
    m = instance["m"]
    load_sizes = instance["load"]
    item_sizes = instance["size"]
    dists = instance["dist"]

    print(status)
    if str(status) == "UNKNOWN":
        return
    delivered = []

    obj = 0
    for i in range(m):
        print(f"Courier {i}: ", end="")

        tot = 0
        last_stop = -1
        travelled = 0

        for k in range(n - m + 1):
            v = results[i][k]
            if v != 0:
                delivered.append(v)
                tot += item_sizes[v-1]
                print(f"{v:2}", end=" ")
            else:
                print("--", end=" ")

            travelled += dists[last_stop][v-1]
            obj = max(travelled, obj)
            last_stop = v-1

        print(f"\t carried: {tot:2} - travelled: {travelled}")
        assert tot <= load_sizes[i], f"Load constraint violated for courier {i}"

    print("Load sizes respected")

    deliv_len = len(delivered)
    deliv_set_len = len(set(delivered))

    assert deliv_len == deliv_set_len, "Items delivered more than once"
    assert deliv_set_len == n, "Not all items were delivered"

    print("All items delivered exactly once")
    return obj


def move_zeros_to_end(arr):
    for i in range(arr.shape[0]):
        non_zeros = arr[i, arr[i] != 0]
        zeros = arr[i, arr[i] == 0]
        arr[i] = np.concatenate((non_zeros, zeros))
    return arr
