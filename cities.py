import numpy
from popdata import *
from collections import deque

arr = numpy.load('node.npy')
pts = None
with open('cities.dat', 'r') as f:
    pts = [[float(d) for d in line.split(':')] for line in f]
q = deque()
for node in arr:
    for p in pts:
        if abs(p[0] - node['lat']) < (km_in_deg/2) and abs(p[1] - node['lon']) < (km_in_deg/2):
            q.append((node['nid'], 0))
while q:
    (nid, dist) = q.popleft()
    if arr[nid]['dCity'] > dist:
        arr[nid]['dCity'] = dist
        for nbor in [arr[nid][x] for x in ['Nnid', 'Snid', 'Enid', 'Wnid']]:
            q.append((nbor, dist + 1))
numpy.save('node.npy', arr)
emptyval = -1000.0
exportGeoTIFF('city_heat.tif', arr, roi, 'dCity', emptyval)
