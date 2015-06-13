from graph_tool.all import *
from PIL import Image
import heatmap
import numpy as np
import time

class Payload():
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

# --- START
# --- CREATE GRAPH (directed)
g = Graph()

# --- ADD ATTRIBUTES (double-precision floating point)
g_payload = g.new_vertex_property("object") 

# --- CONSTANTS
population = 100
immune_percentage = .15
GRAPH_SIZE = 256 * 256

# --- GRAPH-WIDE METRICS
c_total = 0

# --- ADD 256 * 256 VERTICES
vlist = g.add_vertex(GRAPH_SIZE)

printStats(g)
# --- SET VERTEX PROPERTIES 
for i in range(0, GRAPH_SIZE):
    g_payload[g.vertex(i)] = Payload(population * (1 - immune_percentage), population * immune_percentage, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, .5, .05, .1, .05, .3)

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

printStats(g)
s = (256, 256)
p1 = np.zeros(s, dtype=np.float64)
p2 = np.zeros(s, dtype=np.float64)
p3 = np.zeros(s, dtype=np.float64)

for i in range(0, GRAPH_SIZE / 256):
    for j in range(0, GRAPH_SIZE / 256):
        payload = g_payload[g.vertex(i + j)]
        p1[i,j] = payload.susceptible + payload.immune
        p2[i,j] = payload.incubation1 + payload.incubation2 + payload.incubation3 + payload.incubation4
        p3[i,j] = payload.contagious1a + payload.contagious2a

import ColorMap
img1 = Image.fromarray(ColorMap.colorMap(p1))
# img1.save("/Users/paul.warren/Documents/ebola/images/mapped.png")
img1.show()






