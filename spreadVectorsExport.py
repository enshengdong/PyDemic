import numpy
from popdata import *
from collections import deque

arr = numpy.load('node.npy')
emptyval = -1000.0

def getSpreadVector(node):
    if node['isRoad']:
        return 0.0
    else:
        return node['dHosp'] + node['dCity']

(rasterbase, geo) = nidDataToArrayCB(arr, roi, getSpreadVector, emptyval)
exportGeoTIFFRaster('spread_vectors.tif', rasterbase, geo, emptyval)
