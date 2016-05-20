import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

inputfc = r"E:\Research Data\00 Red Butte Creek\RBC_3\SSURGO_Folders\UT612\spatial\soilmu_a_ut612.shp"



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
