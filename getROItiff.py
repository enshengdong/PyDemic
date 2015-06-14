import numpy
from popdata import *

#emptyval = float(numpy.finfo(numpy.float32).min)
emptyval = -1000.0

arr = numpy.load('node.npy')

(rasterbase, geo) = nidDataToArrayCB(arr, roi, lambda _: float(0.0), emptyval)
exportGeoTIFFRaster('base_roi.tif', rasterbase, geo, emptyval)

