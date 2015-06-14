all: node.npy base_roi.tif pop_out.tif roads.tif

node.npy: popdata.py data/africa2010ppp.tif
	python popdata.py
	python scrapeRoadData.py
	python cities.py

base_roi.tif: getROItiff.py node.npy
	python getROItiff.py

pop_out.tif: get_pop_tiff.py node.npy
	python get_pop_tiff.py

roads.tif: base_roi.tif data/roads.shp
	cp base_roi.tif roads.tif
	gdal_rasterize -b 1 -burn 1 -at -l roads data/roads.shp roads.tif

