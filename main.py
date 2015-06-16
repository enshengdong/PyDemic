import model
import time

"""
Comment
"""

# --- EVOLUTION FACTORS
immunityRate = .1  # percentage of people immune
fatalityRate = .6  # chance of dying vs recovering (becoming immune)
maxDistance = 2050  # kilometers per day an average person in Africa can travel:
transmissionRate = .5  # chance you'll infect a given person you come in contact with

# --- CREATE MODEL
print("Creating model...")
name = "ebola2015"
dataFile = "data/nodes.dat"
m = model.Model(name, dataFile, immunityRate, fatalityRate, maxDistance, transmissionRate)

# --- START MODEL
m.startEpidemic()
print("Starting turns...")
runName = "RUN"
for i in range(0, 2):
    start = time.time()
    m.turn()
    if i % 1 == 0:
        m.dump(runName, i)
    print("Finished turn {0} in {1:.2f} seconds.".format(i, time.time() - start))
