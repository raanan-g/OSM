import geojson
import json
import geopandas as gpd
import shapely
from shapely.geometry import *
from osmnx import footprints as fp
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

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
    key : String
        indicates which types of tag to target (i.e, 'landuse', 'highway', 'amenity', etc.)
    area : bool
        indicates whether to return area of building objects
    
    Returns:
    ---------------------------
    ret_df : DataFrame
        contains original dataframe (reordered by region) with columns for tag statistics
    """
    addresses = get_us_region(addresses)
    
    ret_df = pd.DataFrame({'ID':[],'Address':[],'Lat_Lon':[]})
    for tag in tags:
        ret_df[tag] = []
        if area == True:
            t = tag+"_area"
            ret_df[t] = []
    
    # 1. Filter DataFrame by region
    for i in range(0,5): 
        _addresses = addresses[addresses.Reg_Code == i]
        print("Grabbing data in region {} of 5".format(i+1))
        pbar = '--------------------------------------------------'
        prog = '| {0:.0%}'.format(0)
        
        # 2. Load building data for the region
        if len(_addresses) > 0:
            path = USA[key][i] 
            gdf = gdf_from_json(path)
            print(pbar+prog,end='\r')
            
        progress = 0
        for k in _addresses.index:
            progress+=1
            
            # Create new vector to append at end of iteration 
            coords = _addresses['Lat_Lon'][k]
            ID = _addresses['ID'][k]
            Add = _addresses['Address'][k]
            df = pd.DataFrame({'ID':[ID],'Address':[Add],'Lat_Lon':[coords]})  
            
            # 3. Create bounding box as GeoDataFrame
            b = fp.bbox_from_point(coords,dist)

            # 4. Filter gdf by bounding box
            if key=='highway':
                # To get intersecting highways, we cannot use standard cx filtering
                bb = box(b[3],b[1],b[2],b[0])
                bb = Polygon(bb)
                bbox = gpd.GeoSeries([bb])
                bbox = gpd.GeoDataFrame({'geometry':bbox})
                # Filter gdf for all data intersecting Polygon bbox
                osm_in_bbox = gpd.sjoin(bbox, gdf, how = 'left', op = 'intersects')
            else:
                osm_in_bbox = gdf.cx[b[3]:b[2],b[1]:b[0]]
            
            #else:
            #    osm_in_bbox = gpd.overlay(bbox, gdf, how='intersection')
            
            #fig, ax = plt.subplots()
            #osm_in_bbox.plot(ax=ax,column=key,legend=True)
            #plt.show()
            # 5. Get value counts and total area

            for tag in tags:
                x = osm_in_bbox[osm_in_bbox[key]==tag]
                df[tag] = [len(x)]
                if area == True:
                    t = tag+"_area"
                    df[t] = [sum(x['geometry'].area)]

            # 6. Store as new columns in DataFrame
            ret_df = ret_df.append(df)
            lft = round(progress*10/len(_addresses))
            stars = '*' * lft * 5
            pbar = stars + pbar[(lft*5):]
            if progress != 0 and progress==len(_addresses):
                print(pbar+"| {0:.0%}".format(progress/len(_addresses)))
            else:
                print(pbar+"| {0:.0%}".format(progress/len(_addresses)),end='\r')
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
