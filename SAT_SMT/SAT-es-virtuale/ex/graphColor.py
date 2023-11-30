from SAT_SMT.constraints import *

"""
Given a graph (v1,...,vn,E) and d colors, we wanna assign a color to each vertex s.t.:
adjacent vertices have different colors, i.e.
if (vi, vj) \in E then color(vi) != color(vj)
"""

def coloring_graph(n, d, E):
    s = Solver()
    
    # We have to represent the assignment of a color to a vertex
    # vij = True --> vertex vi has color cj (if False, it doesn't)
    verts_colors = [[Bool(f"x_{i}_{j}") for j in range(d)] for i in range(n)]
    
    # Each vertex has at least one color
    for i in range(n):
        s.add(at_least_one(verts_colors[i]))
    
    # Each edge must have different colors in its vertices
    for v1, v2 in E:
        for col in range(d):
            n1 = Not(verts_colors[v1][col])
            n2 = Not(verts_colors[v2][col])
    
            s.add(Or(n1, n2))
    
    s.check()
    m = s.model()
    return [(i, j) for i in range(n) for j in range(d) if m.evaluate(verts_colors[i][j])]

graph = {
        "n" : 5,
        "d": 3,
        "E" : [
            (0, 2),
            (0, 4),
            (1, 2),
            (1, 4),
            (2, 3),
            (3, 4)
        ]
    }

print(coloring_graph(**graph))