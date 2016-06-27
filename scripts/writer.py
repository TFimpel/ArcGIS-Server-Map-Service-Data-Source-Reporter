#Author: Tobias Fimpel
#This script will iterate over a specified file directory and all of it's subdirectories, find all the .mxd files within
#these, and write certain layer properties of the layers within these .mxd files to a specified ArcGIS geodatabase table.

import os, arcpy

############## GP TOOL INPUT PARAMETERS ################

#The input directory with .mxd files (for example, the ArcGIS Server site "arcgisinput" folder).
input_dir  = arcpy.GetParameterAsText(0)

#ArcGIS Geodatabase table to write the layer properties to.
output_gdb_table  = arcpy.GetParameterAsText(1)

#Boolean value to indicate whether to truncate the table before inserting new rows.
truncate_first = arcpy.GetParameterAsText(2)

#######################################################

#Truncate the table if truncate_first is True. String formatting required for gp toolbox.
if str(truncate_first) == 'true':
    arcpy.TruncateTable_management(output_gdb_table)

#Function to build a list of .mxd file paths.
def build_file_list (in_dir,file_extension):
    """This function iterates over a directory and all subdirectories, identifies all .mxd files therein,
    and returns the full file path to these .mxd files as a python list."""
    file_list = []
    for root, dirs, files in os.walk(in_dir):
        for name in files:
            if name.endswith(file_extension):
                file_list.append(os.path.join(root, name))
    return file_list

#Function to insert a row into the output_gdb_table
def insert_row(table, field_list, value_list):
    """This function inserts into a specified ArcGIS geodatabase table a list of values for a given list of fields"""
    cursor = arcpy.da.InsertCursor(table, field_list)
    cursor.insertRow(value_list)


#Function takes a lyr or tbl object and returns a dictionary of its properties.
def get_lyr_or_tbl_props (lyr_or_tbl):
    """Queries the properties of a layer or table object and returns these properties
    and their values as a python dictionary. If a certain property cannot be accessed
    it's value will be set to the string 'Failed to access this property'."""
    props = {}
    try:
        props['isGroupLayer'] = lyr_or_tbl.isGroupLayer
    except:
        props['isGroupLayer'] = 'Failed to access this property'
    try:
        props['name'] = lyr_or_tbl.name
    except:
        props['name'] = 'Failed to access this property'
    try:
        props['dataSource'] = lyr_or_tbl.dataSource
    except:
        props['dataSource'] = 'Failed to access this property'
    try:
        props['datasetName'] = lyr_or_tbl.datasetName
    except:
        props['datasetName'] = 'Failed to access this property'
    try:
        props['workspacePath'] = lyr_or_tbl.workspacePath
    except:
        props['workspacePath'] = 'Failed to access this property'
    try:
        props['definitionQuery'] = lyr_or_tbl.definitionQuery
    except:
        props['definitionQuery'] = 'Failed to access this property'
    return props

#build a list of mxd file paths
mxd_files = build_file_list(input_dir, '.mxd')


#iterate over each mxd file and report on the layer and table data sources
for item in mxd_files:

    mxd = arcpy.mapping.MapDocument(item)
    try:
        mxd_path = item
    except:
        mxd_path = 'Failed to access this property'
    print mxd_path

    #only process map services, exclude gp services etc.
    if '.MapServer' in (mxd_path):

        substring_start = input_dir + '\\'
        substring_end = '.MapServer'
        try:
            service_name = (item.split(substring_start))[1].split(substring_end)[0]
        except:
            service_name = 'Failed to access this property'
        print service_name

        #build a list of all layers as well as all tables in the mxd
        layers_and_tables = arcpy.mapping.ListLayers(mxd) + arcpy.mapping.ListTableViews(mxd)

        #iterate over the list of layers and tables, get the relevant properties, and if it isn't a group layer then insert them into the geodatabase table
        for item in layers_and_tables:
            props = get_lyr_or_tbl_props(item)
            print props

            if (props['isGroupLayer'] is False) or  props['isGroupLayer'] == 'Failed to access this property':
                fields = ['mxd_path', 'service_name', 'name', 'dataSource', 'datasetName', 'workspacePath', 'definitionQuery']
                values = (mxd_path, service_name, props['name'], props['dataSource'], props['datasetName'], props['workspacePath'], props['definitionQuery'])
                insert_row(output_gdb_table, fields, values)
                print('inserted row')
            else:
                print('this is a group layer, do nothing')


# set the script tool's Completed parameter to true
arcpy.SetParameter(3, True)










