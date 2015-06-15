import model
import time

# --- EVOLUTION FACTORS
immunityRate = .1  # percentage of people immune
fatalityRate = .6  # chance of dying vs recovering (becoming immune)
maxDistance = 1000  # kilometers per day an average person in Africa can travel:
transmissionRate = .5  # chance you'll infect a given person you come in contact with

# --- START MODEL
print "Creating model..."
m = model.Model("data/nodes.dat", immunityRate, fatalityRate, maxDistance, transmissionRate)
print "Starting turns..."

for i in range(0, 2):
    start = time.time()
    m.turn()
    if i % 1 == 0:
        m.dump(i)
    print "Finished turn {0} in {1:.2f} seconds.".format(i, time.time() - start)
