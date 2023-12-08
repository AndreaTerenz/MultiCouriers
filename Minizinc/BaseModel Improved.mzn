include "all_different.mzn";
% Inputs
int: n_couriers; % Number of couriers
int: n_items; % Number of packages
array[1..n_couriers] of int: load_sizes; % Maximum load capacity of each courier
array[1..n_items] of int: item_sizes; % Weight/size of each package
array[1..n_items+1, 1..n_items+1] of int: distances; % Distances from all places to one another
% Variables
array[1..n_items] of var 1..n_couriers: Assignment; % For each package, the courier transporting it

constraint forall(i in 1..n_couriers)(sum([item_sizes[j] | j in 1..n_items where Assignment[j] == i]) <= load_sizes[i]); % Do not exceed maximum load size
constraint forall(i in 1..n_couriers)(i in Assignment /\ Tours[i,1] != 0); % At least 1 package per courier, when possible

array[1..n_couriers] of var 1..n_items - n_couriers + 1: Count;
array[1..n_couriers, 1..n_items - n_couriers + 1] of var 0..n_items: Tours; % Each row, the complete tour of a courier
Count = [count(Assignment, i) | i in 1..n_couriers]; % Fill Count with the n. of packages
%constraint forall(i,j in 1..m where i > j)(if load[i] >= load[j] then Count[i] >= Count[j] else (Count[i] <= Count[j]) endif); % If a courier has more space, give priority to it -> Removed for Sorted array
constraint if (min(item_sizes) <= min(load_sizes)) then forall(i in 2..n_couriers)(Count[i-1] <= Count[i]) endif; % Symmetry breaking [SORTED ARRAY]
constraint forall(i in 1..n_couriers, j in (Count[i]+1)..n_items - n_couriers + 1)(Tours[i,j] = 0); % Pad the array

%constraint forall(i in 2..m)(Tours[i,2] >= Tours[i-1,2]); % Symmetry breaking #2 [WRONG, LOAD SIZE]
%constraint forall(i in 1..m)(Tours[i,1] == n+1 /\ Tours[i,Count[i]+2] == n+1); % Begin and end at the starting point //deprecated
constraint forall(i in 1..n_couriers)(alldifferent([Tours[i,j] | j in 1..Count[i]])); % Do not deliver the same package twice
%constraint forall(i in 1..m)(forall(j in 2..count(Assignment, i)+1)(Tours[i,j] in [c | c in 1..n where Assignment[c] == i])); % Deliver only the assigned packages
constraint forall(i in 1..n_couriers, j in 1..n_items where Assignment[j] == i)(j in [Tours[i,p] | p in 1..Count[i]]); % Deliver all the assigned packages

function var int: Objective() = max([sum(i in 2..Count[c])(distances[Tours[c, i-1],Tours[c, i]]) + distances[n_items+1, Tours[c, 1]] + distances[Tours[c, Count[c]], n_items+1] | c in 1..n_couriers]); % Compute objective function


solve minimize(Objective()); % Solve minimizing the maximum distance

output [show(Assignment)] ++ ["\n Maximum Distance: ", show(max([sum(i in 2..Count[c])(distances[Tours[c, i-1],Tours[c, i]]) + distances[n_items+1, Tours[c, 1]] + distances[Tours[c, Count[c]], n_items+1] | c in 1..n_couriers]))] ++ ["\n"] ++ [show(Tours)]