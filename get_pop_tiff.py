import numpy
from popdata import *

#emptyval = float(numpy.finfo(numpy.float32).min)
emptyval = -1000.0

arr = numpy.load('node.npy')
exportGeoTIFF('pop_out.tif', arr, roi, 'pop', emptyval)

