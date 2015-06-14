from __future__ import print_function
import numpy

nodes = numpy.load('node.npy')

maxpop = max(nodes['pop'])

for node in nodes:
    p_stay_city = 1.0/(2*node['dCity']+1)
    p_stay_hosp = 1.0/(2*node['dHosp']+1)
    p_stay_pop = (node['pop']/maxpop)**2
    p_stay_baseline = 0.001
    probGo = (1-p_stay_city)*(1-p_stay_pop)*(1-p_stay_baseline)*(1-p_stay_hosp)
    node['probStay'] = 1 - probGo
    fitness = [0.0]*4
    nids = [node['Nnid'], node['Snid'], node['Enid'], node['Wnid']]
    for i in range(4):
        if nids[i] == -1:
            continue
        pd = (nodes[nids[i]]['pop']/(1+node['pop']))**2
        if nodes[nids[i]]['isRoad']:
            fitness[i] = 5*pd
        else:
            fitness[i] = pd
    tot = sum(fitness)
    if tot < 0.001:
        node['probStay'] = 1.0
        node['Nprob'] = 0.0
        node['Sprob'] = 0.0
        node['Eprob'] = 0.0
        node['Wprob'] = 0.0
    else:
        fitness = [probGo*(f / tot) for f in fitness]
        node['Nprob'] = fitness[0]
        node['Sprob'] = fitness[1]
        node['Eprob'] = fitness[2]
        node['Wprob'] = fitness[3]

numpy.save('node_weighted.npy', nodes)

with open('node_weighted.dat', 'w') as nodefile:
    print(len(nodes), file=nodefile)
    for n in nodes:
        print(':'.join([str(e) for e in n][:-3]), file=nodefile)


