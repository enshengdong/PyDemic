from snap import *

"""
Comment
"""

def printGStats(s, Graph):
    '''
    Print graph statistics
    '''

    print "graph %s, nodes %d, edges %d, empty %s" % (
        s, Graph.GetNodes(), Graph.GetEdges(),
        "yes" if Graph.Empty() else "no")

def DefaultConstructor():
    '''
    Test the default constructor
    '''

    Graph = TNEANet.New()
    PrintGStats("DefaultConstructor:Graph", Graph)

g = TNEANet.New()
g.AddFltAttrN("immune")
g.AddFltAttrN("susceptible")
g.AddFltAttrN("recovered")
g.AddFltAttrN("infected")
g.AddFltAttrN("dead")
g.AddFltAttrN("total")

printGStats("CA ROADS", g)

for i in range(0, 1971281):
	g.AddNode(i)


printGStats("CA ROADS", g)

# with open("/Users/paul.warren/Documents/ebola/data/roadNet-CA.txt", "r") as f:
#     for line in f.readlines():
#         parts = line.split()
#         g.AddEdge(int(parts[0]), int(parts[1]))

printGStats("CA ROADS", g)

# get all the nodes
# NCount = 0
# NI = Graph.BegNI()
# while NI < Graph.EndNI():
#     NCount += 1
#     NI.Next()

# print("done with shit")






