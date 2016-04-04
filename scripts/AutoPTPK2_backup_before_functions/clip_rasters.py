import arcpy
from arcpy import env
from arcpy.sa import *

#it clips all the rasters based on one SSURGO dem given
#NEED TO MANUALLY input rasters name
#rasters need to be as a layer

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

arcpyLayer = arcpy.GetParameterAsText(0)
outDIR = arcpy.GetParameterAsText(1)




#convert all the rasters to tif
list_of_rasters = ['fdr', 'drp', 'DEM_prj', 'Land_Use_Prj', 'n_Channel', 'n_Overland',
                   'Por-t_UT612','Ksat-t_UT612' , 'Ksat-s_UT612' , 'EfPor-t_UT612', 'BblPr-t_UT612']
list_of_rasters_withInvertedComma = ['"' + item+ '"' for item in list_of_rasters]

joining_letter = ";"
joint_string = ";".join(list_of_rasters_withInvertedComma)
joint_string = '"fdr";"drp";"DEM_prj";"Land_Use_Prj";"n_Channel";"n_Overland";"Por-t_UT612";"Ksat-t_UT612";"Ksat-s_UT612";"EfPor-t_UT612";"BblPr-t_UT612"'



#convert rasters to TIF
for raster in list_of_rasters:
    arcpy.RasterToOtherFormat_conversion(Input_Rasters=raster, Output_Workspace= outDIR, Raster_Format="TIFF")

try:

    arcpy.gp.ExtractByMask_sa(arcpyLayer, "Boundary", outDIR+"/"+arcpyLayer)
    arcpy.AddMessage("#########"+arcpyLayer+" Successfully extracted ##########")
except Exception, e:
    arcpy.AddMessage(arcpyLayer+" **************ERROR *********could not be extracted**********")
    print e

# arcpy.RasterToOtherFormat_conversion(Input_Rasters="'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/fdr';'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/drp';'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/dem_prj';'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/n_overland';'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/n_channel';'C:/Users/Prasanna/Box Sync/Red Butte Creek rasters/land_use_prj'",
#                                      Output_Workspace="C:/Users/Prasanna/Box Sync/Red Butte Creek rasters",
#                                      Raster_Format="TIFF")