

def load_MCP(path: str) -> dict:
    with open(path) as f:
        lines = f.readlines()
    count = len(lines)

    output = {"n_couriers": int(lines[0]), "n_items": int(lines[1]),
              "load_sizes": [int(l) for l in lines[2].split(" ")], "item_sizes": [int(l) for l in lines[3].split(" ")],
              "distances": [[int(d) for d in lines[i].split(" ")] for i in range(4, count)]}

    assert output["n_items"] >= output["n_couriers"],\
        f"Invalid instance - too few items (should be at least n_couriers+1 = {output['n_couriers']})"

    return output

if __name__ == '__main__':
    print(load_MCP("instance.mcp"))