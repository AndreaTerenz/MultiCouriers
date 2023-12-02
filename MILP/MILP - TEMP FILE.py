from mip import *
import itertools
import time
import sys
sys.path.append('../MultiCouriers')
import mcutils


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
        if tmp != []:
            res.append(tmp)
    return res


def main():
    """
    IDEA: One Travelling salesman problem per courier
          (aka, one full connection table of booleans for selecting the path)
          -> Remove 'Assignments', use only the table and build constraints on top of it
    """
    m, n, load, size, dist_table = mcutils.read_inst(sys.argv[1])
    load.sort()
    model = Model(sense=MINIMIZE, solver_name=CBC) # use GRB for Gurobi
    Distances = [ model.add_var(name='distance '+str(i), var_type=INTEGER, lb=0, ub=sum(dist_table[0,:])) for i in range(m) ]
    Booleans = np.array([ model.add_var(name='bool '+str(i), var_type=BINARY) for i in range(m * dist_table.size) ])
    Booleans = np.reshape(Booleans, (m,n+1,n+1))
    TEMP = np.reshape([ model.add_var(name='temp '+str(i), var_type=BINARY) for i in range(m * len(dist_table)) ], (m,len(dist_table)))
    OBJ_VAL = model.add_var(name='final val', var_type=INTEGER, lb=0)

    for l in range(m):
        model += OBJ_VAL >= Distances[l]
    model.objective = minimize(OBJ_VAL)
    # model.objective = minimize(xsum(Distances))

    for l in range(m):
        for j in range(n+1):
            model += xsum(np.concatenate((Booleans[l,j,:], Booleans[l,:,j]))) == 2 * TEMP[l,j]  # Every house is part of either 2 or 0 travels :D

    for l in range(n):
        model += xsum(np.reshape(np.concatenate((Booleans[:,l,:], Booleans[:,:,l])),-1)) == 2
        # Deliver every package, only once (checking that the sum of its indexes is 2 over all m)
    model += xsum(np.reshape(np.concatenate((Booleans[:,n,:], Booleans[:,:,n])), -1))  == 2 * m  # Not perfect, assumes every courier moves
    model += xsum(np.reshape(TEMP, -1)) == n + m  # Redundant constraint

    for l in range(m):
        for x in range(n):
            for y in range(n):
                model += Booleans[l,x,y] + Booleans[l,y,x] <= 1
                # No looping between houses

        model += xsum(np.reshape(np.multiply(Booleans[l,:,:], dist_table),-1)) == Distances[l]
        # Calculate Distances

        model += xsum(TEMP[l,:-1] * size) <= load[l]
        # Load size

        model += xsum([Booleans[l,x,y] for x in range(n) for y in range(n) if x >= y]) == 0
        model += Booleans[l,n,n] == 0
        # Symmetry breaking + No looping between houses


    for l in range(m):
        for loop in range(2, n-m+1):
            for t in itertools.combinations(range(n), loop):  # Of size loop, in range n
                model += xsum(give_arcs(Booleans[l, :, :], t)) <= loop -1
                # Avoid separate loops (?)

    #Load_after = [ model.add_var(name='load '+str(i), var_type=INTEGER, lb=0, ub=sum(size)) for i in range(n) ]
    #for l in range(m):
    #    for x in range(n):
    #        for y in range(n):
    #            if x<y and size[x] + size[y] <= load[l]:
    #                model+= Load_after[x] - Load_after[y] + load[l] * (Booleans[l,x,y] + Booleans[l,y,x]) <= load[l] - size[y]
    #        model += Load_after[x] + sum(size) * (TEMP[l,x]-1) <= load[l]
    #for x in range(n):
    #    model += size[x] <= Load_after[x]

    status = model.optimize(max_seconds=3000)
    time_end = time.time() - TIME_START
    if status == OptimizationStatus.OPTIMAL:
        print(f'optimal solution cost {model.objective_value} found')
    print(f'whole vector: {[i.x for i in Distances]}')
    print(f'booleans: \n{np.reshape([b.x for b in np.reshape(Booleans,-1)], Booleans.shape)}')
    print(f"TEMP: {np.reshape([t.x for t in np.reshape(TEMP,-1)], TEMP.shape)}")
    # print(f"Load_After: {[k.x for k in Load_after]}")


if __name__ == '__main__':
    main()
