import model
import time
import numpy as np
from Utility import timeSTR,beep

# --- EVOLUTION FACTORS
immuneRate = 0.1  # percentage of people immune
fatalityRate = 0.6  # chance of dying vs recovering (becoming immune)
maxDistance = 2050  # kilometers per day an average person in Africa can travel:
transmissionRate = 1  # People infected by one person in per stop

# --- START MODEL
print("Starting model...")
start = time.time()
m = model.Model("data/node.dat", immuneRate, fatalityRate, maxDistance, transmissionRate)
m.data[10,16] += 20
m.data[11,16] += 20
print("Finished loading model in {0}. Starting turns...".format(timeSTR(time.time() - start)))
for i in range(0, 1):
    start = time.time()
    m.turn()
    if i % 1 == 0:
        pass
        #m.dump('test',i)
    print("Finished turn {0} in {1}".format(i,timeSTR(time.time() - start)))
    print("{0} traveling contagious and {1} dead".format(np.sum(m.data[:,17]), np.sum(m.data[:,18])))
beep()