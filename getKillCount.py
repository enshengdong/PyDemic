from __future__ import print_function

from osgeo import gdal, osr
import numpy
import math
import sys

geoTIFF = gdal.Open(sys.argv[1])
rows = geoTIFF.RasterYSize
cols = geoTIFF.RasterXSize
band = geoTIFF.GetRasterBand(1)
emptyval = band.GetNoDataValue()
data = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
accumulate = 0L
for row in data:
    for x in row:
        if x == emptyval:
            continue
        accumulate = accumulate + long(x)
print("{}: {}".format(sys.argv[1], accumulate))

