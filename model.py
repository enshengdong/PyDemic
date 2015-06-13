import numpy as np
import time

# --- PRINT GRAPH STATISTICS (number of nodes, number of edges)
def printStats(g):
    print "nodes %d, edges %d " % (len(list(g.vertices())), len(list(g.edges())))

class Node():
    def __init__(self, nid, latitude, longitude, population, probNorth, northNID, probEast, eastNID, probSouth, southNID, probWest, westNID, probStay, immuneRate):
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

        self.immune = self.population * immuneRate
        self.susceptible = self.population - self.immune
        self.incubation1 = 0
        self.incubation2 = 0
        self.incubation3 = 0
        self.incubation4 = 0
        self.contagious1a = 0
        self.contagious1b = 0
        self.contagious2a = 0
        self.contagious2b = 0
        self.dead = 0

    def infect(self):
        """
        subroutine of nodes run when an infected passes through
        updates the number of infected and susceptible
        """
        y = 10 #people interacted with * transmission probability
        I = np.random.poisson(y)
        if I <= self.s:
            self.s -= I
            self.i1 += I
        else:
            self.i1 += self.s
            self.s = 0


class Model():
    def __init__(self, filename, immuneRate, fatalityRate, averageDistance):
        self.filename = filename
        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate 
        self.averageDistance = averageDistance

        self.nodes = self._readFile() # np.array of _Node objects

    def _readFile(self):
        with open(self.filename, "r") as f:
            numNodes = int(f.next().strip())
            nodes = np.empty(numNodes,dtype=np.object)
            count = 0
            start = time.time()
            for line in f:
                inputs = [float(f) for f in line[:-1].split(':')]
                inputs.append(self.immuneRate)
                nodes[count] = Node(*(inputs))
                count += 1
            print("Graph creation time: "+str(time.time()-start))
            print("Created %d nodes" % (count))
        return nodes

    def turn(self):
        # does a turn
        print "does a turn"

    def travel(self):
        """
        Models a person traveling
        At each step they choose a uniform random
        That chooses to either stay or move in direction
        The current node is the tile they are at
        The temp node is their start node
        """
        for i in range(0,self.nodes.shape[0]):
            temp = self.nodes[i]
            for j in range(0,currNode.contagious1a):
                currNode = temp
                for step in range(0,self.maxDistance):
                    direction = np.random.uniform()
                    if direction < currNode.probStay:
                        pass
                    elif (direction-currNode.probStay) < currNode.probNorth:
                        currNode = self.nodes[currNode.northNID]
                    elif (direction-currNode.probStay-currNode.probNorth) \
                        < currNode.probEast:
                        currNode = self.nodes[currNode.eastNID]
                    elif (direction-currNode.probStay-currNode.probNorth
                        -currNode.probEast) < currNode.probSouth:
                        currNode = self.nodes[currNode.southNID]
                    else:
                        currNode = self.nodes[currNode.westNID]
                    currNode.infect()
                currNode.contagious1b += 1
                temp.contagious1a -= 1



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






