import arcpy, os


#inTable = r'C:\Users\myusername\Project.gdb\LYRS_AND_TBLS_IN_MAPSERVICES'
inTable = arcpy.GetParameterAsText(0)

#outMapServicePoints = r'C:\Users\myusername\Project.gdb\MGIS.gdb\POINTS_MAPSERVICES'
outMapServicePoints = arcpy.GetParameterAsText(1)

#outGDBObjectPoints = r'C:\Users\myusername\Project.gdb\POINTS_GDBOBJECTS'
outGDBObjectPoints = arcpy.GetParameterAsText(2)

#outLines = r'C:\Users\myusername\Project.gdb\LINES'
outLines = arcpy.GetParameterAsText(3)

#create in-memory feature classes for outGDBObjectPoints and outMapServicePoints.
#Insert all points into these, then at the end dissolve and set the output to the actual feature classes 
outGDBObjectPoints_in_memory = arcpy.CreateFeatureclass_management("in_memory", "outGDBObjectPoints_in_memory", "POINT", outGDBObjectPoints, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", outGDBObjectPoints)
outMapServicePoints_in_memory = arcpy.CreateFeatureclass_management("in_memory", "outMapServicePoints_in_memory", "POINT", outMapServicePoints, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", outMapServicePoints)
outGDBObjectPoints_in_memory_dissolved = arcpy.CreateFeatureclass_management("in_memory", "outGDBObjectPoints_in_memory_dissolved", "POINT", outGDBObjectPoints, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", outGDBObjectPoints)
outMapServicePoints_in_memory_dissolved = arcpy.CreateFeatureclass_management("in_memory", "outMapServicePoints_in_memory_dissolved", "POINT", outMapServicePoints, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", outMapServicePoints)

#truncate the feature classes
arcpy.TruncateTable_management(outLines)
arcpy.TruncateTable_management(outGDBObjectPoints)
arcpy.TruncateTable_management(outMapServicePoints)


# iterate over rows in inTable. for each row insert one line feature into outLines.
# the service identifier is mxd_path, the gdb object identifier is dataSource
ms_dict = {'ms_ycoord_currentMax': 0}
ds_dict = {'ds_ycoord_currentMax': 0}


with arcpy.da.SearchCursor(inTable, ["DATASOURCEFRIENDLYNAME",
                                     "SERVERSITEFRIENDLYNAME",
                                     "DATASETNAME",
                                     "SERVICE_NAME",
                                     "MXD_PATH",
                                     "NAME",
                                     "DATASOURCE",
                                     "WORKSPACEPATH",
                                     "DEFINITIONQUERY"]) as cursor:
    for row in cursor:
        datasourcefriendlyname = str(row[0])
        serversitefriendlyname = str(row[1])
        datasetname = str(row[2])
        service_name = str(row[3])
        mxd_path = str(row[4])
        name = str(row[5])
        datasource = str(row[6])
        workspacepath = str(row[7])
        definitionquery = str(row[8])

        ms = serversitefriendlyname + '\\' + service_name
        ds = datasourcefriendlyname + '\\' + datasetname

        #set ycoord for map service
        if ms not in ms_dict:
            ms_ycoord_currentMax = max(ms_dict.values())
            ms_ycoord_newMax = ms_ycoord_currentMax + 100
            ms_dict[ms] = ms_ycoord_newMax

        #set ycoord for data source. Special case is if the data source could not be determined (e.g. querylayers, etc.) 
        if (datasourcefriendlyname == 'Failed to access this property') or (datasetname == 'Failed to access this property'):
            ds_dict[ds] = -100
        if ds not in ds_dict:
            ds_ycoord_currentMax = max(ds_dict.values())
            ds_ycoord_newMax = ds_ycoord_currentMax + 100
            ds_dict[ds] = ds_ycoord_newMax      
    
        #build the point and line geometries
        ds_point = arcpy.Point(0, ds_dict[ds])
        ms_point = arcpy.Point(10000, ms_dict[ms])    
        array = arcpy.Array([ds_point,ms_point])
        polyline = arcpy.Polyline(array)

        #insert the features
        with arcpy.da.InsertCursor(outGDBObjectPoints_in_memory, ["DATASOURCEFRIENDLYNAME", "DATASETNAME", "SHAPE@"]) as insert_cursor:
            insert_cursor.insertRow([datasourcefriendlyname, datasetname, ds_point])  
        with arcpy.da.InsertCursor(outMapServicePoints_in_memory, ["SERVERSITEFRIENDLYNAME", "MAPSERVICENAME", "SHAPE@"]) as insert_cursor:
            insert_cursor.insertRow([serversitefriendlyname, service_name, ms_point])
        with arcpy.da.InsertCursor(outLines, ["DATASOURCEFRIENDLYNAME",
                                              "DATASETNAME",
                                              "SERVERSITEFRIENDLYNAME",
                                              "MAPSERVICENAME",
                                              "MXD_PATH",
                                              "NAME",
                                              "DATASOURCE",
                                              "WORKSPACEPATH",
                                              "DEFINITIONQUERY",
                                              "SHAPE@"]) as insert_cursor:
            insert_cursor.insertRow([datasourcefriendlyname,
                                     datasetname,
                                     serversitefriendlyname,
                                     service_name,
                                     mxd_path,
                                     name,
                                     datasource,
                                     workspacepath,
                                     definitionquery,
                                     polyline])

#dissolve the point feature classes so that there is one point per geodatabase object, and one point per map service. (Instead of one per layer/table view.)
arcpy.Dissolve_management(outGDBObjectPoints_in_memory, os.path.join(arcpy.env.scratchGDB, "dissolvedGDBpoints"), ["datasourcefriendlyname", "datasetname"])
arcpy.Dissolve_management(outMapServicePoints_in_memory, os.path.join(arcpy.env.scratchGDB, "dissolvedMSpoints"), ["serversitefriendlyname", "MAPSERVICENAME"])

#append the new dissolved point features
arcpy.Append_management(os.path.join(arcpy.env.scratchGDB, "dissolvedGDBpoints"), outGDBObjectPoints)
arcpy.Append_management(os.path.join(arcpy.env.scratchGDB, "dissolvedMSpoints"), outMapServicePoints)









