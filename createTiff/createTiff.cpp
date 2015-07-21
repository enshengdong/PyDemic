#include <vector>
#include <iostream>
#include <stdio.h>
#include <assert.h>
#include <boost/program_options.hpp>
#include <algorithm>
#include "geotiff.h"

/* Tokenizer Function */
//adapted from http://stackoverflow.com/a/1493195
#include <iterator>
template <class Container>
void tokenize(const std::string& str, std::back_insert_iterator<Container> it,
              const std::string& delimiters = " ", bool trimEmpty = false)
{
    std::string::size_type pos, lastPos = 0;
    using value_type = typename Container::value_type;
    using size_type  = typename Container::size_type;
 
    while (true) {
        pos = str.find_first_of(delimiters, lastPos);
        if (pos == std::string::npos) {
            pos = str.length();
  
            if (pos != lastPos || !trimEmpty) {
                it = value_type(str.data()+lastPos, (size_type)pos-lastPos);
            }
            break;
        }
        else {
            if (pos != lastPos || !trimEmpty) {
                it = value_type(str.data()+lastPos, (size_type)pos-lastPos);
            }
        }
        lastPos = pos + 1;
    }
}

float empty = -20.0;

static_assert(sizeof(float) == 4, "need 32 bit float");

namespace po = boost::program_options;
int main(int argc, char** argv) {
    po::options_description opts("Allowed options");
    opts.add_options()
        ("help,h", "help message")
        ("roi-from-file,f", po::value<std::string>(),
                "set GeoTIFF ROI to match [file]")
        ("roi,r", po::value<std::string>(),
                "set ROI, format tl_lat:tl_lon:br_lat:br_lon:px_res_meters")
        ("out,o", po::value<std::string>(), "Output File (default stdout)")
    ;
    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, opts), vm);
    if (vm.count("help")) {
        std::cout << opts << '\n';
        return 0;
    }
    po::notify(vm);
    std::unique_ptr<ROI> roi;
    if (vm.count("roi-from-file")) {
        roi.reset(new ROI(vm["roi-from-file"].as<std::string>().c_str()));
    }
    else if (vm.count("roi")) {
        std::vector<std::string> toks;
        tokenize(vm["roi"].as<std::string>(), std::back_inserter(toks), ":");
        std::vector<double> roivec;
        std::transform(toks.begin(), toks.end(), std::back_inserter(roivec),
                [](const std::string& a) {return std::stod(a);});
        if (roivec.size() != 5) {
            std::cerr << "Error parsing ROI\n";
            return 1;
        }
        roi.reset(new ROI({roivec[0], roivec[1]}, {roivec[2], roivec[3]},
                    size_t(roivec[4])));
    }
    else {
        std::cerr << "Must specify ROI\n";
        return 1;
    }
    std::string ofile = "/dev/stdout";
    if (vm.count("out")) {
        ofile = vm["out"].as<std::string>();
    }
    geotiff output(ofile.c_str(), empty, *roi);
    auto& b = output.getband(0);
    b.fill_empty();
    double lat, lon, data;
    int x, y;
    while (scanf("%lf %lf %lf", &lat, &lon, &data) != EOF) {
        std::tie(y, x) = output.fromGCS(lat, lon);
        b.at(y, x) = data;
    }
    b.flush();
    return 0;
}
