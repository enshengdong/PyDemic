import model


# --- EVOLUTION FACTORS
immuneRate = .1	 # percentage of people immune: 
fatalityRate = .5 # chance of dying vs recovering (becoming immune): 
averageDistance = 1000 # kilometers per day an average person in Africa can travel: 

# --- START MODEL
m = model.Model("filename", immuneRate, fatalityRate, averageDistance)

for i in range(0, 100):
	m.turn()
