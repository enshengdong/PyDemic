import numpy as np
import time
from random import randint

class Node():
    def __init__(self, nid, latitude, longitude, population, probNorth, northNID, probEast, eastNID, probSouth, southNID, probWest, westNID, probStay, immuneRate):
        self.nid        = int(nid)
        self.latitude   = latitude   
        self.longitude  = longitude    
        self.population = population * 10
        self.probNorth  = probNorth    
        self.northNID   = int(northNID)
        self.probEast   = probEast   
        self.eastNID    = int(eastNID)
        self.probSouth  = probSouth    
        self.southNID   = int(southNID)   
        self.probWest   = probWest   
        self.westNID    = int(westNID)
        self.probStay   = probStay

        self.immune = np.floor(self.population * immuneRate)
        self.susceptible = np.round(self.population - self.immune)
        print(self.susceptible)
        self.incubation1 = 0
        self.incubation2 = 0
        self.incubation3 = 0
        self.incubation4 = 0
        self.contagious1a = 0
        self.contagious1b = 0
        self.contagious2a = 0
        self.contagious2b = 0
        self.dead = 0

    def infect(self, transmissionRate):
        """
        subroutine of nodes run when an infected passes through
        updates the number of infected and susceptible
        """
        # numInfected = (self.susceptible * .001) * transmissionRate
        y = 4
        I = np.random.poisson(y)
        I = 1
        if I <= self.susceptible:
            self.susceptible -= I
            self.incubation1 += I
        else:
            self.incubation1 += self.susceptible
            self.susceptible = 0
        print ("numSuscp = " + str(self.susceptible) + " and numInfected = " + str(y))

        # if numInfected <= self.susceptible:
        #     self.susceptible -= numInfected
        #     self.incubation1 += numInfected
        # else:
        #     self.incubation1 += self.susceptible
        #     self.susceptible = 0


class Model():
    def __init__(self, filename, immuneRate, fatalityRate, averageDistance, transmissionRate):
        self.filename = filename
        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate 
        self.averageDistance = averageDistance
        self.transmissionRate = transmissionRate

        self.nodes = self._readFile() # np.array of _Node objects

    def _readFile(self):
        with open(self.filename, "r") as f:
            start = time.time()
            numNodes = int(f.next().strip())
            nodes = np.empty(numNodes,dtype=np.object)
            count = 0
            for line in f:
                inputs = [float(f) for f in line.strip('\n').split(':')]
                inputs.append(self.immuneRate)
                nodes[count] = Node(*(inputs))
                count += 1
            print("Graph Creation Time: " + str(time.time() - start))
            print("Created %d nodes" % (count))
        return nodes

    def turn(self):
        self.travel()
        print randint(0,self.nodes.shape[0])


    def travel(self):
        """
        Models a person traveling
        At each step they choose a uniform random
        That chooses to either stay or move in direction
        The current node is the tile they are at
        The temp node is their start node
        """
        print(self.nodes.shape[0])
        for nodeID in range(0 , self.nodes.shape[0]):
            print "Node %d" % nodeID
            startNode = self.nodes[nodeID]
            for contagiousPerson in range(0, startNode.contagious1a):
                print ("Contagious person " + str(contagiousPerson) + " in node " + str(nodeID))
                curNode = startNode
                for step in range(0, self.averageDistance):
                    direction = np.random.uniform()
                    if direction < curNode.probStay:
                        print "Decided to stay."
                        pass
                    elif (direction - curNode.probStay) < curNode.probNorth:
                        curNode = self.nodes[curNode.northNID]
                        print "Decided to move North."
                    elif (direction - curNode.probStay - curNode.probNorth) < curNode.probEast:
                        curNode = self.nodes[curNode.eastNID]
                        print "Decided to moved East."
                    elif (direction - curNode.probStay - curNode.probNorth - curNode.probEast) < curNode.probSouth:
                        curNode = self.nodes[curNode.southNID]
                        print "Decided to move South."
                    else:
                        curNode = self.nodes[curNode.westNID]
                        print "Decided to move West."
                    curNode.infect(self.transmissionRate)
                curNode.contagious1b += 1
                startNode.contagious1a -= 1



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






