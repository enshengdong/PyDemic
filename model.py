import numpy as np
import time
import node
import os

class Model():
    """ 
    The Model classes represents our overall network-based model. It takes in a filename of all data necessary to initialize each node
    (sans immunityRate, which is passed into the model during creation). It also takes in evolutionary factors immunityRate (the percentage 
    of the population immune to the disease), fatalityRate (how likely it is a sick person will die or recover), maxDistance 
    (distance a contagious traveler could be expected to cover in our given time step), and transmissionRate (percentage of people a 
    contagious person will infect out of the total people they'll come in contact with).
    """
    def __init__(self, filename, immunityRate, fatalityRate, maxDistance, transmissionRate):
        """
        Initializes model with given information.
        """
        self.filename = filename
        self.immunityRate = immunityRate
        self.fatalityRate = fatalityRate
        self.maxDistance = maxDistance

        self.nodes = self._readFile()  # np.array of _Node objects

    def _readFile(self):
        """
        Helper subroutine that reads the given filename and initializes all the nodes.
        """
        with open(self.filename, "r") as f:
            numNodes = int(f.next().strip())
            nodes = np.empty(numNodes, dtype=np.object)
            count = 0
            start = time.time()
            for line in f:
                inputs = [float(f) for f in line[:-1].split(':')]
                inputs.append(self.immunityRate)
                nodes[count] = node.Node(*(inputs))
                count += 1
            print("{0} nodes loaded into a model in {1:.2f} seconds.".format(count, time.time() - start))
            
        return nodes[:count] # TO-DO: REMOVE

    def startEpidemic(self):
        self.nodes[10].incubation1 += 30
        for i in range(0,5):
            self.nodes[np.random.randint(0,len(self.nodes))].incubation1 += 5

    def turn(self):
        """
        Subroutine that simulates one timestep in our model.
        """
        self.changeStates()
        self.travel()
        self.resetContagious()

    def changeStates(self):
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
        for nodeID in range(0, len(self.nodes)):
            node = self.nodes[nodeID]
            node.contagiousB += node.incubation2
            node.incubation2 = 0
            numInc1 = node.incubation1
            for incubation1Person in range(0, numInc1):
                if np.random.uniform() <= .5:
                    node.incubation2 += 1
                else:
                    node.contagiousB += 1
                node.incubation1 -= 1
            for contagiousPerson in range(0, node.contagiousA + node.contagiousB):
                node.infect()

    def travel(self):
        """
        Subroutine goes through every contagious person who can travel, 
        decides if stay or travel up to the given distance,
        runs the subroutine node.infect() for every node the contagious
        person travels to, and uses the given fatality rate to whether
        the contagious person dies or recovers.
        """
        for nodeID in range(0, len(self.nodes)):
            for contagousPerson in range(0, self.nodes[nodeID].contagiousA):
                curNode = self.nodes[nodeID]
                for step in range(0, self.maxDistance):
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
                self.nodes[nodeID].contagiousA -= 1

    def resetContagious(self):
        for nodeID in range(0, len(self.nodes)):
            node = self.nodes[nodeID]
            node.contagiousA += node.contagiousB
            node.contagiousB = 0

    def dump(self, frame):
        """
        Subroutine that prints out the data in the graph in a format convenient for our parser.
        """
        dead = 0
        if not os.path.exists("data/dumps"):
            os.mkdir("data/dumps")

        with open("data/dumps/graphLong.{}.dmp".format(frame), "w") as out:
            for node in self.nodes:
                if node is not None:
                    dead += node.dead
                    out.write(str(node)+"\n")
        print "{} Dead".format(dead)



