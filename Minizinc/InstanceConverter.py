import os
import time

Inst = os.listdir("Instances")
start = time.time()
for i in Inst:
    if not os.path.exists(i[:-3]+"dzn"):
        print(i)
        f = open("Instances/" + i, "r")
        Lines = f.readlines()
        m = int(Lines[0])
        n = int(Lines[1])
        load = [int(x) for x in Lines[2].split()]
        load.sort()
        size = [int(x) for x in Lines[3].split()]
        f.close()

        o = open(i[:-3]+"dzn", "a")
        o.write("m="+str(m)+";\n")
        o.write("n="+str(n)+";\n")
        o.write("load="+str(load)+";\n")
        o.write("size="+str(size)+";\n")
        o.write("dist=[|" + str([int(x) for x in Lines[4].split()])[1:-1] + ",")
        for n in range(5,len(Lines)):
            if Lines[n] != "":
                o.write("|" + str([int(x) for x in Lines[n].split()])[1:-1] + ",")
        o.write("|];")
        o.close()
print("Elapsed time: " + str(time.time() - start))
