import numpy as np

# --- PRINT GRAPH STATISTICS (number of nodes, number of edges)
def printStats(g):
    print "nodes %d, edges %d " % (len(list(g.vertices())), len(list(g.edges())))

class Node():
    def __init__(self, nid, latitude, longitude, population, probNorth, northNID, probEast, eastNID, probSouth, southNID, probWest, westNID, probStay):
        self.nid        = int(nid)
        self.latitude   = latitude   
        self.longitude  = longitude    
        self.population = population     
        self.probNorth  = probNorth    
        self.northNID   = int(northNID)
        self.probEast   = probEast   
        self.eastNID    = int(eastNID)
        self.probSouth  = probSouth    
        self.southNID   = int(southNID)   
        self.probWest   = probWest   
        self.westNID    = int(westNID)
        self.probStay   = probStay

        self.immune = node.population * self.immuneRate
        self.susceptible = node.population - node.immune
        self.incubation1 = 0
        self.incubation2 = 0
        self.incubation3 = 0
        self.incubation4 = 0
        self.contagious1a = 0
        self.contagious1b = 0
        self.contagious2a = 0
        self.contagious2b = 0
        self.dead = 0


class Model():
    def __init__(self, filename, immuneRate, fatalityRate, averageDistance):
        self.filename = filename
        self.nodes = self._readFile() # np.array of _Node objects

        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate 
        self.averageDistance = averageDistance

        self._initializeNodes()

    def _readFile(self):
        with open(filename, "r") as f:
            numNodes = int(f.readLine())
            nodes = numpy.array([Node() * self.numNodes])
            for count, line in enumerate(f.readlines()):
                nodes[count] = Node(*([float(f) for f in line.split(':')].append(self.immuneRate)))
        return nodes

    def turn():
        # does a turn
        print "does a turn"



# from PIL import Image
# import heatmap

# printStats(g)
# s = (256, 256)
# p1 = np.zeros(s, dtype=np.float64)
# p2 = np.zeros(s, dtype=np.float64)
# p3 = np.zeros(s, dtype=np.float64)

# for i in range(0, GRAPH_SIZE / 256):
#     for j in range(0, GRAPH_SIZE / 256):
#         payload = g_payload[g.vertex(i + j)]
#         p1[i,j] = payload.susceptible + payload.immune
#         p2[i,j] = payload.incubation1 + payload.incubation2 + payload.incubation3 + payload.incubation4
#         p3[i,j] = payload.contagious1a + payload.contagious2a

# import ColorMap
# img1 = Image.fromarray(ColorMap.colorMap(p1))
# # img1.save("/Users/paul.warren/Documents/ebola/images/mapped.png")
# img1.show()






