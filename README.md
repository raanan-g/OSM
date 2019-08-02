# OSM
Tools for working locally with OpenStreetMap (OSM) data

You can download OSM data by geographic from [Geofabrik](geofabrik.de) or using [Overpass Turbo API](https://overpass-turbo.eu/)

Python and batch (command line) scripts in this repository were written by Raanan Gurewitsch

## Dependencies:

The file 'osm_batch.bat' requires [osmconvert](https://wiki.openstreetmap.org/wiki/Osmconvert#Download) to convert .PBF files to .OSM and [osmfilter](https://wiki.openstreetmap.org/wiki/Osmfilter#Download) to filter out specific tags or areas from larger files.

Python libraries for working with OSM and spatial data:

[shapely](https://shapely.readthedocs.io/en/latest/)

[geopandas](http://geopandas.org/install.html)

geojson

[osmnx](https://osmnx.readthedocs.io/en/stable/)

[ogr](https://gdal.org/python/)

## Pipeline:
Step 1 -> geofabrik.py -> download regional OpenStreetMap data for US
Step 2 -> osm_batch.bat -> convert files and extract relevant data by tag
Step 3 -> osmtojson.py -> convert files to json format for analysis
Step 4 -> osm_feature_collection.py -> collect address-level OSM statistics

![Part 1:](osmpl1.png)

![Part 1:](osmpl2.png)
