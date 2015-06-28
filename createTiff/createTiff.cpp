#include <vector>
#include <stdio.h>
#include <assert.h>
#include "gdal_priv.h"
#include "cpl_conv.h"
#include "cpl_string.h"
#include "ogr_api.h"
#include "ogr_spatialref.h"

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/vector.hpp>
#include <boost/numeric/ublas/lu.hpp>

using namespace boost::numeric;

/*********************************************/
/******          CONFIGURATION          ******/
/*********************************************/

// HIGH_ACCURACY
//
// Enable this to convert coordinates from global space
// to pixel space using an LU factorization instead of
// the matrix inverse.  This should in theory be more
// numerically stable, but these effects are not significant
// as we only need to be accurate to the nearest integer.
// 
// Enabling this option causes the runtime to increase by ~9x.
//#define HIGH_ACCURACY

/*********************************************/
/******        END CONFIGURATION        ******/
/*********************************************/



ublas::matrix<double> coordXformFromGDAL(double* gdal) {
    auto xformMatrix = ublas::matrix<double>(3, 3);
    xformMatrix(0, 0) = gdal[1];
    xformMatrix(0, 1) = gdal[2];
    xformMatrix(0, 2) = gdal[0];
    xformMatrix(1, 0) = gdal[4];
    xformMatrix(1, 1) = gdal[5];
    xformMatrix(1, 2) = gdal[3];
    xformMatrix(2, 0) = 0.0;
    xformMatrix(2, 1) = 0.0;
    xformMatrix(2, 2) = 1.0;
    return xformMatrix;
}    

double geoTransformVec[] = {
    -17.49, 0.00899676629221499, 0.0, 17.04896976241858, 0.0, -0.008992995644147054
};

int width = 3580;
int height = 1432;

float empty = -20.0;

static_assert(sizeof(float) == 4, "need 32 bit float");

int main() {

    bool vebose = false; //set to true to warn on dropping pixels

    GDALAllRegister();
    GDALDriver* driver = GetGDALDriverManager()->GetDriverByName("GTiff");
    assert(driver);
    const char* ofile = "/dev/stdout";
    GDALDataset* dataset = driver->Create(ofile, width, height, 1, GDT_Float32, nullptr);
    dataset->SetGeoTransform(geoTransformVec);
    float* raster = new float[width*height];
    for (int i = 0; i < width*height; ++i) {
        raster[i] = empty;
    }
    OGRSpatialReference oSRS;
    oSRS.importFromEPSG(4326);
    char* datum;
    oSRS.exportToWkt(&datum);
    dataset->SetProjection(datum);
    GDALRasterBand* band = dataset->GetRasterBand(1);
    double lat, lon, data;
    auto xformMatrix = coordXformFromGDAL(geoTransformVec);
    decltype(xformMatrix) xformMatrixI = ublas::identity_matrix<double>(xformMatrix.size1());
    auto permute = ublas::permutation_matrix<>(xformMatrix.size1());
    ublas::lu_factorize(xformMatrix, permute);
#ifndef HIGH_ACCURACY
    ublas::lu_substitute(xformMatrix, permute, xformMatrixI);
    //we manually do the matrix multiply as it isn't that hard and we don't
    //use 1/3 of the computation (the homogeneous coordinate which we already
    //know is 1).  Doing this manually cuts overall execution time by about
    //25%, so the added obscurity is worth it.
    double gtm[] = {xformMatrixI(0, 0), xformMatrixI(0, 1), xformMatrixI(0, 2),
                    xformMatrixI(1, 0), xformMatrixI(1, 1), xformMatrixI(1, 2)};
#else
    auto pos = ublas::vector<double>(3);
#endif
    while (scanf("%lf %lf %lf", &lat, &lon, &data) != EOF) {
#ifndef HIGH_ACCURACY
        auto x = int(gtm[0]*lon + gtm[1]*lat + gtm[2]);
        auto y = int(gtm[3]*lon + gtm[4]*lat + gtm[5]);
#else
        pos[0] = lon;
        pos[1] = lat;
        pos[2] = 1.0;
        ublas::lu_substitute(xformMatrix, permute, pos);
        auto x = (int)pos[0];
        auto y = (int)pos[1];
#endif
        if (x < 0 || x >= width || y < 0 || y >= height) {
            if (verbose) {
                fprintf(stderr, "warning: Point at lat/long %lf %lf out of ROI (coords %d, %d)\n",
                    lat, lon, x, y);
            }
        }
        else {
            raster[y*width+x] = data;
        }
    }
    band->RasterIO(GF_Write, 0, 0, width, height, (GByte*)raster, width, height, GDT_Float32, 0, 0);
    GDALClose((GDALDatasetH)dataset);
    delete[] raster;
    return 0;
}
