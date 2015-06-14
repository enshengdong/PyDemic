import numpy as np
import time
from popdata import *
import cv2

# --- PRINT GRAPH STATISTICS (number of nodes, number of edges)
def printStats(g):
    print "nodes %d, edges %d " % (len(list(g.vertices())),len(list(g.edges())))


class Node():
    def __init__(self,nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,
                 westNID,probStay,immuneRate):
        self.nid = int(nid)
        self.latitude = latitude
        self.longitude = longitude
        #self.population = int(population)
        self.probNorth = probNorth
        self.northNID = int(northNID)
        self.probEast = probEast
        self.eastNID = int(eastNID)
        self.probSouth = probSouth
        self.southNID = int(southNID)
        self.probWest = probWest
        self.westNID = int(westNID)
        self.probStay = probStay

        self.immune = population * immuneRate
        self.susceptible = population - self.immune
        self.incubation1 = 0
        self.incubation2 = 0
        self.incubation3 = 0
        self.incubation4 = 0
        self.contagious1a = 0
        self.contagious1b = 0
        self.contagious2a = 0
        self.dead = np.random.random_integers(0,255)

    def infect(self):
        """
        subroutine of nodes run when an infected passes through
        updates the number of infected and susceptible
        """
        y = 10  # people interacted with * transmission probability
        I = np.random.poisson(y)
        if I <= self.s:
            self.s -= I
            self.i1 += I
        else:
            self.i1 += self.s
            self.s = 0

    def getLatLong(self):
        return [self.longitude,self.latitude,1.0]

    def getIncubating(self):
        return self.incubation1 + self.incubation2 + self.incubation3 + self.incubation4

    def getContagious(self):
        return self.contagious1a + self.contagious2a


class Model():
    def __init__(self,filename,immuneRate,fatalityRate,averageDistance):
        self.filename = filename
        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate
        self.averageDistance = averageDistance

        self.nodes = self._readFile()  # np.array of _Node objects

    def _readFile(self):
        with open(self.filename,"r") as f:
            numNodes = int(f.next().strip())
            nodes = np.empty(numNodes,dtype=np.object)
            count = 0
            start = time.time()
            for line in f:
                inputs = [float(f) for f in line[:-1].split(':')]
                inputs.append(self.immuneRate)
                nodes[count] = Node(*(inputs))
                count += 1
                # if count > 1000000:
                #    break
            print("Graph creation time: " + str(time.time() - start))
            print("Created %d nodes" % (count))
        print "file closed"
        return nodes

    def turn(self):
        print "Traveling..."
        self.travel()
        for node in self.nodes:
            node.contagious1a = node.contagious1b
            node.contagious1b = 0

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
                    elif (direction - currNode.probStay) < currNode.probNorth:
                        currNode = self.nodes[currNode.northNID]
                    elif (direction - currNode.probStay - currNode.probNorth) \
                            < currNode.probEast:
                        currNode = self.nodes[currNode.eastNID]
                    elif (direction - currNode.probStay - currNode.probNorth
                              - currNode.probEast) < currNode.probSouth:
                        currNode = self.nodes[currNode.southNID]
                    else:
                        currNode = self.nodes[currNode.westNID]
                    currNode.infect()
                currNode.contagious1b += 1
                temp.contagious1a -= 1

    def viz(self):
        y = (roi[0][1] - roi[0][0]) / roi[0][2]
        x = (roi[1][1] - roi[1][0]) / roi[1][2]
        out = np.zeros((int(y) + 1,int(x) + 1,6),np.float32)
        mat = getGeoTransM(createGeoTrans(roi))
        latLongs = []
        for i in range(0,1000000):
            latLongs.append(self.nodes[i].getLatLong())
        pixels = np.floor(np.clip(np.dot(mat.I,np.array(latLongs).T),0,np.inf)).T.astype(np.uint16)
        print np.amax(pixels[:,0])
        print np.amax(pixels[:,1])
        print np.amin(pixels[:,0])
        print np.amin(pixels[:,1])
        print out.shape
        for i in range(0,pixels.shape[0]):
            out[pixels[i,0] - 2,pixels[i,1] - 2,0] = self.nodes[i].population
            out[pixels[i,0] - 2,pixels[i,1] - 2,1] = self.nodes[i].immune
            out[pixels[i,0] - 2,pixels[i,1] - 2,2] = self.nodes[i].susceptible
            out[pixels[i,0] - 2,pixels[i,1] - 2,3] = self.nodes[i].getIncubating()
            out[pixels[i,0] - 2,pixels[i,1] - 2,4] = self.nodes[i].getContagious()
            out[pixels[i,0] - 2,pixels[i,1] - 2,5] = self.nodes[i].dead
        out /= np.amax(out)
        cv2.namedWindow("Layer",cv2.WINDOW_NORMAL)
        for b in range(0,out.shape[2]):
            cv2.imshow("Layer",out[:,:,b])
            cv2.waitKey(0)
        cv2.destroyAllWindows()
