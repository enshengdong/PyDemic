from __future__ import print_function

from osgeo import gdal, osr
import numpy
import math

# Define ROI
roi_west = -17.490
roi_east = 14.722
roi_south = 4.171
roi_north = 17.057
km_in_deg = 1/111.12
roi = ((roi_west, roi_east, km_in_deg),
        (roi_south, roi_north, km_in_deg))

# Load a WKT projection for the WGS84 datum
wgs84 = osr.SpatialReference()
wgs84.ImportFromEPSG(4326)
wgs84 = wgs84.ExportToWkt()

# Get a list of the coordinate locations along each axis of the ROI
def getCoords(roi):
    xcoords = numpy.arange(*(roi[0]))
    ycoords = numpy.arange(*(roi[1]))[::-1]
    return (xcoords, ycoords)


# the geoTrans matrix appears to be a homogeneous coordinate transformation:
# [ lon ]   [ gT[1] gt[2] gt[0] ][ x ]
# [ lat ] = [ gT[4] gt[5] gt[3] ][ y ]
# [  1  ] = [  0     0     1    ][ 1 ]
#
# this transforms from pixel coordinate space to latitude space
# it should be fairly well conditioned so even though taking the inverse is not
# necessarily ideal it's close enough.

# Create GDAL GeoTrans list from ROI
def createGeoTrans(roi):
    (xcoords, ycoords) = getCoords(roi)
    xr = xcoords.item(-1) - xcoords.item(0)
    yr = ycoords.item(-1) - ycoords.item(0)
    width = xr / len(xcoords)
    height = yr / len(ycoords)
    # for now hard code rotation to zero
    rotX = 0
    rotY = 0
    return (xcoords.item(0), width, rotX, ycoords.item(0), rotY, height)

# Convert GDAL GeoTrans list to a numpy matrix in homogeneous coordinates
def getGeoTransM(geoTrans):
    return numpy.matrix([
        [geoTrans[1], geoTrans[2], geoTrans[0]],
        [geoTrans[4], geoTrans[5], geoTrans[3]],
        [          0,           0,           1]
    ])

# Get Location From Pixel (call with matrix)
def getPixelLoc(geoTransM, x, y):
    loc = geoTransM*numpy.matrix([[x],[y],[1]])
    return (loc.item(0), loc.item(1))

# Get Pixel from Location (call with matrix inverse)
def getLocPixel(geoTransMI, lon, lat):
    px = [int(i.item(0)) for i in geoTransMI*numpy.matrix([[lon],[lat],[1]])]
    return (px[0], px[1])

def recFromFunction(fn, shape, dtype):
    arr = numpy.zeros(shape, dtype=dtype)
    for i in range(shape[0]):
        for j in range(shape[1]):
            arr[i, j] = fn((i, j))
    return arr

# Take a base geoTIFF and clip it to a certain ROI
# We use this for the base layer, and then draw other
# layers over top of it.
def getClippedROIData(roi, geoTIFF, bandNum):
    geotrans_int = geoTIFF.GetGeoTransform()
    geotrans = getGeoTransM(geotrans_int).I
    rows = geoTIFF.RasterYSize
    cols = geoTIFF.RasterXSize
    band = geoTIFF.GetRasterBand(bandNum)
    emptyval = band.GetNoDataValue()
    data = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
    (xcoords, ycoords) = getCoords(roi)
    outdataType = numpy.dtype([
        ('value', numpy.float32),
        ('lat', numpy.float32),
        ('lon', numpy.float32)
    ])
    outarr = numpy.zeros((len(ycoords), len(xcoords)), dtype=outdataType)
    if geotrans_int[2] == 0 and geotrans_int[4] == 0:
        # no rotation, so we can cheat
        pxcoords = [getPixelLoc(geotrans, xc, 0)[0] for xc in xcoords]
        pycoords = [getPixelLoc(geotrans, 0, yc)[1] for yc in ycoords]
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

# Get nid data for export (array attribute) from the node dump data
# Array must be a numpy array supporting 'lat' and 'lon' accessors
def nidDataToArray(nid_data, roi, attr, emptyval):
    (xcoords, ycoords) = getCoords(roi)
    arr = numpy.full((len(ycoords), len(xcoords)), emptyval, dtype=numpy.float32)
    geotrans = createGeoTrans(roi)
    geotrans_m = getGeoTransM(geotrans)
    for node in nid_data:
        (x, y) = getLocPixel(geotrans_m.I, node['lon'], node['lat'])
        arr[y, x] = float(node[attr])
    return (arr, geotrans)

