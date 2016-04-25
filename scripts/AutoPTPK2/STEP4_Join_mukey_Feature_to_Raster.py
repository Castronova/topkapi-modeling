import arcpy
from arcpy import env
import os

'''
Jan 28
this program is supposed to take ssurgo datafolder path as input
and attach to soilmu_a_xxx the table combined for MUKEY earlier

Limitations:
---------------------
you have to open the spatial soilmu_a_xxxx file for it to work
if/when ssurgo replaces its folder and file naming convention, it wont work

Improvements:
---------------------
User defined coordinate system
Converting to TIFs
Soil_properties may be repeated
Fixed folder names, but flexible enough to allow users to slit different steps
User feedback during processes, including percentage perhaps
Tabs are not spaced appropriately
Loading Layers into dataframe
Names of variables, ksat etc. could also be flexible
Important to clip the feature first, and then convert to raster. Because features likes STATSGO
    are likely to be very large
THE PROJECTION OF SSURGO POLYGON IS NOT IN USER INPUT CS

'''


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

path2ssurgoFolders = arcpy.GetParameterAsText(0)
outDir = arcpy.GetParameterAsText(1)                                       #output rasters and the projected polygon shapefile will be saved
MatchRaster = arcpy.GetParameterAsText(2)

def step4_join_mukey_feature2raster(path2ssurgoFolders,outDir,MatchRaster ):
    '''
    :param path2ssurgoFolders: The path to a folder containing the collection of SSURGO (or Statsgo) folders
    :param outDir: folder where the rasters created are stored
    :param MatchRaster: DEM or any raster whose extent, coordinate system are considered while creating SSURGO rasters
    :return:
    '''
    arcpy.AddMessage("This script joins ssurgo derived data and export to rasters")

    #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
    arcpy.env.snapRaster = MatchRaster                                             # Set Snap Raster environment

    mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               #first dataframe in the document


    # create a list of folders containing SSURGO folders only
    folderList = []
    [folderList.append(folders) for folders in os.listdir(path2ssurgoFolders)
        if os.path.isdir(os.path.join(path2ssurgoFolders, folders))]

    # Each ssurgo folder, one at a time
    for folder in folderList:

        path2ssurgo= path2ssurgoFolders + "/" + folder
        path2tabular = path2ssurgo+"/tabular"
        path2Spatial= path2ssurgo+"/spatial"
        arcpy.env.workspace =  path2ssurgo   # arcpy.env.scratchWorkspace =

        muShapefile = os.listdir(path2Spatial)[1].split('.')[0]                             #muShapefile = 'soilmu_a_ut612'
        arcpy.AddMessage("### ***'%s'***  shapefile found was " %muShapefile)

        #project the shapefile in ssurgo table, FILE SELECTION
        try:
            arcpy.Project_management(in_dataset=path2ssurgo+"/spatial/" + muShapefile +".shp",
                                 out_dataset=outDir + "/"+ muShapefile +"_prj",
                                 out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="")
            arcpy.AddMessage("### Shapefile projected ###")
        except Exception, e:
            print e
            arcpy.AddMessage("### Shapefile projection failed ###")


        # to add the projected shapefile from ssurgo, as a layer to the map at the bottom of the TOC in data frame 0
        muShapefileAsLayer = muShapefile +"_prj"

        layer1 = arcpy.mapping.Layer(outDir + "/"+ muShapefileAsLayer+ ".shp" ) # create a new layer
        arcpy.mapping.AddLayer(df, layer1,"TOP")             #added to layer because this will be used code below


        try:

         #join the table that had mUKEY mapped to all soil properties
         arcpy.AddJoin_management(muShapefileAsLayer, "MUKEY", path2ssurgo+"/MUKEY-Vs-Values.csv", "MUKEY")
         arcpy.AddMessage("Field Successfully added")


         #NAMING CONVENTION: -s for ssurgo, and -t for lookup table
         soilProperties = [["ksat_r_WtAvg", "KSAT-s_"+folder ],
                           ["Ks_WtAvg", "KSAT-t_"+folder ],
                           ["ResidualWaterContent_WtAvg", "RSM-t_"+folder ],
                           ["Porosity_WtAvg","POR-t_"+folder ],
                           ["EffectivePorosity_WtAvg","EFPO-t_" +folder ] ,
                           ["BubblingPressure_Geometric_WtAvg", "BBL-t_"+folder ] ,
                           ["PoreSizeDistribution_geometric_WtAvg_y","PSD-t_"+folder],
                           ["HydroGrp", "GRP_"+folder]
                           ]


         #soilProperties = [[ "ksat_r_WtAvg", "Ksat-s_UT612" ], ["Ks_WtAvg", "Ksat-t_ut612" ], .... ]
         for a_soil_property in soilProperties:


             '''
             covert from features to rasters
             take first element of a_soil_property to find values in joint table,
             and second element to name the raster
             '''

             firstNameOfSoilProperty = a_soil_property[1].split('_')[0]                 #e.g. Ksat-s, Bblpr-t, PoreSz-t etc.

             if not os.path.exists(outDir+"/"+firstNameOfSoilProperty):
                 dir4eachRaster = outDir+"/"+firstNameOfSoilProperty
                 os.makedirs(dir4eachRaster)
                 arcpy.AddMessage("' %s' *** , made "%dir4eachRaster )


             try:


                 tempOutputRasterFullpath = outDir+"/"+firstNameOfSoilProperty+"/"+ firstNameOfSoilProperty+ "_"+folder

                 arcpy.FeatureToRaster_conversion(in_features=muShapefileAsLayer,
                                                  field="MUKEY-Vs-Values.csv." + a_soil_property[0] ,
                                                  out_raster= tempOutputRasterFullpath   , cell_size= MatchRaster  )


                 arcpy.gp.ExtractByMask_sa(tempOutputRasterFullpath, MatchRaster, tempOutputRasterFullpath+"X")       #c=clipped

                 # to clip the rasters to the consistent extent, so that their (nrows x ncol) matches
                 arcpy.Clip_management(in_raster=tempOutputRasterFullpath+"X",
                          out_raster= tempOutputRasterFullpath+"c" , in_template_dataset=MatchRaster, nodata_value="-9999",
                          clipping_geometry="NONE", maintain_clipping_extent="MAINTAIN_EXTENT")

             except Exception, e:
                 arcpy.AddMessage("!!!!!!!!!!Error encouncered at line 114 :"+ str(e))

         print "Folder done: ", folder
        except Exception, e:
            print "failed in folder ", folder



    soilProperties = [ ["ksat_r_WtAvg", "KSAT-s_"+folder ],
                       ["Ks_WtAvg", "KSAT-t_"+folder ],
                       ["ResidualWaterContent_WtAvg", "RSM-t_"+folder ],
                       ["Porosity_WtAvg","POR-t_"+folder ],
                       ["EffectivePorosity_WtAvg","EFPO-t_" +folder ] ,
                       ["BubblingPressure_Geometric_WtAvg", "BBL-t_"+folder ] ,
                       ["PoreSizeDistribution_geometric_WtAvg_y","PSD-t_"+folder]
                       ]

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


