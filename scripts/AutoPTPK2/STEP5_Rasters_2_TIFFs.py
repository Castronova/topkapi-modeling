import arcpy
from arcpy import env
import os

def step5_convert_rasters_to_tiff(SSURGO_raster_folder, DEM_rasters_folder, output_tiff):
    '''

    :param SSURGO_raster_folder: Folder where all the ssurgo rasters are saved
    :param output_tiff: folder where the TIFF created are saved
    :return: saves tiffs to the given folder
    '''


    try:

        filepath = []
        for path, subdirs, files in os.walk(SSURGO_raster_folder):
            for filename in files:
                f = os.path.join(path, filename)
                if f.split(".")[0][-1] == "c":
                    filepath.append(f)

        # f would be full path for a filename
        for f in filepath:
            try:
                arcpy.RasterToOtherFormat_conversion(Input_Rasters=f.split(".")[0],
                                                  Output_Workspace=output_tiff, Raster_Format="TIFF")

                newRasterlayer = arcpy.mapping.Layer(tempOutputRasterFullpath+"c")    # create a new layer
                arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")
                arcpy.AddMessage("### Raster created ###")
            except Exception, e:
                print e

    except Exception, e:
        arcpy.AddMessage("!!!!!!!!!!Error encouncered during conversion to tiff from SSURGO rasters ")



    raster_list_from_DEM_processed = ["fdr_c_r", "mask_r" , "n_overland", "slope_c","str_c_r" , "DEM_Prj_fc","Land_Use_Prj_c", "fac", "STRAHLER" ]

    for raster in raster_list_from_DEM_processed:
        f = os.path.join(DEM_rasters_folder , raster)
        try:
            arcpy.RasterToOtherFormat_conversion(Input_Rasters=f,
                                              Output_Workspace=output_tiff, Raster_Format="TIFF")

            newRasterlayer = arcpy.mapping.Layer(tempOutputRasterFullpath+"c")    # create a new layer
            arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")
            arcpy.AddMessage("### Raster created ###")
        except Exception, e:
            arcpy.AddMessage("!!!!!!!!!!Error encouncered during conversion to tiff from DEM processing rasters ")


    try:

        #merge rasters present in outDir
        FOLDERSOFRASTERS = [folder.split('_')[0] for folder in [list[1] for list  in soilProperties]]

        for afolderOfRaster in FOLDERSOFRASTERS:
            arcpy.env.workspace = outDir+"/"+afolderOfRaster
            raster_list=arcpy.ListRasters("", "tif")
            arcpy.CompositeBands_management(raster_list, outDir+"/"+afolderOfRaster+".tif") #will save output on the same folder

            newRasterlayer = arcpy.mapping.Layer(outDir+"/"+afolderOfRaster +".tif")    # create a new layer
            arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")

    except Exception,e :
        arcpy.AddMessage("!!!!!!!!!!Error in merging encouncered, at line 159 :"+ str(e))






# DEM_processed_raster_list_fullpath = [os.path.join(DEM_rasters_folder, rasterName) for rasterName in raster_list_from_DEM_processed]
# [filepath.append(a_raster_from_DEM) for a_raster_from_DEM in DEM_processed_raster_list_fullpath]
# filepath = list(set(filepath))
