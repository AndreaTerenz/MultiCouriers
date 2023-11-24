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

if __name__ == '__main__':
    print(load_MCP("instance.mcp"))
    #random_instance()