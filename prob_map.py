import numpy
from popdata import *

arr = numpy.load('node_weighted.npy')
emptyval = -1000.0
exportGeoTIFF('stay_map.tif', arr, roi, 'probStay', emptyval)
