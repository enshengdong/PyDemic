import numpy as np
import time
import h5py


class Model(np.ndarray):
    def __new__(subtype,shape,dtype=float,buffer=None,offset=0,strides=None,order=None,info=None):
        """
        Create the ndarray instance of our type, given the usual
        ndarray input arguments.  This will call the standard
        ndarray constructor, but return an object of our type.
        It also triggers a call to InfoArray.__array_finalize__
        """
        obj = np.ndarray.__new__(subtype,shape,dtype,buffer,offset,strides,order)
        obj.info = info
        return obj

    def __init__(self):
        pass

class Node_OLD():
    """ 
    Helper Node class. Represents a 1km x 1km tile. Takes in Node ID, latitude, longitude, population, the probability of contagious people 
    going North when traveling, the ID of the node to the North, the probability of contagious people going East when traveling, the ID of 
    the node to the East, the probability of contagious people going South when traveling, the ID of the node to the South, the probability 
    of contagious people going West when traveling, the ID of the node to the North, the probability of contagious people staying instead of
    traveling, and the percentage of the overall population who are immune to the disease. 

    Has nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,westNID,probStay,immuneRate,immune,
    susceptible,incubation1,incubation2,contagiousA,contagiousB, and dead fields. Immune, susceptible, ... fields all represent the total number
    of people in that 1km x 1km region who are in that stage of the disease. ContagiousB is used to store contagious people who have all traveled
    before; when calculating the number of contagious people in a given node, you should sum contagiousA and contagious B.
    """
    def __init__(self,nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,westNID,probStay,immuneRate):
        """
        Initializes node with given information.
        """
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
        Subroutine that nodes run when a contagious person passes through to determine how many people that contagious person infects.
        Automatically updates information.
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
        """
        Subroutine that returns latitude and longitude in a convenient format for our parser.
        """
        return [self.longitude,self.latitude,1.0]

    def getIncubating(self):
        """
        Subroutine that returns the number of people in the incubutation stage of the disease in a convenient format for our parser.
        """
        return self.incubation1 + self.incubation2

    def getContagious(self):
        """
        Subroutine that returns the number of people in the contagious stage of the disease in a convenient format for our parser.
        """
        return self.contagiousA + self.contagiousB

    def __str__(self):
        """
        to_string subroutine that combines all of the interesting data (latitude, longitude, immune, susceptible, incubation1, 
        incubation2, contagiousA, contagiousB, dead) in each node in a convenient format for our parser.
        """
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


class Model_OLD():
    """ 
    The Model classes represents our overall network-based model. It takes in a filename of all data necessary to initialize each node
    (sans immuneRate, which is passed into the model during creation). It also takes in evolutionary factors immuneRate (the percentage 
    of the population immune to the disease), fatalityRate (how likely it is a sick person will die or recover), averageDistance 
    (distance a contagious traveler could be expected to cover in our given time step), and transmissionRate (percentage of people a 
    contagious person will infect out of the total people they'll come in contact with).
    """
    def __init__(self,filename,immuneRate,fatalityRate,averageDistance,transmissionRate):
        """
        Initializes model with given information.
        """
        self.filename = filename
        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate
        self.averageDistance = averageDistance

        self.nodes = self._readFile()  # np.array of _Node objects

    def _readFile(self):
        """
        Helper subroutine that reads the given filename and initializes all the nodes.
        """
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
            nodes[10].incubation1 += 30
            for i in range(0,5):
                nodes[np.random.randint(0,numNodes)].incubation1 += 5
        return nodes

    def turn(self):
        """
        Subroutine that simulates one timestep in our model.
        """
        self.stateChange()
        self.travel()
        self.resetContagious()


    def resetContagious(self):
        for i in range(0,self.nodes.shape[0] - 1):
            node = self.nodes[i]
            node.contagiousA += node.contagiousB
            node.contagiousB = 0

    def stateChange(self):
        """
        Subroutine that determines, for every time step, moves everyone in incubation2 state
        into the contagious state, around half of the people in the incubation1 state into the
        incubation2 state, and the other half of the people in the incubation1 state into the 
        contagious state. It runs the node.infect() subroutine for every contagious person in 
        all nodes at the end of this state change.

        People moved to the contagious state are moved into contagiousB because people can only 
        have one state transition a turn. ContagiousB is the set of contagious people who have already
        moved or done a state transition and so can't move for the rest of the timestep.
        """
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
        Subroutine goes through every contagious person who can travel, 
        decides if stay or travel up to the given distance (2050km),
        runs the subroutine node.infect() for every node the contagious
        person travels to, and uses the given fatality rate to whether
        the contagious person dies or recovers.
        """
        for i in range(0,self.nodes.shape[0] - 1):
            for j in range(0,self.nodes[i].contagiousA):
                curNode = self.nodes[i]
                for step in range(0,2050):
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
                self.nodes[i].contagiousA -= 1

    def dump(self,frame):
        """
        Subroutine that prints out the data in the graph in a format convenient for our parser.
        """
        with open("graphLong.%d.dmp" % (frame),"w") as out:
            for node in self.nodes:
                if node is not None:
                    out.write(str(node)+"\n")



