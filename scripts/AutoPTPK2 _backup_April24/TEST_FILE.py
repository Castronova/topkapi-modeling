# import arcpy
# from arcpy.sa import *
# import os
# from arcpy import env
#
# arcpy.env.overwriteOutput = True
# arcpy.CheckOutExtension("Spatial")
#
# arcpy.env.workspace = arcpy.env.scratchWorkspace = r"C:\Users\WIN10-HOME\Documents\ArcGIS\Default.gdb"
#
# inputfc = r"E:\Research Data\00 Red Butte Creek\RBC_3\SSURGO_Folders\UT612\spatial\soilmu_a_ut612.shp"
# outputfc = os.path.join(arcpy.env.workspace ,"out2.shp")
# fieldname = "MUKEY"
# fieldvalue = 613806


# One thing that makes writing WHERE clauses a lot easier is to use the AddFieldDelimiters function,
# which automatically adds the correct, DBMS-specific delimiters for field identifiers, such as double-quotes
# for FGDB and brackets for PGDB.
# The other thing you have to consider is whether the value is a number, string, or other data type. Specifically,
# strings are wrapped in single quotes while numbers are not. You could check the field type and add single
# quotes if it is a string field.

def buildWhereClause(table, field, value):
    """Constructs a SQL WHERE clause to select rows having the specified value
    within a given field and table."""

    # Add DBMS-specific field delimiters
    fieldDelimited = arcpy.AddFieldDelimiters(table, field)

    # Determine field type
    fieldType = arcpy.ListFields(table, field)[0].type

    # Add single-quotes for string field values
    if str(fieldType) == 'String':
        value = "'%s'" % value

    # Format WHERE clause
    whereClause = "%s = %s" % (fieldDelimited, value)
    arcpy.AddMessage(whereClause)
    return whereClause

if __name__ == "__main__":
    reclassifying_field = "Value"
    landuse_n_file_path = "landuse_n.txt"

    landuse_n_file = open(landuse_n_file_path, "r")
    landuse_n_file_temp = open("landuse_n_temp.txt" , "w")


    for line in landuse_n_file.readlines():
        value = line.split(":")[-1].split("\n")[0]
        new_value = float(value) * 10000.
        print new_value
        temp_line = []
        landuse_n_file_temp.write(line.split(":")[0]+ " : " +  str(new_value) + "\n")

    landuse_n_file.close()
    landuse_n_file_temp.close()




















# whereClause = "soilmu_a_ut612.MUKEY = 482993"
# # whereClause = buildWhereClause(inputfc, fieldname, fieldvalue)
# arcpy.SelectLayerByAttribute_management(inputfc, outputfc, whereClause)
# arcpy.CopyFeatures_management (inputfc, outputfc)
#
# arcpy.Dissolve_management(in_features=outputfc, out_feature_class="ut612_Dissolve7",
#                           dissolve_field="",
#                           statistics_fields="",
#                           multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")













# """ Project DEM to UTM """
#
# ProjectRaster(in_raster=inFile, out_raster="DEM_Prj", out_coor_system=projection_file,
#                                resampling_type="NEAREST",   #cell_size=str(cell_size) + " "+str(cell_size),
#                                Registration_Point="")
#
# CopyRaster(in_raster=inFile, out_rasterdataset="DEM_temp",
#                             nodata_value="-9999")
#
# Resample(in_raster= "DEM_temp",
#                           out_raster= "DEM_Prj",
#                           cell_size= str(cell_size)+" "+str(cell_size), resampling_type="NEAREST")