# Get nid data for export (using a callback) from the node dump data
def nidDataToArrayCB(nid_data, roi, callback, emptyval):
    (xcoords, ycoords) = getCoords(roi)
    arr = numpy.full((len(ycoords), len(xcoords)), emptyval, dtype=numpy.float32)
    geotrans = createGeoTrans(roi)
    geotrans_m = getGeoTransM(geotrans)
    for node in nid_data:
        (x, y) = getLocPixel(geotrans_m.I, node['lon'], node['lat'])
        arr[y, x] = callback(node)
    return (arr, geotrans)

# Export a geoTIFF with the most common settings
def exportGeoTIFF(fname, nid_data, roi, attr, emptyval):
    (arr, geotrans) = nidDataToArray(nid_data, roi, attr, emptyval)
    exportGeoTIFFRaster(fname, arr, geotrans, emptyval)

# Export raster data from one of the nidDataToArray* funcitons
def exportGeoTIFFRaster(fname, raster, geotrans, emptyval):
    cols = raster.shape[1]
    rows = raster.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    # file name, xsize, ysize, numbands, datatype
    outRaster = driver.Create(fname, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform(geotrans)
    outband = outRaster.GetRasterBand(1)
    outband.SetNoDataValue(emptyval)
    outband.WriteArray(raster)
    outRaster.SetProjection(wgs84)
    outband.FlushCache()

##
## Process the popdata file
##
def main():
    # strip all things below a certain threshold
    strip_threshold = -1

    popdata = gdal.Open('data/africa2010ppp.tif')
    rows = popdata.RasterYSize
    cols = popdata.RasterXSize
    
    # Get transformation matrices
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
    nodes = dict()
    vert_edges = []
    horiz_edges = []
    nid = 0
    data = getClippedROIData(roi, popdata, 1)

    del popdata # free memory

    # walk the data and create the nodes and lists of edges
    (ylen, xlen) = data.shape
    for yi in range(ylen):
        for xi in range(xlen):
            (val, lat, lon) = data.item((yi, xi))
            if not math.isnan(val) and val > strip_threshold:
                if xi != 0:
                    nbor = nodes.get((xi-1, yi))
                    if nbor is not None:
                        horiz_edges.append((nid, nbor[0]))
                if yi != 0:
                    nbor = nodes.get((xi, yi-1))
                    if nbor is not None:
                        vert_edges.append((nid, nbor[0]))
                nodes[(xi, yi)] = (nid, lon, lat, val)
                nid = nid + 1

    # create adjacency list graph structure
    # nodes' values are nid, lon, lat, pop
    # output format is nid, lat, lon, pop, pN, n, pE, e, pS, s, pW, w, pStay

    nodeType = numpy.dtype([
        ('nid', numpy.int32),
        ('lat', numpy.float32),
        ('lon', numpy.float32),
        ('pop', numpy.float32),
        ('Nprob', numpy.float32),
        ('Nnid', numpy.int32),
        ('Eprob', numpy.float32),
        ('Enid', numpy.int32),
        ('Sprob', numpy.float32),
        ('Snid', numpy.int32),
        ('Wprob', numpy.float32),
        ('Wnid', numpy.int32),
        ('probStay', numpy.float32),
        ('isRoad', numpy.bool_),
        ('dHosp', numpy.int32),
        ('dCity', numpy.int32)])
    nodeArr = numpy.zeros(len(nodes), dtype=nodeType)
    for n in nodes.viewvalues():
        (nid, lon, lat, pop) = n
        nodeArr[nid] = numpy.array([(nid, lat, lon, pop, 1.0, -1, 0.0, -1, 0.0, -1, 0.0, -1, 0.0, False, 99999999999, 99999999999)], dtype=nodeType)
    for edge in horiz_edges:
        (eastnid, westnid) = edge
        nodeArr[westnid]['Enid'] = eastnid
        nodeArr[eastnid]['Wnid'] = westnid
    for edge in vert_edges:
        (southnid, northnid) = edge
        nodeArr[southnid]['Nnid'] = northnid
        nodeArr[northnid]['Snid'] = southnid
    del nodes
    del horiz_edges
    del vert_edges
    
    # generate easy to read node listing
    with open('node.dat', 'w') as nodefile:
        print(len(nodeArr), file=nodefile)
        for n in nodeArr:
            print(':'.join([str(e) for e in n][:-3]), file=nodefile)
    numpy.save('node.npy', nodeArr)

if __name__ == '__main__':
    main()
