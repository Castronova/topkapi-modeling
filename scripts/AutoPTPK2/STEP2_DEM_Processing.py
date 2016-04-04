import arcpy
from arcpy import env
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
'''

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True    # to overwrite

DEM = arcpy.GetParameterAsText(0)
land_use = arcpy.GetParameterAsText(1)
outDir= arcpy.GetParameterAsText(2)
outlet_point_sf = arcpy.GetParameterAsText(3)
threshold = arcpy.GetParameterAsText(4)
# outlet_point_sf = arcpy.GetParameterAsText(5)         # Outlet point for the catchment

def step2_dem_processing(DEM, land_use, outDir, outlet_point_sf, threshold):
    '''

    :param DEM: Projected DEM (for now, projected to UTM zone 12)
    :param land_use: Projected Land_use raster from NLCD
    :param outDir: geodatabase where the rasters created are stored
    :param outlet_point_sf: the point shapefile for the outlet point
    :param threshold: Threshold for defining stream
    :return:
    '''

    if threshold == "": threshold = "3000"     # is a source of bug, if the cell size is big but this is small

    # Set workspace environment
    arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir
    # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
    arcpy.env.snapRaster = DEM              # Set Snap Raster environment

    fill = "fel"  #fill
    fdr =  'fdr'
    fac = 'fac'
    strlnk = 'strlnk'
    str = 'str'
    strc = 'strc'
    slope = 'slope'
    Catchment = 'Catchment'
    DrainageLine_shp = 'DrainageLine'
    CatchPoly_shp =  'CatchPoly'
    CatchPolyDissolve_shp = 'CatchPolyDissolve'
    STRAHLER = "STRAHLER"
    Outlet = "Outlet"
    mask = "mask"

    # arcpy.gp.Fill_sa(DEM, fill, "")
    # arcpy.gp.FlowDirection_sa(fill, fdr, "NORMAL", slope)
    # arcpy.gp.FlowAccumulation_sa(fdr, fac, "", "FLOAT")
    # arcpy.gp.RasterCalculator_sa('"fac" > ' + threshold, str)
    # arcpy.gp.ExtractByMask_sa(str, Basin, strc)
    # arcpy.gp.StreamLink_sa(strc, fdr, strlnk)
    # arcpy.gp.StreamToFeature_sa(strlnk, fdr, DrainageLine_shp, "NO_SIMPLIFY")

    # arcpy.gp.Watershed_sa(fdr, strlnk, Catchment, "VALUE")
    # arcpy.RasterToPolygon_conversion(Catchment, CatchPoly_shp, "NO_SIMPLIFY", "VALUE")
    # arcpy.Dissolve_management(CatchPoly_shp, CatchPolyDissolve_shp, "GRIDCODE", "", "MULTI_PART", "DISSOLVE_LINES")


    #-------------------------dt code---------------------------------
    # outFill = Fill(DEM) ;                                   outFill.save(fill)  ;                   print "Fill Done"        #the result is in memory
    # outFlowDirection = FlowDirection(fill) ;               outFlowDirection.save(fdr)
    # outFlowAccumulation = FlowAccumulation(fdr);            outFlowAccumulation.save(fac) ;           print "fac"
    # arcpy.gp.FlowDirection_sa(fill, fdr, "NORMAL", slope)
    # outSnapPour = SnapPourPoint(outlet_point_sf, fac, 100,"OBJECTID"); outSnapPour.save(Outlet) ;                 print "snappoint done"   #snap the outlet_point_sfpoint from outlet_point_sf to fac, within a distance of 50m #saves it as a raster
    # outWatershed = Watershed(fdr, Outlet);                  outWatershed.save(mask)
    # StreamRaster = (Raster(fac) >= float(threshold)) & (Raster(mask) >= 0) ; StreamRaster.save(str);   print "StreamNet done"  #to define stream only upstream of the outlet
    # outStreamLink = StreamLink(str,fdr) ;                   outStreamLink.save(strlnk)
    # Catchment = Watershed(fdr, strlnk);                     Catchment.save("catchment")         # we do not need catchment though, mask is good for us
    # StreamToFeature(strlnk, fdr, "Streamnet","NO_SIMPLIFY")                                                               #stream defined
    # arcpy.RasterToPolygon_conversion("catchment", "CatchTemp", "NO_SIMPLIFY")
    # arcpy.Dissolve_management("catchtemp", "CatchPoly", "GRIDCODE")                                                            #dissolves extra catchments
    # arcpy.Dissolve_management(in_features=outDir+"/catchtemp", out_feature_class="C:/Users/Prasanna/Box Sync/Test Wshed Point GDB/CatchPoly.shp", dissolve_field="GRIDCODE", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    # print "Catchment Dissolved"


    #trial
    Fill(DEM).save(fill)
    FlowDirection(fill).save(fdr)
    FlowAccumulation(fdr).save(fac)
    Slope(fill, "DEGREE", "1").save(slope)
    #arcpy.gp.Slope_sa(fill, slope, "DEGREE", "1")
    FlowDirection(fill, "NORMAL",slope).save(fdr)
    SnapPourPoint(outlet_point_sf, fac, 100,"OBJECTID").save(Outlet)
    Watershed(fdr, Outlet).save(mask)
    StreamRaster = (Raster(fac) >= float(threshold)) & (Raster(mask) >= 0) ; StreamRaster.save(str)



    arcpy.AddMessage("********** Fdr, Fac, Stream processing complete **********")

    #clip to the mask--------------------------------------------------------
    arcpy.gp.ExtractByMask_sa(str, mask, str+"_c")
    arcpy.gp.ExtractByMask_sa(fdr, mask, fdr+"_c")
    arcpy.gp.ExtractByMask_sa(slope, mask, slope+"_c")
    arcpy.gp.ExtractByMask_sa(fill, mask, DEM+"_fc")      # f for fill, c for clip
    arcpy.gp.ExtractByMask_sa(land_use, mask, land_use+"_c")

    # after clipping, we only use clipped files
    land_use = land_use +"_c"
    str = str +"_c"
    fdr = fdr +"_c"
    slope = slope +"_c"
    SD = "SD_c"    # c for consistency in naming

    #strahler for mannings for channel
    arcpy.gp.StreamOrder_sa(str, fdr, STRAHLER, "STRAHLER")  # the last parameter, Strahler string, is actually a method of ordering stream. NOT A NAME
    arcpy.AddMessage("********** Strahler stream order processing complete **********")

    arcpy.AddField_management(in_table= land_use , field_name="ManningsN", field_type="LONG",field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddMessage("********** Adding field to Land Use complete **********")


    # reclassification, as above, did not work. so, multiply Manning's n by 10,000. We will later divide it by 10,000 again
    arcpy.gp.Reclassify_sa(land_use, "Value", "11 0;21 404;22 678;23 678;24 404;31 113;41 3600;42 3200;43 4000;52 4000;71 3680;81 3250;82 3250;90 860;95 1825", outDir+"/nx10000_Overl", "DATA")
    arcpy.AddMessage("********** Land Use reclassification to obtain Mannings n complete **********")

    # reclassifying Strahler order to get Manning's for channel in the same way
    arcpy.gp.Reclassify_sa("STRAHLER", "Value", "1 500;2 400;3 350;4 300;5 300;6 250", outDir+"/nx10000_Chan", "DATA")
    arcpy.AddMessage("********** Strahler order raster reclassification to obtain Mannings n complete **********")

    # now, NLCD to n calculate the real Manning's, divide reclassified raster by 10,000
    arcpy.gp.RasterCalculator_sa(""""nx10000_Overl" /10000.0""", outDir+"/n_Overland")
    arcpy.gp.RasterCalculator_sa(""""nx10000_Chan" /10000.0""", outDir+"/n_Channel")

    arcpy.AddMessage("########## DEM processing complete ##########")



    #REclassify to change no data to -9999
    arcpy.gp.Reclassify_sa(fdr, "Value", "1 1;2 2;4 4;8 8;16 16;32 32;64 64;128 128;NODATA -9999", fdr+"_r", "DATA")
    arcpy.gp.Reclassify_sa(str, "Value", "0 0;1 1;NODATA -9999", str + "_r", "DATA")
    arcpy.gp.Reclassify_sa(mask, "Value", "2 1", mask + "_r", "DATA")
    # arcpy.gp.RasterCalculator_sa(""""mask_c"+.5""", SD)                                                    #creating soil depth raster, len = 1.5
    arcpy.AddMessage("########## Assigning -9999 to NoData, mask and Soil depth creation  completed ##########")


    # after reclassifying
    str = str +"_r"
    fdr = fdr +"_r"
    mask = mask + "_r"
    DEM = DEM+"_fc"

    # Add n_Channel and n_Overland to layer and then to map document
    mxd = arcpy.mapping.MapDocument("CURRENT")                      # get the map document
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                   # first data-frame in the document
    try:
        fdr_layer = arcpy.mapping.Layer(outDir+"/"+ mask)                 # create a new layer
        arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")

        fdr_layer = arcpy.mapping.Layer(outDir+"/"+ DEM )                 # create a new layer
        arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")

        # n_Channel_layer = arcpy.mapping.Layer(outDir+"/n_Channel")      # create a new layer
        # arcpy.mapping.AddLayer(df, n_Channel_layer ,"TOP")

        n_Overland_layer = arcpy.mapping.Layer(outDir+"/n_Overland")    # create a new layer
        arcpy.mapping.AddLayer(df, n_Overland_layer,"TOP")

        fdr_layer = arcpy.mapping.Layer(outDir+"/"+fdr)                 # create a new layer
        arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")

        slope_layer = arcpy.mapping.Layer(outDir+"/"+ slope)                # create a new layer
        arcpy.mapping.AddLayer(df, slope_layer ,"TOP")
    except Exception, e:
        print e
if __name__ == "__main__":
    step2_dem_processing(DEM, land_use, outDir, outlet_point_sf, threshold)

