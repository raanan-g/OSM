import json
import ogr
import geojson
import geopandas as gpd

def osmtogdf(path, layer='polygons'):
    """
    Generate a geopandas GeoDataFrame from a .osm file
    
    Parameters:
    ---------------
    path : file path to .osm file
        
    layer : String -> either 'polygons' or 'lines'
    
    Returns:
    ---------------
    gdf: GeoDataFrame
        GeoDataFrame containing all data from .osm file
    """
    driver = ogr.GetDriverByName('OSM')
    data = driver.Open(path)

    if layer == 'lines':
        p_layer = data.GetLayer('points')
        l_layer = data.GetLayer('lines')

        features=[x for x in p_layer]
        features1=[x for x in l_layer]

        x_data = []

        for feature in features:
            x_data.append(feature.ExportToJson(as_object=True))

        for feature in features1:
            x_data.append(feature.ExportToJson(as_object=True))
    elif layer == 'polygons':
        mp_layer = data.GetLayer('multipolygons')
        features=[x for x in p_layer]
        x_data = []

        for feature in features:
            x_data.append(feature.ExportToJson(as_object=True))
    else:
        print("Error, layer type not supported")
        
    path = path.replace('osm','json')
    path = path.replace('Filtered','Filtered/GeoJSON')

    with open(path, 'w') as outfile:
        json.dump(x_data, outfile)

    with open(path) as json_file:
        test_data = json.load(json_file)

    test_data = geojson.FeatureCollection(test_data)
    gdf = gpd.GeoDataFrame.from_features(test_data)
    
    return gdf
