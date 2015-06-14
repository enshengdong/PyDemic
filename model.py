import numpy as np
import time

class Node():
    def __init__(self,nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,westNID,probStay,immuneRate):
        self.nid = int(nid)
        self.latitude = latitude
        self.longitude = longitude
        self.probNorth = probNorth
        self.northNID = int(northNID)
        self.probEast = probEast
        self.eastNID = int(eastNID)
        self.probSouth = probSouth
        self.southNID = int(southNID)
        self.probWest = probWest
        self.westNID = int(westNID)
        self.probStay = probStay

        self.immune = int(round(population * immuneRate))
        self.susceptible = int(round(population - self.immune))
        self.incubation1 = 0
        self.incubation2 = 0
        self.contagiousA = 0
        self.contagiousB = 0  
        self.dead = 0

    def infect(self):
        """
        subroutine of nodes run when an infected passes through
        updates the number of infected and susceptible
        """
        y = 10  # people interacted with * transmission probability
        I = np.random.poisson(y)
        if I <= self.susceptible:
            self.susceptible -= I
            self.incubation1 += I
        else:
            self.incubation1 += self.susceptible
            self.susceptible = 0

    def getLatLong(self):
        return [self.longitude,self.latitude,1.0]

    def getIncubating(self):
        return self.incubation1 + self.incubation2

    def getContagious(self):
        return self.contagiousA + self.contagiousB

    def __str__(self):
        out = ""
        out += str(self.latitude) + ":"
        out += str(self.longitude) + ":"
        out += str(self.immune) + ":"
        out += str(self.susceptible) + ":"
        out += str(self.incubation1) + ":"
        out += str(self.incubation2) + ":"
        out += str(self.contagiousA) + ":"
        out += str(self.contagiousB) + ":"
        out += str(self.dead)
        return out


class Model():
    def __init__(self,filename,immuneRate,fatalityRate,averageDistance,transmissionRate):
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
            nodes[10].incubation1 += 20
            for i in range(0,5):
                nodes[np.random.randint(0,numNodes)].incubation1 += 5
        return nodes

    def turn(self):
        self.stateChange()
        self.travel()
        self.resetContagious()


    def resetContagious(self):
        for i in range(0,self.nodes.shape[0] - 1):
            node = self.nodes[i]
            node.contagiousA += node.contagiousB
            node.contagiousB = 0

    def stateChange(self):
        for i in range(0,self.nodes.shape[0] - 1):
            node = self.nodes[i]
            # print("node.contagiousB = " + str(node.contagiousB))
            node.contagiousB += node.incubation2
            node.incubation2 = 0
            numInc1 = node.incubation1
            for i in range(0, numInc1):
                if np.random.uniform() <= .5:
                    node.incubation2 += 1
                else:
                    node.contagiousB += 1
                node.incubation1 -= 1
            for i in range(0, node.contagiousA + node.contagiousB):
                node.infect()

    def travel(self):
        """
        Models a person traveling
        At each step they choose a uniform random
        That chooses to either stay or move in direction
        The current node is the tile they are at
        The temp node is their start node
        """
        for i in range(0,self.nodes.shape[0] - 1):
            startNode = self.nodes[i]
            for j in range(0,startNode.contagiousA):
                curNode = startNode
                for step in range(0,1000):
                    direction = np.random.uniform()
                    if direction < curNode.probStay:
                        pass
                    elif (direction - curNode.probStay) < curNode.probNorth:
                        curNode = self.nodes[curNode.northNID]
                    elif (direction - curNode.probStay - curNode.probNorth) < curNode.probEast:
                        curNode = self.nodes[curNode.eastNID]
                    elif (direction - curNode.probStay - curNode.probNorth
                              - curNode.probEast) < curNode.probSouth:
                        curNode = self.nodes[curNode.southNID]
                    else:
                        curNode = self.nodes[curNode.westNID]
                    curNode.infect()
                if np.random.uniform() <= self.fatalityRate:
                    curNode.dead += 1
                else:
                    curNode.immune += 1
                startNode.contagiousA -= 1

    def dump(self,frame):
        with open("graph0.%d.dmp" % (frame),"w") as out:
            for node in self.nodes:
                if node is not None:
                    out.write(str(node)+"\n")



