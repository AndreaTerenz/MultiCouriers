from constraints import *

"""
a hospital supervisor needs to create a schedule for n nurses over a fixed day period, subject to the following conditions:

- Each day is divided into three 8-hour shifts.
- Every day, each shift is assigned to a single nurse, and no nurse works more than one shift.
- Each nurse is assigned to a minimum amount of shifts during the given period.
"""

def nurses_sat(num_nurses, num_shifts, num_days):
    s = Solver()

    assignments = [[[Bool(f"s_{i}_{j}_{k}") for k in range(num_shifts)] for j in range(num_days)] for i in range(num_nurses)]

    # In each shift can work just one nurse
    for j in range(num_days):
        for k in range(num_shifts):
            s.add(exactly_one([assignments[i][j][k] for i in range(num_nurses)]))

    # Each nurse can work not more than one shift per day
    for i in range(num_nurses):
        for k in range(num_shifts):
            s.add(at_most_one([assignments[i][j][k] for j in range(num_shifts)]))

    # If possible, shifts should be distributed evenly and fairly, so that each
    # nurse works the minimum amount of them.
    # If this is not possible, because the total number of shifts is not divisible
    # by the number of nurses, some nurses will be assigned one more shift,
    # without crossing the maximum number of shifts which can be worked
    # by each nurse

    balanced = (num_shifts % num_nurses == 0)
    min_shifts = (num_shifts * num_days) // num_nurses
    max_shifts = min_shifts
    if not balanced:
        max_shifts += 1

    for i in range(num_nurses):
        shifts = [assignments[i][j][k] for j in range(num_days) for k in range(num_shifts)]
        # Fair assignment constraints
        s.add(at_least_k_np(shifts, min_shifts))
        s.add(at_most_k_np(shifts, max_shifts))

    if s.check() != sat:
        return None

    m = s.model()

    return [(i, j, k) for i in range(num_nurses) for j in range(num_days) for k in range(num_shifts) if
            m.evaluate(assignments[i][j][k])]

instance1 = {
    "num_nurses" : 4,
    "num_shifts" : 3,
    "num_days" : 3
}

instance2 = {
    "num_nurses" : 4,
    "num_shifts" : 3,
    "num_days" : 4
}

for i, j, k in nurses_sat(**instance1):
    print(f"nurse #{i} works shift #{k} on day #{j}")
print("######################################")
for i, j, k in nurses_sat(**instance2):
    print(f"nurse #{i} works shift #{k} on day #{j}")