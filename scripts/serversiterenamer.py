import arcpy
#inTable = r'C:\Users\myusername\Documents\Project.gdb\LYRS_AND_TBLS_IN_MAPSERVICES'
inTable =  arcpy.GetParameterAsText(0)

#serversitefriendlynametable = r'C:\Users\myusername\Documents\Project.gdb\FRIENDLYSERVERSITENAMETABLE'
serversitefriendlynametable = arcpy.GetParameterAsText(1)

#iterate over the rows in the inTable and assign friendly names as defined in the serversitefriendlynametable.
#if no friendly name has been defined in the serversitefriendlynametable use the existing name.

with arcpy.da.UpdateCursor(inTable, ["MXD_PATH", "SERVERSITEFRIENDLYNAME"]) as update_cursor:
    for update_row in update_cursor:

        mxd_path = update_row[0]

        #the field for which we want to calculate a new value if we find one in the serversitefriendlynametable.Initialize with
        #the existing values, then if we find a new value in the serversitefriendlynametable we will overwrite the initial one.
        serversitefriendlyname = mxd_path

        #search through the friendlynametable for friendly names
        with arcpy.da.SearchCursor(serversitefriendlynametable, ["name", "friendlyname"]) as search_cursor:
            for search_row in search_cursor:
                
                serversite_name = search_row[0]
                serversite_friendlyname = search_row[1]
                
                if mxd_path.startswith(serversite_name):
                    serversitefriendlyname = serversite_friendlyname

        #then update the row
        update_cursor.updateRow([mxd_path, serversitefriendlyname])

# set the script tool's Completed parameter to true
arcpy.SetParameter(2, True)


