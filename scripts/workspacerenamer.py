import arcpy

#example inTable = r'C:\Users\myusername\Documents\Project.gdb\LYRS_AND_TBLS_IN_MAPSERVICES'
inTable = arcpy.GetParameterAsText(0)

#friendlyworkspacenametable = r'C:\Users\myusername\Documents\Project.gdb\\FRIENDLYWORKSPACENAMETABLE'
friendlyworkspacenametable = arcpy.GetParameterAsText(1)

#iterate over the rows in the inTable and assign friendly names as defined in the friendlyworkspacenametable.
#if no friendly name has been defined in the friendlyworkspacenametable use the existing name.

with arcpy.da.UpdateCursor(inTable, ["DATASOURCE", "DATASOURCEFRIENDLYNAME"]) as update_cursor:
    for update_row in update_cursor:

        datasource = update_row[0]

        #the field for which we want to calculate a new value if we find one in the friendlyworkspacenametable.Initialize with
        #the existing values, then if we find a new value in the friendlyworkspacenametable we will overwrite the initial one.
        datasourcefriendlyname = datasource

        #search through the friendlynametable for friendly names
        with arcpy.da.SearchCursor(friendlyworkspacenametable, ["name", "friendlyname"]) as search_cursor:
            for search_row in search_cursor:
                
                database_name = search_row[0]
                database_friendlyname = search_row[1]
                
                if datasource.startswith(database_name):
                    datasourcefriendlyname = database_friendlyname

        #then update the row
        update_cursor.updateRow([datasource, datasourcefriendlyname])

# set the script tool's Completed parameter to true
arcpy.SetParameter(2, True)
