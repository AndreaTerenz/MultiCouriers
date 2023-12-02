import re

import numpy.random

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

def check_solver(result, vars, instance, get_val_lambda, optim_value = None, expected_res = None, unsat_val = None):
    print("*" * 50)

    n = instance["n_items"]
    m = instance["n_couriers"]
    load_sizes = instance["load_sizes"]
    item_sizes = instance["item_sizes"]
    dists = instance["distances"]

    assert expected_res is None or result == expected_res, f"Incorrect result (expected {expected_res})"

    if unsat_val is not None:
        if result == unsat_val:
            print("UNSATISFIABLE")
            return

        print("SATISFIABLE")

    vars_values = [[get_val_lambda(vars[i][k]) for k in range(n-m+1)] for i in range(m)]

    delivered = []

    if optim_value is not None:
        print(f"Optimized Z: {optim_value}")

    for i in range(m):
        print(f"Courier {i}: ", end="")

        tot = 0
        last_stop = -1
        travelled = 0

        for k in range(n-m+1):
            v = vars_values[i][k]
            if v != -1:
                delivered.append(v)
                tot += item_sizes[v]
                print(f"{v:2}", end=" ")
            else:
                print("--", end=" ")

            travelled += dists[last_stop][v]
            last_stop = v

        print(f"\t carried: {tot:2} - travelled: {travelled}")
        assert tot <= load_sizes[i], f"Load constraint violated for courier {i}"

    print("Load sizes respected")

    deliv_len = len(delivered)
    deliv_set_len = len(set(delivered))

    assert deliv_len == deliv_set_len, "Items delivered more than once"
    assert deliv_set_len == n, "Not all items were delivered"

    print("All items delivered exactly once")

if __name__ == '__main__':
    print(load_MCP("instance.mcp"))
    #random_instance()