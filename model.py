import numpy as np
import time
import os
from Utility import timeSTR

class Model():
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
        fileData = np.loadtxt(fname,dtype=float,comments='#',delimiter=':',skiprows=1)
        calcData = np.zeros((fileData.shape[0],6),dtype=float)
        calcData[:,0] = np.random.poisson(fileData[:,3] * immuneRate,fileData.shape[0])
        calcData[:,1] = np.around(fileData[:,3] - calcData[:,0])
        self.data = np.hstack((fileData,calcData))
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
            return self.data[:,idx]
        else:
            return __dict__[attr]

    def __getitem__(self,key):
        if isinstance(key,tuple):
            return self.data[key]
        else:
            return self.data[key,:]

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
        dead = np.clip(np.random.poisson(self.fatalityRate * self.data[:,17]),0,self.data[:,17])
        self.data[:,18] += dead
        self.data[:,13] += self.data[:,17] - dead
        self.data[:,17] = 0
        # incubation2 to contagious and reset incubation
        self.data[:,17] += self.data[:,16]
        self.data[:,16] = 0
        # Aproximately half of incubation1 go to incubation2 rest go to contagiousB
        incu2 = np.clip(np.random.poisson(0.5 * self.data[:,15]),0,self.data[:,15])
        #print("Average Incu2 {}".format(0.5 * self.data[7:13,15]))
        #print("# TO Incu2 {}".format(incu2[7:13]))
        self.data[:,16] += incu2
        self.data[:,17] += self.data[:,15] - incu2
        self.data[:,15] = 0

    def infect(self,contagious):
        """
        Calculates the newly infected people for all nodes at the given step in the day
        :param contagious:
        :return:
        """
        # Transmission rate is infections per person per travel step
        # Clip makes sure you cant infect more people than there are susceptible
        infected = np.clip(np.random.poisson(contagious * self.transmissionRate),0,self.data[:,14])
        self.data[:,15] += infected
        self.data[:,14] -= infected

    def travel(self):
        """
        Subroutine goes through every contagious person who can travel,
        decides if stay or travel up to the given distance (2050km),
        runs the subroutine node.infect() for every node the contagious
        person travels to, and uses the given fatality rate to whether
        the contagious person dies or recovers.
        """
        moving = np.zeros((self.data.shape[0],2),dtype=float)
        # Move contagious people to travel matrix
        moving[:,0] = self.data[:,17]
        # Adjacency is a matrix of the nids n,e,s,w
        # Clip prevents -1 indices from going to 4294967295 and causing an error
        adjacency = np.clip(self.data[:,[5,7,9,11]],0,self.data.shape[1]).astype(np.uint32)
        for step in range(0,self.maxDistance):
            stay = np.clip(np.random.poisson(self.data[:,12] * moving[:,0]),0,moving[:,0])
            moving[:,1] += stay
            moving[:,0] -= stay
            north = np.clip(np.random.poisson(self.data[:,4] * moving[:,0]),0,moving[:,0])
            moving[adjacency[:,0].tolist(),1] += north
            moving[:,0] -= north
            east = np.clip(np.random.poisson(self.data[:,6] * moving[:,0]),0,moving[:,0])
            moving[adjacency[:,1].tolist(),1] += east
            moving[:,0] -= east
            south = np.clip(np.random.poisson(self.data[:,8] * moving[:,0]),0,moving[:,0])
            moving[adjacency[:,2].tolist(),1] += south
            moving[:,0] -= south
            west = moving[:,0]  # Everybody else goes west
            moving[adjacency[:,3].tolist(),1] += west
            moving[:,0] -= west
            # INFECT AND RESET TEMP ARRAY
            self.infect(moving[:,1])
            # Roll effectively switches the two columns
            moving = np.roll(moving,1,1)
        self.data[:,17] = moving[:,0]

    def dump(self,runName,frame):
        if not os.path.exists("data/dumps"):
            os.mkdir("data/dumps")
        out = self.data[:,[13,14,15,16,17,18]].astype(np.uint16)
        np.savetxt('data/dumps/graph.{0}.{1}.dmp'.format(runName, frame),out[:5000,:],fmt='%i',delimiter=':')

if __name__ == '__main__':
    a = Model("data/node.dat",0.2,0,0,0)
    print(a.nid)
    print(a[0])
    print(a[0:3].nid)
