__author__ = 'Dan.Simon'

import numpy as np
import sys

class Node():
    """
    s - succeptible
    im - immune
    i# - incubation [#,#,#,#]
    c#a - contagious stage and not moved
    c#b - contagious stage and moved
    r - recovered
    probability - [#,#,#,#]
    pStay - probability of not traveling
    edges - [Node,Node,Node,Node]
    """
    __slots__ = ('s','im','incubation','c1a','c1b','c2a',
                 'c2b','r','probability','pstay','edges')

    def __init__(self):
        self.s = 0
        self.im = 0
        self.incubation = [0,0,0,0]
        self.c1a = 0
        self.c2a = 0
        self.c1b = 0
        self.c2b = 0
        self.r = 0
        self.probability = [0.0,0.0,0.0,0.0]
        self.pstay = 1 - sum(self.probability)
        self.edges = [None] * 4

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

    def travel(self):
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

if __name__ == '__main__':
    nodes = []
    i = 0
    while True:
        try:
            nodes.append(Node())
            i += 1
            sys.stdout.write("Created %d nodes\r" % (i))
        except:
            print("Created %d nodes" % (i))