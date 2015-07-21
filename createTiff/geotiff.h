#ifndef GEOTIFF_H_INC
#define GEOTIFF_H_INC

#include <vector>
#include <memory>
#include <array>
#include <stdexcept>
#include <string>
#include <cstdint>

#include <assert.h>
#include "gdal_priv.h"
#include "cpl_conv.h"
#include "cpl_string.h"
#include "ogr_api.h"
#include "ogr_spatialref.h"

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/vector.hpp>
#include <boost/numeric/ublas/lu.hpp>

#include "row_buffer.h"

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

typedef std::array<double, 6> affineXform;

//Points are {lat, lon} or {y, x} throughout.
template <class T>
using point = std::pair<T, T>;

ublas::matrix<double> coordXformFromGDAL(affineXform gdal) {
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

struct ROI {
    double lat_top;
    double lon_left;
    affineXform gtm;
    size_t width;
    size_t height;


    //standard ctor - form ROI from GCS of top left/bottom right and
    //desired resolution, res, in meters.
    ROI(point<double> top_left, point<double> bot_right, size_t res) {
        std::tie(lat_top, lon_left) = top_left;
        //TODO: this is only strictly accurate for the equator
        double deg_in_m = 110754.2727;
        double step = res/deg_in_m;
        gtm = {lon_left, step, 0, lat_top, 0, step};
        width = ceil((bot_right.second - top_left.second)/step);
        height = ceil((top_left.first - bot_right.first)/step);
    }
    //Get ROI that matches a given geotiff
    explicit ROI(const char* fname);
};

class geotiff {
public:
    class band;
private:
    GDALDataset* dataset;
    std::vector<band> bands;   
    double emptyval;
    size_t width;
    size_t height;
    affineXform gtm;
#ifndef HIGH_ACCURACY
    affineXform gtmi;
#else
    ublas::matrix<double> xformMatrix;
    auto permute = ublas::permutation_matrix<>(3);
    auto pos = ublas::vector<double>(3);
#endif
public:
    using iterator = decltype(bands)::iterator;
    iterator begin() {
        return bands.begin();
    }
    iterator end() {
        return bands.end();
    }
    band& getband(size_t i) {
        return bands[i];
    }
    size_t numbands() {
        return bands.size();
    }
    struct geotiff_global {
        GDALDriver* driver;
        char* wgs84;
        GDALDataset* open(const char* fname, GDALAccess access) {
            return (GDALDataset*)GDALOpen(fname, access);
        }
        void close(GDALDataset* ds) {
            GDALClose((GDALDatasetH)ds);
        }
        geotiff_global() {
            //open GDAL GeoTIFF Driver
            GDALAllRegister();
            driver = GetGDALDriverManager()->GetDriverByName("GTiff");
            assert(driver);
            //set datum to WGS84
            OGRSpatialReference oSRS;
            oSRS.importFromEPSG(4326); //4326 is EPSG number for wgs84
            oSRS.exportToWkt(&wgs84);
        }
    };
    static geotiff_global& glob() {
        static geotiff_global global;
        return global;
    }
    class band {
        friend class geotiff;
    private:
        row_buffer<float> data;
        GDALRasterBand* band_ptr;
        float dummy;
        float empty;
        band(GDALDataset* dataset, int num, double nodata, size_t width, size_t height) :
            data(width, height)
        {
            band_ptr = dataset->GetRasterBand(num+1);
            band_ptr->SetNoDataValue(nodata);
            empty = nodata;
        }
    public:
        band(band&&) = default;
        void flush() {
            //push raster band buffer to the GeoTIFF
            band_ptr->RasterIO(GF_Write, 0, 0, data.width(), data.height(), 
                    (GByte*)(data.data()), data.width(), data.height(), GDT_Float32, 0, 0);
        }
        void fill_empty() {
            std::fill(data.all().begin(), data.all().end(), empty);
        }
        //UNSAFE
        float& operator()(int y, int x) {
            return data(y, x);
        }
        float& at(int y, int x) {
            if (x < 0 || (size_t)x > data.width() 
                    || y < 0 || (size_t)y > data.height())
            {
                return dummy;
#ifdef VERBOSE
                fprintf(stderr, "warning: Point at lat/long %lf %lf out of "
                        "ROI (coords %d, %d)\n", lat, lon, x, y);
#endif 
            }
            return data(y, x);
        }
    };
    geotiff(const char* name, double nodata, ROI roi, int numbands=1) {
#ifndef HIGH_ACCURACY
        ublas::matrix<double> xformMatrix;
        ublas::permutation_matrix<> permute(3);
#endif
        gtm = roi.gtm;
        width = roi.width;
        height = roi.height;
        emptyval = nodata;
        dataset = glob().driver->Create(name, roi.width,
                roi.height, numbands, GDT_Float32, nullptr);
        dataset->SetProjection(glob().wgs84);
        dataset->SetGeoTransform(gtm.data());
        //put geospatial transformation tuple into a more useful format
        xformMatrix = coordXformFromGDAL(gtm);
        ublas::lu_factorize(xformMatrix, permute);
#ifndef HIGH_ACCURACY
        //get the inverse from back substitution
        decltype(xformMatrix) xformMatrixI = ublas::identity_matrix<double>(xformMatrix.size1());
        ublas::lu_substitute(xformMatrix, permute, xformMatrixI);
        //we manually do the matrix multiply as it isn't that hard and we don't
        //use 1/3 of the computation (the homogeneous coordinate which we already
        //know is 1).  Doing this manually cuts overall execution time by about
        //25%, so the added obscurity is worth it.
        gtmi = {xformMatrixI(0, 0), xformMatrixI(0, 1), xformMatrixI(0, 2),
                xformMatrixI(1, 0), xformMatrixI(1, 1), xformMatrixI(1, 2)};
#endif
        for (int num = 0; num < numbands; ++num) {
            bands.push_back({dataset, num, emptyval, width, height});
        }
    }
    ~geotiff() {
        //close/write the file
        glob().close(dataset);
    }
    point<int> fromGCS(double lat, double lon) {
#ifndef HIGH_ACCURACY
        //do matrix multiply [x; y; 1] = Ainv*pos
        auto x = int(gtmi[0]*lon + gtmi[1]*lat + gtmi[2]);
        auto y = int(gtmi[3]*lon + gtmi[4]*lat + gtmi[5]);
#else
        //solve system of equations pos = A*[x; y; 1]
        pos[0] = lon;
        pos[1] = lat;
        pos[2] = 1.0;
        ublas::lu_substitute(xformMatrix, permute, pos);
        auto x = (int)pos[0];
        auto y = (int)pos[1];
#endif
        return {y, x};
    }
    point<double> toGCS(int y, int x) {
        auto lon = gtm[0] + x*gtm[1] + y*gtm[2];
        auto lat = gtm[3] + x*gtm[4] + y*gtm[5];
        return {lat, lon};
    }
};

ROI::ROI(const char* fname) {
    auto ds = geotiff::glob().open(fname, GA_ReadOnly);
    if (!ds) {
        throw std::runtime_error((std::string("Unable to open file ")
                   + fname).c_str());
    }
    ds->GetGeoTransform(gtm.data());
    lat_top = gtm[3];
    lon_left = gtm[0];
    width = ds->GetRasterXSize();
    height = ds->GetRasterYSize();
    GDALClose((GDALDatasetH)ds);
}

#endif
