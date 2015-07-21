CXX=clang++
CXXFLAGS=-I/usr/include/gdal -std=c++1y -Wall -O2
LINKFLAGS=-lgdal -lboost_program_options
all: createTiff

createTiff: createTiff.cpp
	${CXX} createTiff.cpp -o createTiff ${CXXFLAGS} ${LINKFLAGS}

clean:
	rm -f createTiff
