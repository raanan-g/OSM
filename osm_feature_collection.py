import geojson
import json
import geopandas as gpd
import shapely
from shapely.geometry import *
from osmnx import footprints as fp
import pandas as pd
#from tqdm.autonotebook import tqdm

buildings = ['us-midwest-building.geojson',
             'us-northeast-building.geojson',
             'us-pacific-building.geojson',
             'us-south-building.geojson',
             'us-west-building.geojson']

highways = ['us-midwest-highway.geojson',
             'us-northeast-highway.geojson',
             'us-pacific-highway.geojson',
             'us-south-highway.geojson',
             'us-west-highway.geojson']

landuse = ['us-midwest-landuse.geojson',
           'us-northeast-landuse.geojson',  
           'us-pacific-landuse.geojson',
           'us-south-landuse.geojson',
           'us-west-landuse.geojson']
           
# DataFrame stores all file paths by region and OSM key
USA = pd.DataFrame({'building':buildings,'highway':highways,'landuse':landuse})

def gdf_from_json(path):
    # import json file
    with open(path) as json_file:
        test_data = json.load(json_file)
    # create feature collection
    test_data = geojson.FeatureCollection(test_data)
    # turn into GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(test_data)
    
    return gdf

def osm_from_points(addresses, dist, key, tags, area=False):
    """
    Create a dataframe of key=value pair statistics within a bounding box 
    around a set of coordinates.
    
    Parameters:
    ---------------------------
    addresses : DataFrame
        must have columns 'Address', 'ID' & 'Lat_Lon' (tuple)
    dist : int
        how many meters the north, south, east, and west sides of the box should
        each be from the point
    tags : list, dict
        specific tags (key=tag) to target from OSM data. 
        Find more in the OSM Map Features wiki: https://wiki.openstreetmap.org/wiki/Map_features        
    keys : String
        indicates which types of tag to target (i.e, 'landuse', 'highway', 'amenity', etc.)
    area : bool
        indicates whether to return area of building objects
    
    Returns:
    ---------------------------
    ret_df : DataFrame
        contains original dataframe (reordered by region) with columns for tag statistics
    """
    addresses = get_us_region(addresses)
    
    ret_df = pd.DataFrame({'ID':[],'Lat_Lon':[]})
    for tag in tags:
        ret_df[tag] = []
        if area == True:
            t = tag+"_area"
            ret_df[t] = []
    
    # 1. Filter DataFrame by region
    for i in range(0,5): 
        _addresses = addresses[addresses.Reg_Code == i]
        print("Grabbing data in region {} of 5...".format(i+1))
        # 2. Load building data for the region
        path = USA[key][i] 
        gdf = gdf_from_json(path)
        
        progress = 0
        for k in _addresses.index:
            progress+=1
            
            # Create new vector to append at end of iteration 
            coords = _addresses['Lat_Lon'][k]
            ID = _addresses['ID'][k]
            df = pd.DataFrame({'ID':[ID],'Lat_Lon':[coords]})  
            
            # 3. Create bounding box as GeoDataFrame
            bb = fp.bbox_from_point(coords,dist)
            bb = box(bb[3],bb[1],bb[2],bb[0])
            bb = Polygon(bb)
            bbox = gpd.GeoSeries([bb])
            bbox = gpd.GeoDataFrame({'geometry':bbox})

            # 4. Overlay bounding box onto gdf
            gdf = gdf.reset_index(drop=True)
            bbox = bbox.reset_index(drop=True)
            osm_in_bbox = gpd.overlay(bbox, gdf, how='intersection')

            # 5. Get value counts and total area

            for tag in tags:
                x = osm_in_bbox[osm_in_bbox[key]==tag]
                df[tag] = [len(x)]
                if area == True:
                    t = tag+"_area"
                    df[t] = [sum(x['geometry'].area)]

            # 6. Store as new columns in DataFrame
            ret_df = ret_df.append(df)
            print("    Progress: {0:.0%}".format(progress/len(_addresses)))
    return ret_df

def get_us_region(addresses):
    """
    Add a region code column to a dataframe of US addresses
    
    Parameters:
    ---------------
    addresses : DataFrame
        must contain 'Address' column with two-character state abbreviation
        
    Returns:
    ---------------
    addresses: DataFrame
        Original DataFrame with a column 'Reg_Code' c(0,4) corresonding to the 
        USA DataFrame index
    """
    midwest = ('ND','SD','NE','KS','MO','IL','IN','OH','MI','WI','MN','IA') # index 0 in USA dataframe
    northeast = ('ME','NH','VT','MA','RI','CT','NY','PA','NJ')# index 1 in USA dataframe
    pacific = ('AK','HI')# index 2 in USA dataframe
    south = ('TX','OK','AR','LA','MS','AL','FL','GA','SC','NC','VA','DE','MD','WV','VA','KY','TN','DC')# index 3 in USA dataframe
    west = ('WA','OR','CA','AZ','NM','CO','WY','MT','ID','NV','UT')# index 4 in USA dataframe
        
    reg = []
    for address in addresses['Address']:
    
        x = address.split(", ")

        for c in x:
            if len(c.strip())==2:
                if c.strip() in ('WA','OR','CA','AZ','NM','CO','WY','MT','ID','NV','UT','AK','HI','TX','OK','AR','LA','MS','AL','FL','GA','SC','NC','VA','DE','MD','WV','VA','KY','TN','DC','ND','SD','NE','KS','MO','IL','IN','OH','MI','WI','MN','IA','ME','NH','VT','MA','RI','CT','NY','PA','NJ'):
                    state = c.strip()
                    break

        if state in midwest:
            y= int(0)
        elif state in northeast:
            y= int(1)
        elif state in pacific:
            y= int(2)
        elif state in south:
            y= int(3)
        elif state in west:
            y= int(4)
        else:
            y = np.nan
        
        reg.append(y)
        
    addresses['Reg_Code'] = reg
        
    return addresses
