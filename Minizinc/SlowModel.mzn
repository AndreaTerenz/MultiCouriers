include "all_different.mzn";
% Inputs
int: m; % Number of couriers
int: n; % Number of packages
array[1..m] of int: load; % Maximum load capacity of each courier
array[1..n] of int: size; % Weight/size of each package
array[1..n+1, 1..n+1] of int: dist; % Distances from all places to one another
% Variables
array[1..n] of var 1..m: Assignment; % For each package, the courier transporting it
constraint forall(i in 1..m)(sum([size[j] | j in 1..n where Assignment[j] = i]) <= load[i]); % Do not exceed maximum load size
constraint if (n >=m /\ max(size) <= min(load)) then forall(i in 1..m)(i in Assignment) endif; % At least 1 package per courier, when possible

array[1..m] of var 1..n: Count;
array[1..n, 1..2] of var 1..n+1: Tours; % Each row, the previous & next destination w.r.t. a pack
Count = [count(Assignment, i) | i in 1..m]; % Fill Count with the n. of packages
%constraint forall(i,j in 1..m where i > j)(if load[i] >= load[j] then Count[i] >= Count[j] else (Count[i] <= Count[j]) endif); % If a courier has more space, give priority to it -> Removed for Sorted array
constraint if (max(size) <= min(load)) then forall(i in 2..m)(Count[i-1] <= Count[i]) endif; % Symmetry breaking [SORTED ARRAY]

constraint count([Tours[i,1]|i in 1..n], n+1)=card(array2set(Assignment)) /\ count([Tours[i,2]|i in 1..n], n+1) = card(array2set(Assignment)); % Begin and end at the starting point
constraint forall (i in 1..m)(alldifferent([Tours[j,1]|j in 1..n where Assignment[j] = i]) /\ n+1 in [Tours[j,1]| j in 1..n where Assignment[j] = i]); % Start from origin, do not loop
constraint forall (i in 1..m, p in 1..n where Assignment[p] = i)(p in [Tours[j,1]|j in 1..n where Assignment[j] = i /\ j != p] \/ p in [Tours[j,2]|j in 1..n where Assignment[j] = i /\ j != p] \/ (Count[i] = 1 /\ Tours[p,1] = n+1 /\ Tours[p,2] = n+1)); %deliver all packages
constraint forall (i in 1..m)(alldifferent([Tours[j,2]|j in 1..n where Assignment[j] = i]) /\ n+1 in [Tours[j,2]|j in 1..n where Assignment[j] = i]); % End at origin, do not loop

function var int: Objective() = max([sum([dist[i, Tours[i,2]] | i in 1..n where Assignment[n] = c]) + dist[n+1, b] | c in 1..m, b in 1..n where Tours[b,1] = n+1 /\ Assignment[b] = c]); % Compute objective function


solve minimize(Objective()); % Solve minimizing the maximum distance

output [show(Assignment)] ++ ["\n Maximum Distance: ", show(max([sum([dist[i, Tours[i,2]] | i in 1..n where Assignment[i] = c]) + dist[n+1, b] | c in 1..m, b in 1..n where Tours[b,1] = n+1 /\ Assignment[b] = c]))]
