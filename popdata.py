from __future__ import print_function

from osgeo import gdal
import numpy
import math

popdata = gdal.Open('africa2010ppp.tif')

roi_west = -17.490
roi_east = 14.722
roi_south = 4.171
roi_north = 17.057

km_in_deg = 1/111.12

# the geoTrans matrix appears to be a homogeneous coordinate transformation:
# [ lon ]   [ gT[1] gt[2] gt[0] ][ x ]
# [ lat ] = [ gT[4] gt[5] gt[3] ][ y ]
# [  1  ] = [  0     0     1    ][ 1 ]

# it should be fairly well conditioned so even though taking the inverse is not
# necessarily ideal it's close enough.

def getGeoTransM(geoTrans):
    return numpy.matrix([
        [geoTrans[1], geoTrans[2], geoTrans[0]],
        [geoTrans[4], geoTrans[5], geoTrans[3]],
        [          0,           0,           1]
    ])


def getPixelLoc(geoTransM, x, y):
    loc = geoTransM*numpy.matrix([[x],[y],[1]])
    return (loc.item(0), loc.item(1))

def getLocPixel(geoTransMI, lon, lat):
    px = [int(round(i.item(0))) for i in geoTransMI*numpy.matrix([[lon],[lat],[1]])]
    return (px[0], px[1])

##
## Process the popdata file
##

rows = popdata.RasterYSize
cols = popdata.RasterXSize
geo_trans = popdata.GetGeoTransform()
geo_trans_m = getGeoTransM(geo_trans)
geo_trans_mi = geo_trans_m.I

#print('Image is {}x{} px'.format(cols, rows))
#print('Corners:')
#ext = [getPixelLoc(geo_trans_m, x, y) for x in [0, cols] for y in [0, rows]]
#for corner in ext:
#    print('\t{}'.format(corner))
#print('Computed size is: {}'.format(getLocPixel(geo_trans_mi, *(ext[3]))))

#for now, nodes will be (xi, yi) -> (nid, x, y, popdens)

def recFromFunction(fn, shape, dtype):
    arr = numpy.zeros(shape, dtype=dtype)
    for i in range(shape[0]):
        for j in range(shape[1]):
            arr[i, j] = fn((i, j))
    return arr

# {lon,lat}data is a tuple (min, max, stride)
def getClippedROIData(roi, geoTIFF, bandNum):
    londata = roi[0]
    latdata = roi[1]
    geotrans_int = geoTIFF.GetGeoTransform()
    geotrans = getGeoTransM(geotrans_int).I
    rows = geoTIFF.RasterYSize
    cols = geoTIFF.RasterXSize
    band = geoTIFF.GetRasterBand(bandNum)
    emptyval = band.GetNoDataValue()
    data = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
    xcoords = numpy.arange(*londata)
    ycoords = numpy.arange(*latdata)[::-1]
    outdataType = numpy.dtype([
        ('value', numpy.float32),
        ('lat', numpy.float32),
        ('lon', numpy.float32)
    ])
    outarr = numpy.zeros((len(ycoords), len(xcoords)), dtype=outdataType)
    if geotrans_int[2] == 0 and geotrans_int[4] == 0:
        # no rotation, so we can cheat
        pxcoords = [getLocPixel(geotrans, xc, 0)[0] for xc in xcoords]
        pycoords = [getLocPixel(geotrans, 0, yc)[1] for yc in ycoords]
        for i in range(len(ycoords)):
            for j in range(len(xcoords)):
                lat = ycoords.item(i)
                lon = xcoords.item(j)
                pxloc = (pxcoords[j], pycoords[i])
                val = data.item((pxloc[1], pxloc[0]))
                if val == emptyval:
                    val = numpy.nan
                outarr[i, j] = numpy.array([(val, lat, lon)], dtype=outdataType)
    else:
        for i in range(len(ycoords)):
            for j in range(len(xcoords)):
                lat = ycoords.item(i)
                lon = xcoords.item(j)
                pxloc = getPixelLoc(geotrans, lon, lat)
                val = data.item((pxloc[1], pxloc[0]))
                if val == emptyval:
                    val = numpy.nan
                outarr[i, j] = numpy.array([(val, lat, lon)], dtype=outdataType)
    return outarr

nodes = dict()
adjlist = []
nid = 0
roi = ((roi_west, roi_east, km_in_deg),
        (roi_south, roi_north, km_in_deg))
data = getClippedROIData(roi, popdata, 1)

del popdata # free memory

(ylen, xlen) = data.shape
for yi in range(ylen):
    for xi in range(xlen):
        (lat, lon, val) = data.item((yi, xi))
        if not math.isnan(val):
            if xi != 0:
                nbor = nodes.get((xi-1, yi))
                if nbor is not None:
                    adjlist.append((nid, nbor[0]))
            if yi != 0:
                nbor = nodes.get((xi, yi-1))
                if nbor is not None:
                    adjlist.append((nid, nbor[0]))
            nodes[(xi, yi)] = (nid, lon, lat, val)
            nid = nid + 1



with open('edges', 'w') as edgefile:
    for edge in adjlist:
        print('{}:{}'.format(*edge), file=edgefile)

with open('nodes', 'w') as nodefile:
    for n in nodes.viewvalues():
        print('{}:{}:{}:{}'.format(*n), file=nodefile)


#numbands = popdata.RasterCount
#print('File has {} data bands'.format(numbands))
## NB: bands are indexed from *1*
#for num in range(numbands):
#    band = popdata.GetRasterBand(num+1)
#    nodata = band.GetNoDataValue()

