from graph_tool.all import *
from PIL import Image
import heatmap
import numpy as np
import time
import payload

# --- PRINT GRAPH STATISTICS (number of nodes, number of edges)
def printStats(g):
    print "nodes %d, edges %d " % (len(list(g.vertices())), len(list(g.edges())))

class Constructor():
    def __init__(self, numVertices):
        
        # --- INITIALIZE (direct) GRAPH with node payloads
        g = Graph()
        g_payload = g.new_vertex_property("object") 
        self.vlist = g.add_vertex(numVertices)

    def addNodeInfo(self, filename):


    def addEdges(self, filename):



# --- CONSTANTS
population = 100
immune_percentage = .15
GRAPH_SIZE = 256 * 256


printStats(g)
# --- SET VERTEX PROPERTIES 
for i in range(0, GRAPH_SIZE):
    g_payload[g.vertex(i)] = Payload(population * (1 - immune_percentage), population * immune_percentage, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, .5, .05, .1, .05, .3)

printStats(g)
# --- CONNECT ALL NODES (directed graph)


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