if __name__ == "__main__":
    step4_join_mukey_feature2raster(path2ssurgoFolders,outDir,MatchRaster )





































#
#
#
#
#
# import arcpy
# from arcpy import env
# import os
#
# #this program is supposed to take ssurgo datafolder path as input and attach to soil_mu_xxx the table combined for MUKEY earlier
# #one limitation, you have to open the spatial soilmu_a_xxxx file for it to work
#
#
# arcpy.env.overwriteOutput = True
# arcpy.CheckOutExtension("Spatial")
#
# path2ssurgoFolders = arcpy.GetParameterAsText(0)
# outDir = arcpy.GetParameterAsText(1)     #this is where the output rasters and the projected polygon shapefile will be saved
# cellSize = arcpy.GetParameterAsText(2)
#
# arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(102008)
#
# mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
# df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               #first dataframe in the document
#
# #create a list of folders only
# folderList = []
# [folderList.append(folders) for folders in os.listdir(path2ssurgoFolders)
#     if os.path.isdir(os.path.join(path2ssurgoFolders, folders))]
#
# folderList = folderList
# for folder in folderList:
#     path2ssurgo= path2ssurgoFolders + "/" + folder
#     path2tabular = path2ssurgo+"/tabular"
#     path2Spatial= path2ssurgo+"/spatial"
#     arcpy.env.workspace = arcpy.env.scratchWorkspace = path2ssurgo
#
#     muShapefile = os.listdir(path2Spatial)[1].split('.')[0]
#
#     #project the shapefile in ssurgo table
#     arcpy.Project_management(in_dataset= path2ssurgo+"/spatial/" + muShapefile +".shp" , out_dataset=outDir + "/"+ muShapefile +"_prj", out_coor_system="PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="WGS_1984_(ITRF00)_To_NAD_1983", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="")
#
#     # to add the projected shapefile from ssurgo, as a layer to the map at the bottom of the TOC in data frame 0
#     muShapefileAsLayer = muShapefile +"_prj"
#     newlayer = arcpy.mapping.Layer(outDir + "/"+ muShapefileAsLayer + ".shp" )    # create a new layer
#     arcpy.mapping.AddLayer(df, newlayer,"BOTTOM")   #added to layer because this will be used code below
#
#
#     try:
#         #join the table that had mUKEY mapped to all soil properties
#         arcpy.AddJoin_management(muShapefileAsLayer, "MUKEY", path2ssurgo+"/MUKEY-Vs-Values.csv", "MUKEY")
#
#         #ssr for ssurgo, and tbl for lookup table
#
#         soilProperties = [["ksat_r_WtAvg", "Ksat-s_"+folder ],
#                           ["Ks_WtAvg", "Ksat-t_"+folder ],
#                           ["Porosity_WtAvg","Por-t_"+folder ],
#                           ["EffectivePorosity_WtAvg","EfPor-t_" +folder ] ,
#                           ["BubblingPressure_Geometric_WtAvg", "BblPr-t_"+folder ] ,
#                           ["PoreSizeDistribution_geometric_WtAvg_y","PoreSz-t_"+folder]
#                           ]
#
#         #soilProperties = [[ "ksat_r_WtAvg", "Ksat_ssur" ], ["Ks_WtAvg", "Ksat_tbl" ], ["dbthirdbar_r_WtAvg","dbthirdbar_ssur"  ] ]
#         for a_soil_property in soilProperties:
#             #covert from features to rasters
#             #take first element of a_soil_property to find values in joint table, and second element to name the raster
#
#             firstNameOfSoilProperty = a_soil_property[1].split('_')[0]    #example Ksat_s, Bblpr_t, PoreSz-t etc.
#             if not os.path.exists(outDir+"/"+firstNameOfSoilProperty):
#                 dir4eachRaster = outDir+"/"+firstNameOfSoilProperty
#                 os.makedirs(dir4eachRaster)
#             try:
#                 tempOutputRasterFullpath = outDir+"/"+firstNameOfSoilProperty+"/"+ firstNameOfSoilProperty+ "_"+folder
#                 arcpy.FeatureToRaster_conversion(in_features=muShapefileAsLayer,    field="MUKEY-Vs-Values.csv." + a_soil_property[0]    ,
#                                                  out_raster= tempOutputRasterFullpath   , cell_size= cellSize )   #   ""2.71097365691884E-03")
#
#                 arcpy.RasterToOtherFormat_conversion(Input_Rasters=tempOutputRasterFullpath, Output_Workspace=outDir+"/"+firstNameOfSoilProperty , Raster_Format="TIFF")
#
#                 # newRasterlayer = arcpy.mapping.Layer(outDir+"/"+firstNameOfSoilProperty+"/"+ firstNameOfSoilProperty+".tif")    # create a new layer
#                 # arcpy.mapping.AddLayer(df, newRasterlayer,"BOTTOM")
#
#
#
#             except Exception, e:
#                 print e
#
#         print "Folder done: ", folder
#     except Exception, e:
#         print "failed in folder ", folder
#
#
#
#
# try:
#     #merge rasters present in outDir
#     FOLDERSOFRASTERS = [folder.split('_')[0] for folder in [list[1] for list  in soilProperties]]
#     for afolderOfRaster in FOLDERSOFRASTERS:
#         arcpy.env.workspace = outDir+"/"+afolderOfRaster
#         raster_list=arcpy.ListRasters("", "tif")
#         arcpy.CompositeBands_management(raster_list, outDir+"/"+afolderOfRaster+".tif") #will save output on the same folder
#
#         newRasterlayer = arcpy.mapping.Layer(outDir+"/"+afolderOfRaster +".tif")    # create a new layer
#         arcpy.mapping.AddLayer(df, newRasterlayer,"BOTTOM")
#
# except Exception,e :
#     print e
#
#
#
