from graph_tool.all import *
from PIL import Image
import heatmap
import numpy as np
import time

class payload():
    def __init__(self, s, im, i1, i2, i3, i4, c1a, c1b, c2a, c2b, r, d, pN, pE, pS, pW, pStay):
        self.susceptible  = s
        self.immune       = im
        self.incubation1  = i1
        self.incubation2  = i2
        self.incubation3  = i3
        self.incubation4  = i4
        self.contagious1a = c1a
        self.contagious1b = c1b
        self.contagious2a = c2a
        self.contagious2b = c2b
        self.recovered    = r
        self.dead         = d
        self.probNorth    = pN
        self.probEast     = pE
        self.probSouth    = pS
        self.probWest     = pW
        self.probStay     = pStay



# --- PRINT GRAPH STATISTICS (number of nodes, number of edges)
def printStats(g):
    print "nodes %d, edges %d " % (len(list(g.vertices())), len(list(g.edges())))

start = time.time()
# --- CREATE GRAPH (directed)
g = Graph()
print "CREATED GRAPH: " + str((time.time() - start))
start = time.time()

# --- ADD ATTRIBUTES (double-precision floating point)
g_payload  = g.new_vertex_property("object") 
g_immune       = g.new_vertex_property("double")
g_incubation1  = g.new_vertex_property("double")
g_incubation2  = g.new_vertex_property("double")
g_incubation3  = g.new_vertex_property("double")
g_incubation4  = g.new_vertex_property("double")
g_contagious1a = g.new_vertex_property("double")
g_contagious1b = g.new_vertex_property("double")
g_contagious2a = g.new_vertex_property("double")
g_contagious2b = g.new_vertex_property("double")
g_recovered    = g.new_vertex_property("double")
g_dead         = g.new_vertex_property("double")
g_probNorth    = g.new_vertex_property("double")
g_probEast     = g.new_vertex_property("double")
g_probSouth    = g.new_vertex_property("double")
g_probWest     = g.new_vertex_property("double")
g_probStay     = g.new_vertex_property("double")

print "ADDED VERTEX PROPERTIES: " + str((time.time() - start))
start = time.time()

# --- CONSTANTS
population = 100
immune_percentage = .15
GRAPH_SIZE = 256 * 256

# --- GRAPH-WIDE METRICS
c_total = 0

# --- ADD 256 * 256 VERTICES
vlist = g.add_vertex(GRAPH_SIZE)
print "ADDED VERTICES: " + str((time.time() - start))
start = time.time()

printStats(g)
# --- SET VERTEX PROPERTIES 
for i in range(0, GRAPH_SIZE):
    g_susceptible[g.vertex(i)]  = population * (1 - immune_percentage)
    g_immune[g.vertex(i)]       = population * immune_percentage
    g_incubation1[g.vertex(i)]  = 0.0
    g_incubation2[g.vertex(i)]  = 0.0
    g_incubation3[g.vertex(i)]  = 0.0
    g_incubation4[g.vertex(i)]  = 0.0
    g_contagious1a[g.vertex(i)] = 0.0
    g_contagious1b[g.vertex(i)] = 0.0
    g_contagious2a[g.vertex(i)] = 0.0
    g_contagious2b[g.vertex(i)] = 0.0
    g_recovered[g.vertex(i)]    = 0.0
    g_dead[g.vertex(i)]         = 0.0
    g_probNorth[g.vertex(i)]    = .5
    g_probEast[g.vertex(i)]     = .05
    g_probSouth[g.vertex(i)]    = .1
    g_probWest[g.vertex(i)]     = .05
    g_probStay[g.vertex(i)]     = .3

print "SET VERTEX PROPERTIES: " + str((time.time() - start))
start = time.time()

printStats(g)
# --- CONNECT ALL NODES (directed graph)
for i in range(0, GRAPH_SIZE):
    if i < 256:
        if i % 256 == 0:
            # leftmost point, connect with +256, +1
            g.add_edge(i, i + 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with +256, -1
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
        else: 
            # middle, connect with +256, -1, +1
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)
    elif i >= 65280:
        if i % 256 == 0:
            # leftmost point, connect with -256, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with -256, -1
            g.add_edge(i, i - 256)
            g.add_edge(i, i - 1)

        elif i % 255 != 0:
            # middle, connect with -256, -1, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)
    else:
        if i % 256 == 0:
            # leftmost point, connect with -256, +256, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0: 
            # rightmost point, connect with -256, +256, -1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
        else:
            # middle, connect with -256, +256, -1, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)

print "ADDED EDGES: " + str((time.time() - start))
start = time.time()

printStats(g)

s = (256, 256)
p1 = np.zeros(s, dtype=np.float64)
p2 = np.zeros(s, dtype=np.float64)
p3 = np.zeros(s, dtype=np.float64)

for i in range(0, GRAPH_SIZE / 256):
    for j in range(0, GRAPH_SIZE / 256):
        p1[i,j] = g_susceptible[g.vertex(i + j)] + g_immune[g.vertex(i + j)]
        p2[i,j] = g_incubation1[g.vertex(i + j)] + g_incubation2[g.vertex(i + j)] + g_incubation3[g.vertex(i + j)] + g_incubation4[g.vertex(i + j)]
        p3[i,j] = g_contagious1a[g.vertex(i + j)] + g_contagious2a[g.vertex(i + j)]

import ColorMap

print p1

img1 = Image.fromarray(ColorMap.colorMap(p1))
img1.save("/Users/paul.warren/Documents/ebola/images/mapped.png")

print "FINISHED IMAGE SHIT: " + str((time.time() - start))
# v[0].g_susceptible 


# img1.show()

# img = Image.new('RGB', (256,256), "black")
# pixels = img.load()
# for i in range(img.size[0]):    # for every pixel:
#     for j in range(img.size[1]):

#         pixels[i,j] = (i, j, 100) # set the colour accordingly
# img.show()

# # img = Image.new( 'RGB', (255,255), "black") # create a new black image
# # pixels = img.load() # create the pixel map
# print(g.GetFltAttrDatN(0, "s"))
# t = (256, 256)

# print(g.GetFltAttrDatN(0, "s"))
# # get all the nodes
# NI = g.BegNI()

# for i in range(0, 1):
#     for j in range(0, 1):
#         NI.Next()
#         print(i + j)
#         print(g.GetFltAttrDatN(NI, "s"))
#         print(g.GetFltAttrDatN(NI, "im"))
#         print(g.GetFltAttrDatN(NI, "i1"))  
#         print(g.GetFltAttrDatN(NI, "i2"))
#         print(g.GetFltAttrDatN(NI, "i3"))
#         print(g.GetFltAttrDatN(NI, "i4"))
#         print(g.GetFltAttrDatN(NI, "c1a"))
#         print(g.GetFltAttrDatN(NI, "c2a"))

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
#         g.g.add_edge(int(parts[0]), int(parts[1]))

# print("done with shit")






