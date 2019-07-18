@ECHO OFF
:: This batch file converts OpenStreetMap data for each US region from pbf to o5m format
:: Each file is then filtered through and a separate .osm file is created with only the 
:: OSM tags needed for analysis.


:ProgressMeter
SETLOCAL ENABLEDELAYEDEXPANSION
SET ProgressPercent=%1
SET /A NumBars=%ProgressPercent%/2
SET /A NumSpaces=50-%NumBars%

SET Meter=

FOR /L %%A IN (%NumBars%,-1,1) DO SET Meter=!Meter!I
FOR /L %%A IN (%NumSpaces%,-1,1) DO SET Meter=!Meter!

TITLE OSM Convert & Filter || US Data || Progress:  [%Meter%]  %ProgressPercent%%%
ENDLOCAL
GOTO :EOF

ECHO ============= US - MIDWEST ===================
ECHO Converting file...
osmconvert us-midwest-latest.osm.pbf -o= us-midwest.o5m
ECHO Done!
ECHO Grabbing building tags...
osmfilter us-midwest.o5m --keep="building=residential =warehouse =industrial =house =retail =commercial" --drop-author --drop-version -o=Filtered/us-midwest-building.osm
ECHO Grabbing highway tags...
osmfilter us-midwest.o5m --keep="highway=residential =motorway =primary =secondary" --drop-author --drop-version -o=Filtered/us-midwest-highway.osm
ECHO Grabbing landuse tags...
osmfilter us-midwest.o5m --keep="landuse=residential =industrial =farmland =commercial" --drop-author --drop-version -o=Filtered/us-midwest-landuse.osm
:: next region
ECHO ============= US - PACIFIC ===================
ECHO Converting file...
osmconvert us-pacific-latest.osm.pbf -o= us-pacific.o5m
ECHO Done!
ECHO Grabbing building tags...
osmfilter us-pacific.o5m --keep="building=residential =warehouse =industrial =house =retail =commercial" --drop-author --drop-version -o=Filtered/us-pacific-building.osm
ECHO Grabbing highway tags...
osmfilter us-pacific.o5m --keep="highway=residential =motorway =primary =secondary" --drop-author --drop-version -o=Filtered/us-pacific-highway.osm
ECHO Grabbing landuse tags...
osmfilter us-pacific.o5m --keep="landuse=residential =industrial =farmland =commercial" --drop-author --drop-version -o=Filtered/us-pacific-landuse.osm
:: next region
ECHO =============  US - SOUTH  ===================
ECHO Converting file...
osmconvert us-south-latest.osm.pbf -o= us-south.o5m
ECHO Done!
ECHO Grabbing building tags...
osmfilter us-south.o5m --keep="building=residential =warehouse =industrial =house =retail =commercial" --drop-author --drop-version -o=Filtered/us-south-building.osm
ECHO Grabbing highway tags...
osmfilter us-south.o5m --keep="highway=residential =motorway =primary =secondary" --drop-author --drop-version -o=Filtered/us-south-highway.osm
ECHO Grabbing landuse tags...
osmfilter us-south.o5m --keep="landuse=residential =industrial =farmland =commercial" --drop-author --drop-version -o=Filtered/us-south-landuse.osm
:: next region
ECHO ============= US - NORTHEAST =================
ECHO Converting file...
osmconvert us-northeast-latest.osm.pbf -o= us-northeast.o5m
ECHO Done!
ECHO Grabbing building tags...
osmfilter us-northeast.o5m --keep="building=residential =warehouse =industrial =house =retail =commercial" --drop-author --drop-version -o=Filtered/us-northeast-building.osm
ECHO Grabbing highway tags...
osmfilter us-northeast.o5m --keep="highway=residential =motorway =primary =secondary" --drop-author --drop-version -o=Filtered/us-northeast-highway.osm
ECHO Grabbing landuse tags...
osmfilter us-northeast.o5m --keep="landuse=residential =industrial =farmland =commercial" --drop-author --drop-version -o=Filtered/us-northeast-landuse.osm
:: next region
ECHO =============   US - WEST  ===================
ECHO Converting file...
osmconvert us-west-latest.osm.pbf -o= us-west.o5m
ECHO Done!
ECHO Grabbing building tags...
osmfilter us-west.o5m --keep="building=residential =warehouse =industrial =house =retail =commercial" --drop-author --drop-version -o=Filtered/us-west-building.osm
ECHO Grabbing highway tags...
osmfilter us-west.o5m --keep="highway=residential =motorway =primary =secondary" --drop-author --drop-version -o=Filtered/us-west-highway.osm
ECHO Grabbing landuse tags...
osmfilter us-west.o5m --keep="landuse=residential =industrial =farmland =commercial" --drop-author --drop-version -o=Filtered/us-west-landuse.osm



