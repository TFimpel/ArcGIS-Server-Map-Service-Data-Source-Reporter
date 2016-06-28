# ArcGIS-Server-Map-Service-Data-Source-Reporter

Python scripts to iterate over .mxds of one or more ArcGIS Server sites and produce a "report" on which data sources are associated with each map service.

![capture](https://cloud.githubusercontent.com/assets/7443922/16395372/1baca152-3c7f-11e6-8fd4-873573d0fce2.JPG)

The scripts are designed to be run as Script tools through ArcMap's geoprocessing framework. To use them download the file geodatabase, it contains everything that's needed: 
+ two point feature classes
 - one representing data sources
 - one representing map services
+ one line feature class representing layer or table views in map services
+ two geodatabase tables
 - one to enter alias-name pairs for server sites
 - one to enter alias-name pairs for data source paths (e.g. connection strings to databases can be formatted in many ways but actually connect to identical databases)
+ one geodatabase toolbox with
 - four tools (made form the python scripts)
 - one model that shows an example of how the scripts can be executed in sequence against 5 ArcGIS server sites (add or remove sites as needed. Instead of removing you can also point any writer.py tool except for the first one to an empty folder directory. This is the quickest way to re-use the model.)

Note:
+ you'll need access to the ArcGIS Server site's file storage (specifically, the folder .../directories/arcgissystem/arcgisinput because that's where the mxd's are stored. Alternatively you could run the tools against a copy of this folder.
+ doesn't deal very nicely with querylayres, annotation feature classes, child geodatabase versions in that it can only report the limited properties that the arcpy module can read from these types of layer/table views.

I developed this as a class project. For more detail please refer to my project write-up, get in touch with me, or log an issue here on Github.

