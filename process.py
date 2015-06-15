import sys
import numpy
from popdata import *

def dataToArray(data, roi, attr, emptyval):
    (xcoords, ycoords) = getCoords(roi)
    arr = numpy.full((len(ycoords+1), len(xcoords+1)), emptyval, dtype=numpy.float32)
    print arr.shape
    geotrans = createGeoTrans(roi)
    geotrans_m = getGeoTransM(geotrans).I
    for node in data:
        (x, y) = getLocPixel(geotrans_m, node[1], node[0])
        arr[y, x] = node[attr]
    return (arr, geotrans)

def convert(files):
    params = [('immune', 2), ('sus', 3), ('inc', 4), ('cont', 6), ('dead', 8)]
    empty = -1000.0
    for fname in files:
        with open(fname, 'r') as fin:
            data = [[float(x) for x in line.split(':')] for line in fin.readlines()]
            for node in data:
                node[4] = node[4] + node[5]
                node[6] = node[6] + node[7]
            for field in params:
                (raster, trans) = dataToArray(data, roi, field[1], empty)
                exportGeoTIFFRaster(fname + '.' + field[0] + '.tif', raster, trans, empty)

if __name__ == '__main__':
    files = sys.argv[1:]
    convert(files)