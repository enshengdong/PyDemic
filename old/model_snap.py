from snap import *
import numpy as np
# import sys

"""
Comment
"""

def printStats(s, g):
    '''
    Print graph statistics
    '''
    print "g %s, nodes %d, edges %d, empty %s" % (s, g.GetNodes(), g.GetEdges(), "yes" if g.Empty() else "no")

def addEdge(g, x, y):
    if g.AddEdge(x, y)  < 0:
        raise ValueError('Failed to add an edge between nodes ' + str(x) + " and " + str(y))

def addNode(g, i):
    if g.AddNode(i) < 0:
        raise ValueError('Failed to add node ' + str(i))

def addFltAttrN(g, attr):
    if g.AddFltAttrN(attr) < 0:
        raise ValueError('Failed to add node attribute ' + attr)

# print(sys.version)

# --- CREATE NETWORK
g = TNEANet.New()
printStats("Test Model", g)

# --- ADD ATTRIBUTES
addFltAttrN(g, "s")
addFltAttrN(g, "im")
addFltAttrN(g, "i1")
addFltAttrN(g, "i2")
addFltAttrN(g, "i3")
addFltAttrN(g, "i4")
addFltAttrN(g, "c1a")
addFltAttrN(g, "c1b")
addFltAttrN(g, "c2a")
addFltAttrN(g, "c2b")
addFltAttrN(g, "r")
addFltAttrN(g, "d")
addFltAttrN(g, "pn")
addFltAttrN(g, "pe")
addFltAttrN(g, "ps")
addFltAttrN(g, "pw")
addFltAttrN(g, "pstay")

# --- CONSTANTS
population = 100
immune_percentage = .15

# --- NETWORK-WIDE METRICS
c_total = 0

# --- ADD 256 * 256 NODES
for i in range(0, 256 * 256):
    addNode(g, i)
    # print(g.GetFltAttrDatN(0, "s"))
    g.AddFltAttrDatN(i, population * (1 - immune_percentage), "s")
    # print(g.GetFltAttrDatN(0, "s"))
    g.AddFltAttrDatN(i, population * immune_percentage, "im")
    # g.AddFltAttrDatN(i, 0.0, "i1")
    # g.AddFltAttrDatN(i, 0.0, "i2")
    # g.AddFltAttrDatN(i, 0.0, "i3")
    # g.AddFltAttrDatN(i, 0.0, "i4")
    # g.AddFltAttrDatN(i, 0.0, "c1a")
    # g.AddFltAttrDatN(i, 0.0, "c1b")
    # g.AddFltAttrDatN(i, 0.0, "c2a")
    # g.AddFltAttrDatN(i, 0.0, "c2b")
    # g.AddFltAttrDatN(i, 0.0, "r")
    # g.AddFltAttrDatN(i, .5, "pn")
    # g.AddFltAttrDatN(i, .05, "pe")
    # g.AddFltAttrDatN(i, .1, "ps")
    # g.AddFltAttrDatN(i, .05, "pw")
    # g.AddFltAttrDatN(i, .3, "pstay")

printStats("Test Model", g)
print(g.GetFltAttrDatN(0, "s"))
# CONNECT ALL NODES (undirected graph)
for i in range(0, 256 * 256):
    if i < 256:
        if i % 256 == 0:
            # leftmost point, connect with +256, +1
            addEdge(g, i, i + 256)
            addEdge(g, i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with +256, -1
            addEdge(g, i, i + 256)
            addEdge(g, i, i - 1)
        else: 
            # middle, connect with +256, -1, +1
            addEdge(g, i, i + 256)
            addEdge(g, i, i - 1)
            addEdge(g, i, i + 1)
    elif i >= 65280:
        if i % 256 == 0:
            # leftmost point, connect with -256, +1
            addEdge(g, i, i - 256)
            addEdge(g, i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with -256, -1
            addEdge(g, i, i - 256)
            addEdge(g, i, i - 1)

        elif i % 255 != 0:
            # middle, connect with -256, -1, +1
            addEdge(g, i, i - 256)
            addEdge(g, i, i - 1)
            addEdge(g, i, i + 1)
    else:
        if i % 256 == 0:
            # leftmost point, connect with -256, +256, +1
            addEdge(g, i, i - 256)
            addEdge(g, i, i + 256)
            addEdge(g, i, i + 1)
        elif i % 255 == 0: 
            # rightmost point, connect with -256, +256, -1
            addEdge(g, i, i - 256)
            addEdge(g, i, i + 256)
            addEdge(g, i, i - 1)
        else:
            # middle, connect with -256, +256, -1, +1
            addEdge(g, i, i - 256)
            addEdge(g, i, i + 256)
            addEdge(g, i, i - 1)
            addEdge(g, i, i + 1)

printStats("Test Model", g)

# img = Image.new( 'RGB', (255,255), "black") # create a new black image
# pixels = img.load() # create the pixel map
print(g.GetFltAttrDatN(0, "s"))
t = (256, 256)
p1 = np.zeros(t, dtype=np.float64)
p2 = np.zeros(t, dtype=np.float64)
p3 = np.zeros(t, dtype=np.float64)
print(g.GetFltAttrDatN(0, "s"))
# get all the nodes
NI = g.BegNI()

for i in range(0, 1):
    for j in range(0, 1):
        NI.Next()
        print(i + j)
        print(g.GetFltAttrDatN(NI, "s"))
        print(g.GetFltAttrDatN(NI, "im"))
        print(g.GetFltAttrDatN(NI, "i1"))  
        print(g.GetFltAttrDatN(NI, "i2"))
        print(g.GetFltAttrDatN(NI, "i3"))
        print(g.GetFltAttrDatN(NI, "i4"))
        print(g.GetFltAttrDatN(NI, "c1a"))
        print(g.GetFltAttrDatN(NI, "c2a"))

        # p1[i,j] = (g.GetFltAttrDatN(i + j, "s") + g.GetFltAttrDatN(i + j, "im"))
        # p2[i,j] = (g.GetFltAttrDatN(i + j, "i1") + g.GetFltAttrDatN(i + j, "i2") + g.GetFltAttrDatN(i + j, "i3") + g.GetFltAttrDatN(i + j, "i4"))
        # p3[i,j] = (g.GetFltAttrDatN(i + j, "c1a") + g.GetFltAttrDatN(i + j, "c2a"))

# print(p1)
# print(p2)
# print(p3)



# for i in range(img.size[0]):    # for every pixel:
#     for j in range(img.size[1]):
#         pixels[i,j] = (i, j, 100) # set the colour accordingly
# img.show()

# get all the nodes
# NCount = 0
# NI = Graph.BegNI()
# while NI < Graph.EndNI():
#     NCount += 1
#     NI.Next()

# with open("/Users/paul.warren/Documents/ebola/data/roadNet-CA.txt", "r") as f:
#     for line in f.readlines():
#         parts = line.split()
#         g.AddEdge(int(parts[0]), int(parts[1]))

# print("done with shit")






