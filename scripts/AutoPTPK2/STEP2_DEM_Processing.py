import arcpy
import os
from arcpy.sa import *

'''
Issues:
If output is folder, dissolve (around line 77 ) does not work

Improvements
Full path may not be required when we hae assigned workspace
Default Threshold of flow accumulation
Clipping / extracting by a mask
Soil depth is in string

Snapped outlet_point_sf/outlet needs to be created as a seperated point shapefile
soil depth still missing
SnapPourPoint distance = (5) *cell size
Mask is created after delineating wshed from Outlet created in SnapPourPoint process. BUT,
    the outlet raster created takes its value from a field in vector point outlet shapefile as user input
    if the file does not have 1, the mask will end up with value != 1. Therefore,
    for user input outlet, need to add field and assign value =1

Threshold should also be such that the area draining = 25 km2
'''

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True    # to overwrite

DEM = arcpy.GetParameterAsText(0)
land_use = arcpy.GetParameterAsText(1)
outDir= arcpy.GetParameterAsText(2)
outlet_point_sf = arcpy.GetParameterAsText(3)
threshold = arcpy.GetParameterAsText(4)


def step2_dem_processing(DEM, land_use, outDir, outlet_point_sf, threshold):
    """
    :param DEM: Projected DEM (for now, projected to UTM zone 12)
    :param land_use: Projected Land_use raster from NLCD
    :param outDir: geodatabase where the rasters created are stored
    :param outlet_point_sf: the point shapefile for the outlet point
    :param threshold: Threshold for defining stream
    :return:
    """

    arcpy.AddMessage("*** This scripts Processes the DEM and Landuse data *** ")

    # Un tested
    if threshold == "": # threshold = "3000"
        area_threshold = 1 #km2
        threshold = int (area_threshold / ( (arcpy.Describe(DEM).children[0].meanCellHeight)/1000. )**2)

    # Set workspace environment
    arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir
    # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
    arcpy.env.snapRaster = DEM              # Set Snap Raster environment
    arcpy.env.overwriteOutput = True

    #trial
    Fill(DEM).save("fel")
    FlowDirection("fel").save('fdr')
    FlowAccumulation('fdr').save('fac')
    Slope("fel", "DEGREE", "1").save('slope')
    #arcpy.gp.Slope_sa(fill, slope, "DEGREE", "1")
    FlowDirection("fel", "NORMAL",'slope').save('fdr')
    SnapPourPoint(outlet_point_sf, 'fac', 100,"").save("Outlet") # 3* arcpy.Describe(DEM).children[0].meanCellHeight
    Watershed('fdr', "Outlet").save("mask")
    StreamRaster = (Raster('fac') >= float(threshold)) & (Raster("mask") >= 0) ; StreamRaster.save('str')

    try:
        # Added code
        outStreamLink = StreamLink('str','fdr') ; outStreamLink.save('strlnk')
        Catchment = Watershed('fdr', 'strlnk'); Catchment.save("catchment")            # no need catchment, mask is good
        StreamToFeature('strlnk', 'fdr', "Streamnet","NO_SIMPLIFY")                    # stream defined
        arcpy.RasterToPolygon_conversion("catchment", "CatchTemp", "NO_SIMPLIFY")
        arcpy.Dissolve_management("catchtemp", "CatchPoly", "GRIDCODE")                # dissolves extra catchments
        arcpy.Dissolve_management(in_features="catchtemp", out_feature_class="CatchPoly.shp", dissolve_field="GRIDCODE",
                                  statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    except Exception, e:
        arcpy.AddMessage("FAILURE: "+ e)


    arcpy.AddMessage("SUCCESS: Fdr, Fac, Stream processing complete ")

    #clip to the mask--------------------------------------------------------
    arcpy.gp.ExtractByMask_sa('str', "mask", 'str_c')
    arcpy.gp.ExtractByMask_sa('fdr', "mask", "fdr_c")
    arcpy.gp.ExtractByMask_sa("slope", "mask", "slope_c")
    arcpy.gp.ExtractByMask_sa("fel", "mask", DEM+"_fc")      # f for fill, c for clip
    arcpy.gp.ExtractByMask_sa(land_use, "mask", land_use+"_c")

    # after clipping, we only use clipped files
    land_use = land_use +"_c"
    str = "str_c"
    fdr = "fdr_c"
    slope = "slope_c"
    SD = "SD_c"    # c for consistency in naming

    #strahler for mannings for channel
    arcpy.gp.StreamOrder_sa(str, fdr, "STRAHLER", "STRAHLER")  # the last parameter, Strahler string, is actually a method of ordering stream. NOT A NAME
    arcpy.AddMessage("SUCCESS: Strahler stream order processing complete")

    arcpy.AddField_management(in_table= land_use , field_name="ManningsN", field_type="LONG",field_precision="",
                              field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddMessage("SUCCESS: Adding field to Land Use complete")

    # multiply Manning's n by 10,000. We will later divide it by 10,000 again
    arcpy.gp.Reclassify_sa(land_use, "Value", "11 0;21 404;22 678;23 678;24 404;31 113;41 3600;42 3200;43 4000;52 4000;71 3680;81 3250;82 3250;90 860;95 1825", outDir+"/nx10000_Overl", "DATA")
    arcpy.AddMessage("SUCCESS: Land Use reclassification to obtain Mannings n complete ")

    # reclassifying Strahler order to get Manning's for channel in the same way
    arcpy.gp.Reclassify_sa("STRAHLER", "Value", "1 500;2 400;3 350;4 300;5 300;6 250", outDir+"/nx10000_Chan", "DATA")
    arcpy.AddMessage("SUCCESS: Strahler order raster reclassification to obtain Mannings n complete **********")

    # now, NLCD to n calculate the real Manning's, divide reclassified raster by 10,000
    arcpy.gp.RasterCalculator_sa(""""nx10000_Overl" /10000.0""", outDir+"/n_Overland")
    arcpy.gp.RasterCalculator_sa(""""nx10000_Chan" /10000.0""", outDir+"/n_Channel")

    arcpy.AddMessage("SUCCESS: All of DEM processing complete ")

    # Reclassify to change no data to -9999
    arcpy.gp.Reclassify_sa(fdr, "Value", "1 1;2 2;4 4;8 8;16 16;32 32;64 64;128 128;NODATA -9999", fdr+"_r", "DATA")
    arcpy.gp.Reclassify_sa(str, "Value", "0 0;1 1;NODATA -9999", str + "_r", "DATA")
    arcpy.gp.Reclassify_sa("mask", "Value", "2 1", "mask_r", "DATA")

    arcpy.CopyRaster_management(in_raster="mask_r",out_rasterdataset="SD",nodata_value="-9999")
    arcpy.AddMessage("SUCCESS: Assigning -9999 to NoData, mask and Soil depth creation  completed")


    # Add n_Channel and n_Overland to layer and then to map document
    mxd = arcpy.mapping.MapDocument("CURRENT")                      # get the map document
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                   # first data-frame in the document
    try:
        fdr_layer = arcpy.mapping.Layer(outDir+"/"+ "mask_r")                 # create a new layer
        arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")

        dem_layer = arcpy.mapping.Layer(outDir+"/"+ "DEM_Prj_fc" )                 # create a new layer
        arcpy.mapping.AddLayer(df, dem_layer ,"TOP")

        landuse_layer = arcpy.mapping.Layer(outDir+"/"+ "LandUse_Prj_fc" )                 # create a new layer
        arcpy.mapping.AddLayer(df, landuse_layer ,"TOP")

        # n_Channel_layer = arcpy.mapping.Layer(outDir+"/n_Channel")      # create a new layer
        # arcpy.mapping.AddLayer(df, n_Channel_layer ,"TOP")

        n_Overland_layer = arcpy.mapping.Layer(outDir+"/n_Overland")    # create a new layer
        arcpy.mapping.AddLayer(df, n_Overland_layer,"TOP")

        fdr_layer = arcpy.mapping.Layer(outDir+"/"+"fdr_r")                 # create a new layer
        arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")

        slope_layer = arcpy.mapping.Layer(outDir+"/"+ "slope_c")                # create a new layer
        arcpy.mapping.AddLayer(df, slope_layer ,"TOP")


    except Exception, e:
        print e
if __name__ == "__main__":
    step2_dem_processing(DEM, land_use, outDir, outlet_point_sf, threshold)

