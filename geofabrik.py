# OSM Data Pipeline

# Step 1: Download each region's pbf file from geofrabrik.de
import pandas as pd
import urllib.request

regs = 'us-midwest','us-northeast','us-pacific','us-south','us-west'
url = "http://download.geofabrik.de/north-america/"

for reg in regs:
	link = url+reg+'-latest.osm.pbf'
	path = reg+'.pbf'
	urllib.request.urlretrieve(link, path)



