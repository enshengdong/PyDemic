CXX=clang++
CXXFLAGS=-lgdal -I/usr/include/gdal -std=c++1y -Wall -O2

all: createTiff

createTiff: createTiff.cpp
	${CXX} createTiff.cpp -o createTiff ${CXXFLAGS}

clean:
	rm -f createTiff
