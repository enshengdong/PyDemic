import model
import time

# --- EVOLUTION FACTORS
immuneRate = .1	 # percentage of people immune: 
fatalityRate = .6 # chance of dying vs recovering (becoming immune): 
averageDistance = 1000 # kilometers per day an average person in Africa can travel: 
transmissionRate = .5 # chance you'll infect a given person

# --- START MODEL
print "Starting model..."
m = model.Model("data/node.dat", immuneRate, fatalityRate, averageDistance, transmissionRate)
print "Finished model. Starting turn..."
#m.viz()
for i in range(0,1000):
	m.turn()
	start = time.time()
	if i % 1 == 0:
		m.dump(i)
	print "Finished turn %d in %d seconds" % (i,time.time()-start)
