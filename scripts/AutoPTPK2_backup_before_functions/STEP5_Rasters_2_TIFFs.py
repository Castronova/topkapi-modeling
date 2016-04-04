import arcpy
from arcpy import env
import os

def step5_convert_rasters_to_tiff(SSURGO_raster_folder, output_tiff):
    '''

    :param SSURGO_raster_folder: Folder where all the ssurgo rasters are saved
    :param output_tiff: folder where the TIFF created are saved
    :return: saves tiffs to the given folder
    '''

    # a list of folders inside the folder where ssurgo rasters are created
    folders_inside_SSURGO_raster_folder = []
    [folders_inside_SSURGO_raster_folder.append(folders) for folders in os.listdir(SSURGO_raster_folder)
        if os.path.isdir(os.path.join(SSURGO_raster_folder, folders))]


    try:

        # for one_ssurgo_property_folder in folders_inside_SSURGO_raster_folder:        #
            #     pass

        filepath = []
        for path, subdirs, files in os.walk(SSURGO_raster_folder):
            for filename in files:
                f = os.path.join(path, filename)
                filepath.append(f)
                if f.split(".")[0][-1] == "c":
                    print f.split(".")[0]
                    try:
                        arcpy.RasterToOtherFormat_conversion(Input_Rasters=f.split(".")[0],
                                                          Output_Workspace=output_tiff, Raster_Format="TIFF")

                        newRasterlayer = arcpy.mapping.Layer(tempOutputRasterFullpath+"c")    # create a new layer
                        arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")

                    except Exception, e:
                        print e
            arcpy.AddMessage("### Raster %sc created ###")



    except Exception, e:
     arcpy.AddMessage("!!!!!!!!!!Error encouncered during conversion to tiff ")



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




