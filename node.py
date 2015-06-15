import numpy as np

class Node():
    """ 
    Helper Node class. Represents a 1km x 1km tile. Takes in Node ID, latitude, longitude, population, the probability of contagious people 
    going North when traveling, the ID of the node to the North, the probability of contagious people going East when traveling, the ID of 
    the node to the East, the probability of contagious people going South when traveling, the ID of the node to the South, the probability 
    of contagious people going West when traveling, the ID of the node to the North, the probability of contagious people staying instead of
    traveling, and the percentage of the overall population who are immune to the disease. 

    Has nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,westNID,probStay,immunityRate,immune,
    susceptible,incubation1,incubation2,contagiousA,contagiousB, and dead fields. Immune, susceptible, ... fields all represent the total number
    of people in that 1km x 1km region who are in that stage of the disease. ContagiousB is used to store contagious people who have all traveled
    before; when calculating the number of contagious people in a given node, you should sum contagiousA and contagious B.
    """
    def __init__(self,nid,latitude,longitude,population,probNorth,northNID,probEast,eastNID,probSouth,southNID,probWest,westNID,probStay,immunityRate):
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

        self.immune = np.random.poisson(int(population*immunityRate))
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
        y = 2 # people interacted with * transmission probability
        I = np.random.poisson(y)
        if I <= self.susceptible:
            self.susceptible -= I
            self.incubation1 += I
        else:
            self.incubation1 += self.susceptible
            self.susceptible = 0

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

