import model


# --- EVOLUTION FACTORS
immuneRate = .1	 # percentage of people immune: 
fatalityRate = .5 # chance of dying vs recovering (becoming immune): 
averageDistance = 1000 # kilometers per day an average person in Africa can travel: 
transmissionRate = .5 # chance you'll infect a person you interact with:

# --- START MODEL
print "Reading data..."
m = model.Model("data/node_train.dat", immuneRate, fatalityRate, averageDistance, transmissionRate)

for i in range(0, 1):
	print "Turn %d" % i
	m.turn()
