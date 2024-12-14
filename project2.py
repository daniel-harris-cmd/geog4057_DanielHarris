import arcpy
import os
import ee 
import csv
import pandas as pd


#example usage:
#python project2.py 'C:\Users\brdwh\Documents\programming 2\geog4057_DanielHarris\Project2' boundary.csv pnt_elev4.shp 32119


def getGeeElevation(workspace,csv_file,outfc_name,epsg=4326):
     
    
    #load csv file
    csv_file = os.path.join(workspace,csv_file)
    data = pd.read_csv(csv_file)
    dem = ee.Image('USGS/3DEP/10m')
    geometrys = [ee.Geometry.Point([x,y],f'EPSG:{epsg}') for x,y in zip(data['X'],data['Y'])]
    fc = ee.FeatureCollection(geometrys)
    orginial_info = fc.getInfo()
    sampled_fc = dem.sampleRegions(collection=fc,scale=10,geometries=True)
    
    sampled_info = sampled_fc.getInfo()
    for ind, itm in enumerate(orginial_info['features']):
        itm['properties'] = sampled_info['features'][ind]['properties']
        
    fcname = os.path.join(workspace,outfc_name)
    if arcpy.Exists(fcname):
        arcpy.management.Delete(fcname) #check to see if the fcname exists; if yes, delete it 
    arcpy.management.CreateFeatureclass(workspace,outfc_name,geometry_type='POINT',spatial_reference=epsg)
    
    #add elevations field
    arcpy.management.AddField(fcname,field_name='elevation',field_type='FLOAT')
    
    with arcpy.da.InsertCursor(fcname,['SHAPE@', 'elevation']) as cursor:
        for feat in orginial_info['features']:
            #get coordinates and create a point geometry
            coords = feat['geometry']['coordinates']
            pnt = arcpy.PointGeometry(arcpy.Point(coords[0],coords[1]), spatial_reference=32119)
            #get the properties and write to elevation
            elev = feat['properties']['elevation']
            cursor.insertRow([pnt,elev])

def main():
    import sys
    try:
        ee.Initialize(project='ee-brdwh22')
    except:
        ee.Authenticate()
        ee.Initialize(project='ee-brdwh22')
    workspace=sys.argv[1]
    csv_file=sys.argv[2]
    outfc_name=sys.argv[3]
    epsg=int(sys.argv[4])
        
    getGeeElevation(workspace=workspace,csv_file=csv_file,outfc_name=outfc_name,epsg=epsg)
    


if __name__ == '__main__':
    main()
    