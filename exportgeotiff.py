import numpy
from popdata import *

arr = numpy.load('node.npy')
exportGeoTIFF('pop_out.tif', arr, roi, float(numpy.finfo(numpy.float32).min))

