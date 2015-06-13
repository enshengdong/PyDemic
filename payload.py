class Payload():
    def __init__(self, s, im, i1, i2, i3, i4, c1a, c1b, c2a, c2b, r, d, pN, pE, pS, pW, pStay):
        self.susceptible  = s
        self.immune       = im
        self.incubation1  = i1
        self.incubation2  = i2
        self.incubation3  = i3
        self.incubation4  = i4
        self.contagious1a = c1a
        self.contagious1b = c1b
        self.contagious2a = c2a
        self.contagious2b = c2b
        self.recovered    = r
        self.dead         = d
        self.probNorth    = pN
        self.probEast     = pE
        self.probSouth    = pS
        self.probWest     = pW
        self.probStay     = pStay