import numpy as np
import time
import os
from Utility import timeSTR


class Model(object):
    """
    The Model classes represents our overall network-based model. It takes in a filename of all data necessary to initialize each node
    (sans immuneRate, which is passed into the model during creation). It also takes in evolutionary factors immuneRate (the percentage
    of the population immune to the disease), fatalityRate (how likely it is a sick person will die or recover), averageDistance
    (distance a contagious traveler could be expected to cover in our given time step), and transmissionRate (percentage of people a
    contagious person will infect out of the total people they'll come in contact with).
    """
    __slots__ = ('data','mapping','immuneRate','fatalityRate','maxDistance','transmissionRate')

    def __init__(self,fname,immuneRate,fatalityRate,maxDistance,transmissionRate):
        """
        Initializes model with given information.
        """
        self.mapping = {'nid': 0,'latitude': 1,'longititude': 2,'population': 3,
                        'probNorth': 4,'northNid': 5,'probEast': 6,'eastNid': 7,
                        'probSouth': 8,'southNid': 9,'probWest': 10,'westNid': 11,
                        'probStay': 12,'immune': 13,'susceptible': 14,'incubation1': 15,
                        'incubation2': 16,'contagious': 17,'dead': 18}
        fileData = np.loadtxt(fname,dtype=float,comments='#',delimiter=':',skiprows=1,unpack=True)
        calcData = np.zeros((6,fileData.shape[1]),dtype=float)
        calcData[0,:] = np.random.poisson(fileData[3,:] * immuneRate,(fileData.shape[1]))
        calcData[1,:] = np.around(fileData[3,:] - calcData[0,:])
        self.data = np.vstack((fileData,calcData))
        self.immuneRate = immuneRate
        self.fatalityRate = fatalityRate
        self.maxDistance = maxDistance
        self.transmissionRate = transmissionRate

    def __getattr__(self,attr):
        """
        Emulates named slots but actually gets the corresponding numpy column
        """
        if attr in self.mapping:
            idx = self.mapping[attr]
            return self.data[idx,:]
        else:
            return __dict__[attr]

    def __getitem__(self,key):
        if isinstance(key,tuple):
            return self.data[key]
        else:
            return self.data[:,key]

    def turn(self):
        """
        Subroutine that simulates one timestep in our model.
        """
        self.stateChange()
        self.travel()

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
        # No need to infect, travel infects the destination
        # Add dying or surviving as it makes sense to change with the rest of the game state
        dead = np.clip(np.random.poisson(self.fatalityRate * self.data[17,:]),0,self.data[17,:])
        self.data[18,:] += dead
        self.data[13,:] += self.data[17,:] - dead
        self.data[17,:] = 0
        # incubation2 to contagious and reset incubation
        self.data[17,:] += self.data[16,:]
        self.data[16,:] = 0
        # Aproximately half of incubation1 go to incubation2 rest go to contagiousB
        incu2 = np.clip(np.random.poisson(0.5 * self.data[15,:]),0,self.data[15,:])
        self.data[16,:] += incu2
        self.data[17,:] += self.data[15,:] - incu2
        self.data[15,:] = 0

    def infect(self,contagious):
        """
        Calculates the newly infected people for all nodes at the given step in the day
        :param contagious:
        :return:
        """
        # Transmission rate is infections per person per travel step
        # Clip makes sure you cant infect more people than there are susceptible
        # print("Contagious shape {}".format(contagious.shape))
        contLoc = contagious.nonzero()[0]
        subCont = contagious[contLoc]
        # print("Contagious locations: {}".format(contLoc))
        # print("Contagious subsection: {}".format(subCont))
        infected = np.clip(np.random.poisson(subCont * self.transmissionRate),0,self.data[14,contLoc])
        self.data[15,contLoc] += infected
        self.data[14,contLoc] -= infected

    def travel(self):
        """
        Subroutine goes through every contagious person who can travel,
        decides if stay or travel up to the given distance (2050km),
        runs the subroutine node.infect() for every node the contagious
        person travels to, and uses the given fatality rate to whether
        the contagious person dies or recovers.
        """
        movable = np.zeros((2,self.data.shape[1]),dtype=float)
        movable[0,:] = np.copy(self.data[17,:])
        adjacency = np.clip(self.data[[5,7,9,11],:],0,np.inf).astype(np.uint32)
        # i switches the active column so they columns dont have
        # to be switched in memory which is expensive
        i = 0
        for step in range(0,self.maxDistance):
            movingIDX = movable[i,:].nonzero()[0]
            moving = np.copy(movable[i,movingIDX])
            north = np.clip(np.random.poisson(np.multiply(self.data[4,movingIDX],moving)),0,moving)
            moving -= north
            movable[1-i,adjacency[0,movingIDX]] += north
            east = np.clip(np.random.poisson(np.multiply(self.data[6,movingIDX],moving)),0,moving)
            moving -= east
            movable[1-i,adjacency[1,movingIDX]] += east
            south = np.clip(np.random.poisson(np.multiply(self.data[8,movingIDX],moving)),0,moving)
            moving -= south
            movable[1-i,adjacency[2,movingIDX]] += south
            west = np.clip(np.random.poisson(np.multiply(self.data[10,movingIDX],moving)),0,moving)
            moving -= west
            movable[1-i,adjacency[3,movingIDX]] += west
            stay = np.copy(moving)
            movable[1-i,movingIDX] += stay
            i = 1 - i
            movable[1-i,:] = 0
            self.infect(movable[i,:])
        self.data[17,:] = movable[i,:]

    def dump(self,runName,frame):
        if not os.path.exists("data/dumps"):
            os.mkdir("data/dumps")
        out = self.data[[13,14,15,16,17,18],:].astype(np.uint16)
        np.savetxt('data/dumps/graph.{0}.{1}.dmp'.format(runName,frame),out.T,fmt='%i',delimiter=':')


if __name__ == '__main__':
    a = Model("data/node.dat",0.2,0,0,0)
