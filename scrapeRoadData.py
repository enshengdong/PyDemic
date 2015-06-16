from __future__ import print_function

from osgeo import gdal, osr
import numpy
import math
from popdata import *

"""
Comment
"""

if __name__ == '__main__':
    roaddata = gdal.Open('roads.tif')
    rows = roaddata.RasterYSize
    cols = roaddata.RasterXSize
    geotrans = getGeoTransM(roaddata.GetGeoTransform()).I
    band = roaddata.GetRasterBand(1)
    nodedata = numpy.load('node.npy')
    data = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)

    for node in nodedata:
        (x, y) = getLocPixel(geotrans, node['lon'], node['lat'])
        if data.item((y, x)) > 0.5: # equal to one, but floating point bleh.
            node['isRoad'] = True

    numpy.save('node.npy', nodedata)
