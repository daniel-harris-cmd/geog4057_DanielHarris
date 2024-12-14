import json
import arcpy
import os

def importNoTaxJSON(workspace=r'C:\Users\brdwh\Documents\programming 2\geog4057_DanielHarris\Project1',json_file='no_tax.json',out_fc='notax_fc.shp'):
    with open(json_file,'r') as file:
        tax_json = json.load(file)
        
    for row in tax_json['data']:
        row[8] = arcpy.FromWKT(row[8])
        
    fcname = out_fc
    fc_fullname = os.path.join(workspace,fcname)
    if arcpy.Exists(fc_fullname):
        arcpy.management.Delete(fc_fullname)
        
    arcpy.management.CreateFeatureclass(out_path=workspace,out_name=fcname,geometry_type='POLYGON',spatial_reference=4236)

    fields = tax_json['meta']['view']['columns']
    field_type = ['TEXT','TEXT','LONG','LONG','TEXT','LONG','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT']
    field_names = []
    for ind,field in enumerate(fields):
        name = field['name']
        if name == 'the_geom':
            continue
        if name.lower() == 'id':
            name = f'id_{ind}'
        max_len = min(10,len(name))
        name = name[:max_len]
        field_names.append(name)
    field_names = [field.replace(" ","_") for field in field_names]
    field_names = [field.replace(".","_") for field in field_names]

    for ind,field_name in enumerate(field_names):
        arcpy.management.AddField(fc_fullname,field_name=field_name,field_type=field_type[ind])
    field_names.append('SHAPE@')

    with arcpy.da.InsertCursor(fc_fullname,field_names=field_names) as cursor:
        for row in tax_json['data']:
            new_row = []
            for ind, value in enumerate(row):
                if ind == 8:
                    continue
                if value == None:
                    value = ""
                new_row.append(value)
            new_row.append(row[8])
            cursor.insertRow(new_row)
            
def main():
    importNoTaxJSON(out_fc='notac_fc_3.shp')
    
if __name__ == '__main__':
    main()