import sys
import numpy as np
from popdata import *
import time
import glob
from threading import Thread

"""
Comment
"""

def dataToArray(data, roi, attr, emptyval):
    (xcoords, ycoords) = getCoords(roi)
    arr = numpy.full((len(ycoords), len(xcoords)), emptyval, dtype=numpy.float32)
    geotrans = createGeoTrans(roi)
    geotrans_m = getGeoTransM(geotrans).I

    for node in data:
        (x, y) = getLocPixel(geotrans_m, node[1], node[0])
        if (x < arr.shape[1]) and (y < arr.shape[0]):
            arr[y, x] = node[attr]
    return (arr, geotrans)

class Exporter(Thread):
    __slots__ = ('fname','band','field','empty','data')

class Converter(Thread):
    __slots__ = ('data','params','totals','empty','verbose')

    def __init__(self,data,verbose=False):
        super(Converter,self).__init__()
        self.fname = data
        self.params = {'immune':2, 'sus':3, 'inc':4, 'cont':6, 'dead':8}
        self.totals = {'immune':0, 'sus':0, 'inc':0, 'cont':0, 'dead':0}
        self.empty = -1000.0
        self.verbose = verbose

    def run(self):
        self.data[:,4] = np.sum(self.data[:,4:6],axis=1)
        self.data[:,6] = np.sum(self.data[:,6:8],axis=1)
        for field in self.params:
            start = time.time()
            (raster, trans) = dataToArray(self.data, roi, self.params[field], self.empty)
            exportGeoTIFFRaster(self.fname[:-4] + '.' + field + '.tif', raster, trans, self.empty)
            if self.verbose:
                print("{0} band {1} finished in {2} seconds".format(self.fname.split("\\")[1],field,(time.time() - start)))

def convert(files):
    threads = [None] * len(files)
    start = time.time()
    print("Reading data in")
    dataArrays = []
    for fname in files:
        dataArrays.append(np.loadtxt(fname,delimiter=':'))
    print("Spawning {0} threads".format(len(files)))
    for i in range(0,len(files)):
        threads[i] = Converter(dataArrays[i],True)
        threads[i].start()
    for thread in threads:
        thread.join()
    print("Conversion Complete")

if __name__ == '__main__':
    #files = sys.argv[1:]
    files = ["graphLong.6.dmp"]
    files = glob.glob("data/dumps/*.dmp")
    print(str(files))
    convert(files)
