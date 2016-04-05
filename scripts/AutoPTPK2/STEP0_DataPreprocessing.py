import os
import sys
import arcpy
from arcpy import env
from arcpy.sa import *
from STEP1_Get_DEM_LANDUSE import step1_get_dem_landuse
from STEP2_DEM_Processing import step2_dem_processing
# from STEP3_Merge_SSURGO import step3_merge_ssurgo
from STEP4_Join_mukey_Feature_to_Raster import step4_join_mukey_feature2raster
from STEP5_Rasters_2_TIFFs import step5_convert_rasters_to_tiff

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

inUsername = arcpy.GetParameterAsText(0)
inPassword = arcpy.GetParameterAsText(1)
outDir = arcpy.GetParameterAsText(2)           # RAW FILES
wshedBoundary = arcpy.GetParameterAsText(3)    # Bounding Box
bufferDi= arcpy.GetParameterAsText(4)
cell_size = arcpy.GetParameterAsText(5)
outlet_point_sf = arcpy.GetParameterAsText(6)   # boundary
threshold = arcpy.GetParameterAsText(7)        # Threshold for defining stream
path2ssurgoFolders = arcpy.GetParameterAsText(8)
# shapefile_fieldAdded = arcpy.GetParameterAsText(10)
# DEM, Landuse, .... [user input files, not downloaded]

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir

# list of empty directories to be made
folders_to_create = ['DEM_processed_rasters', 'SSURGO_rasters', 'TIFFS']

# Out Directories
raw_files_outDir = os.path.join(outDir, "Raw_files.gdb")
DEM_processed_outDir = os.path.join(outDir, folders_to_create[0])
ssurgo_outDir = os.path.join(outDir,folders_to_create[1])
tiffs_outDir = os.path.join(outDir, folders_to_create[2])

# make the empty directories
try:
    for folder in folders_to_create:
        directory = os.path.join(outDir,folder)
        if not os.path.exists(directory):
            os.makedirs(directory)
        arcpy.CreateFileGDB_management(outDir, "Raw_files.gdb")

except Exception, e:
    print e



# Step1, download the data
step1_get_dem_landuse(inUsername,inPassword,raw_files_outDir,wshedBoundary,bufferDi,cell_size)

# Step2
DEM = os.path.join(raw_files_outDir, "DEM_Prj")
land_use = os.path.join(raw_files_outDir, "Land_Use_Prj")
step2_dem_processing(DEM, land_use ,raw_files_outDir , outlet_point_sf, threshold)

# Step4
MatchRaster = os.path.join(raw_files_outDir, "DEM_Prj_fc")
step4_join_mukey_feature2raster(path2ssurgoFolders,ssurgo_outDir ,MatchRaster )

# Step 5
step5_convert_rasters_to_tiff(ssurgo_outDir, raw_files_outDir ,tiffs_outDir)



# step1_get_dem_landuse(inUsername,inPassword,raw_files_outDir,wshedBoundary,bufferDi,cell_size)
# DEM = os.path.join(raw_files_outDir, "DEM_Prj")
# land_use = os.path.join(raw_files_outDir, "Land_Use_Prj")
# step2_dem_processing(DEM, land_use ,raw_files_outDir , outlet_point_sf, threshold)
# MatchRaster = os.path.join(raw_files_outDir, "DEM_Prj_fc")
# step4_join_mukey_feature2raster(path2ssurgoFolders,ssurgo_outDir ,MatchRaster )
# step5_convert_rasters_to_tiff(ssurgo_outDir, tiffs_outDir)






































# # if calling functions do not work
# def step1_download_dem_landuse( inUsername, inPassword, outDir, bounding_box, wshedBoundary, bufferDi, cell_size):
#     '''
#     Future Improvements:
#     Buffer distance and cell size default values
#     Use of arcpy.SpatialReference("UTM..") once to avoid repeated projection
#     User defined Projection
#     Folder and personal gdb naming convention. And their automatic creation
#     What boundary to use to clip the resulting rasters
#
#     Untested:
#     User defined resolution
#     Creating folders, and personal gdb
#     '''
#
#     #defaulted, to make things easier
#     if inUsername == "": inUsername = "prasanna_usu"
#     if inPassword  == "": inPassword = "Hydrology12!@"
#     if bufferDi == "":
#         if cell_size == "":
#             bufferDi = 100
#         else:
#             bufferDi = float(cell_size) * 3
#
#     # Set workspace environment
#     arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir
#     #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(102008)
#     #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
#
#
#     Boundary = "Boundary"
#
#     # Add Data to Geodatabase
#     arcpy.FeatureClassToFeatureClass_conversion(wshedBoundary, outDir, Boundary)  # to convert feature to feature class (as contained in geodatabase)
#     arcpy.MakeFeatureLayer_management(Boundary, Boundary)                         # creates temporary layer
#
#
#     # Buffer
#     arcpy.Buffer_analysis(Boundary, "Buffer", str(bufferDi)+" Meters", "FULL", "ROUND", "NONE", "", "PLANAR")
#     arcpy.MakeFeatureLayer_management("Buffer", "Buffer")                        #creates temporary layer
#
#     # Connect to ArcGIS Servers
#     out_folder_path = 'GIS Servers'
#
#     out_landscape = 'Landscape.ags'
#     server_landscape = 'https://landscape5.arcgis.com:443/arcgis/services/'
#
#     out_elevation = 'Elevation.ags'
#     server_elevation = 'https://elevation.arcgis.com:443/arcgis/services/'
#
#     arcpy.mapping.CreateGISServerConnectionFile("USE_GIS_SERVICES",
#                                                     out_folder_path,
#                                                     out_landscape,
#                                                     server_landscape,
#                                                     "ARCGIS_SERVER",
#                                                     username=inUsername,
#                                                     password=inPassword,
#                                                     save_username_password=True)
#
#     arcpy.mapping.CreateGISServerConnectionFile("USE_GIS_SERVICES",
#                                                     out_folder_path,
#                                                     out_elevation,
#                                                     server_elevation,
#                                                     "ARCGIS_SERVER",
#                                                     username=inUsername,
#                                                     password=inPassword,
#                                                     save_username_password=True)
#
#
#     # Extract Image Server Data
#     """ DEM, 30m NED """
#     NED30m_ImageServer = "GIS Servers\\Elevation\\NED30m.ImageServer"
#     arcpy.MakeImageServerLayer_management(NED30m_ImageServer, "NED30m_Layer")
#     arcpy.gp.ExtractByMask_sa("NED30m_Layer", "Buffer", "DEM")
#
#     arcpy.env.snapRaster = "DEM"                                              # Set Snap Raster environment
#
#     """ Land Use """
#     NLCD_ImageServer = "GIS Servers\\Landscape\\USA_NLCD_2011.ImageServer"
#     arcpy.MakeImageServerLayer_management(NLCD_ImageServer,"NLCD_Layer")
#     arcpy.gp.ExtractByMask_sa("NLCD_Layer", "DEM", "Land_Use")
#
#     arcpy.AddMessage("************DEM and Land Use data, i.e. NLCD , download complete************")
#
#
#
#
#     """ Project DEM to UTM """
#     arcpy.ProjectRaster_management(in_raster="DEM", out_raster="DEM_Prj", out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", resampling_type="NEAREST", cell_size="30.922080775934 30.922080775934", geographic_transform="WGS_1984_(ITRF00)_To_NAD_1983", Registration_Point="", in_coor_system="PROJCS['North_America_Albers_Equal_Area_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]")
#
#     """ Project Land Use to UTM """
#     arcpy.ProjectRaster_management(in_raster="Land_Use", out_raster="Land_Use_Prj", out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", resampling_type="NEAREST", cell_size="30.922080775934 30.922080775934", geographic_transform="WGS_1984_(ITRF00)_To_NAD_1983", Registration_Point="", in_coor_system="PROJCS['North_America_Albers_Equal_Area_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]")
#
#     arcpy.AddMessage("************DEM and Land Use file projected to UTM************")
#
#     #put DEM and Land_Use on maps as a layer
#     mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
#     df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               #first dataframe in the document
#
#     #if cell size given, need to resample here
#     if cell_size != "":
#         """ resample to the user specified resolution """
#         arcpy.Resample_management(in_raster= "DEM_Prj",
#                                   out_raster= "DEM_Prj",
#                                   cell_size= str(cell_size)+" "+str(cell_size), resampling_type="NEAREST")
#
#         arcpy.Resample_management(in_raster= "Land_Use_Prj",
#                                   out_raster= "Land_Use_Prj",
#                                   cell_size=str(cell_size)+" "+str(cell_size), resampling_type="NEAREST")
#
#         arcpy.AddMessage("************Resample DEM and Land Use with cell size %s m completed ************"%cell_size)
#         DEM_layer = arcpy.mapping.Layer(outDir+"/DEM_Prj")    # create a new layer
#         arcpy.mapping.AddLayer(df, DEM_layer,"TOP")
#
#         LandUse_layer = arcpy.mapping.Layer(outDir+"/Land_Use_Prj")    # create a new layer
#         arcpy.mapping.AddLayer(df, LandUse_layer,"TOP")
#
#
#     DEM_layer = arcpy.mapping.Layer(outDir+"/DEM_Prj")    # create a new layer
#     arcpy.mapping.AddLayer(df, DEM_layer,"TOP")
#
#     LandUse_layer = arcpy.mapping.Layer(outDir+"/Land_Use_Prj")    # create a new layer
#     arcpy.mapping.AddLayer(df, LandUse_layer,"TOP")
#
#     Buffer_layer = arcpy.mapping.Layer(outDir+"/Buffer")    # create a new layer
#     arcpy.mapping.AddLayer(df, Buffer_layer,"TOP")
#
# # STEP 2 --------------------------------------------------------------------------------------------------------------
# def step2_dem_processing(dem, landuse, outDir, outlet, threshold):
#
#     '''
#     Issues:
#     If output is folder, dissolve (around line 77 ) does not work
#     Improvements
#     Full path may not be required when we hae assigned workspace
#     Default Threshold of flow accumulation
#     Clipping / extracting by a mask
#     Soil depth is in string
#
#     Snapped gage/outlet needs to be created as a seperated point shapefile
#     Also, confusion on why mask has value=2 and not 1
#     '''
#
#     if threshold == "": threshold = "3000"     # is a source of bug, if the cell size is big but this is small
#
#     # Set workspace environment
#     arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir
#     # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
#     arcpy.env.snapRaster = DEM              # Set Snap Raster environment
#
#     fill = "fel"  #fill
#     fdr =  'fdr'
#     fac = 'fac'
#     strlnk = 'strlnk'
#     str = 'str'
#     strc = 'strc'
#     slope = 'slope'
#     Catchment = 'Catchment'
#     DrainageLine_shp = 'DrainageLine'
#     CatchPoly_shp =  'CatchPoly'
#     CatchPolyDissolve_shp = 'CatchPolyDissolve'
#     STRAHLER = "STRAHLER"
#     Outlet = "Outlet"
#     mask = "mask"
#
#
#
#     #trial
#     Fill(DEM).save(fill)
#     FlowDirection(fill).save(fdr)
#     FlowAccumulation(fdr).save(fac)
#     Slope(fill, "DEGREE", "1").save(slope)
#     #arcpy.gp.Slope_sa(fill, slope, "DEGREE", "1")
#     FlowDirection(fill, "NORMAL",slope).save(fdr)
#     SnapPourPoint(gage, fac, 100,"OBJECTID").save(Outlet)
#     Watershed(fdr, Outlet).save(mask)
#     StreamRaster = (Raster(fac) >= float(threshold)) & (Raster(mask) >= 0) ; StreamRaster.save(str)
#
#
#
#     arcpy.AddMessage("********** Fdr, Fac, Stream processing complete **********")
#
#     #clip to the mask--------------------------------------------------------
#     arcpy.gp.ExtractByMask_sa(str, mask, str+"_c")
#     arcpy.gp.ExtractByMask_sa(fdr, mask, fdr+"_c")
#     arcpy.gp.ExtractByMask_sa(slope, mask, slope+"_c")
#     arcpy.gp.ExtractByMask_sa(fill, mask, DEM+"_fc")      # f for fill, c for clip
#     arcpy.gp.ExtractByMask_sa(land_use, mask, land_use+"_c")
#
#     # after clipping, we only use clipped files
#     land_use = land_use +"_c"
#     str = str +"_c"
#     fdr = fdr +"_c"
#     slope = slope +"_c"
#     SD = "SD_c"    # c for consistency in naming
#
#     #strahler for mannings for channel
#     arcpy.gp.StreamOrder_sa(str, fdr, STRAHLER, "STRAHLER")  # the last parameter, Strahler string, is actually a method of ordering stream. NOT A NAME
#     arcpy.AddMessage("********** Strahler stream order processing complete **********")
#
#     arcpy.AddField_management(in_table= land_use , field_name="ManningsN", field_type="LONG",field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
#     arcpy.AddMessage("********** Adding field to Land Use complete **********")
#
#
#     # reclassification, as above, did not work. so, multiply Manning's n by 10,000. We will later divide it by 10,000 again
#     arcpy.gp.Reclassify_sa(land_use, "Value", "11 0;21 404;22 678;23 678;24 404;31 113;41 3600;42 3200;43 4000;52 4000;71 3680;81 3250;82 3250;90 860;95 1825", outDir+"/nx10000_Overl", "DATA")
#     arcpy.AddMessage("********** Land Use reclassification to obtain Mannings n complete **********")
#
#     # reclassifying Strahler order to get Manning's for channel in the same way
#     arcpy.gp.Reclassify_sa("STRAHLER", "Value", "1 500;2 400;3 350;4 300;5 300;6 250", outDir+"/nx10000_Chan", "DATA")
#     arcpy.AddMessage("********** Strahler order raster reclassification to obtain Mannings n complete **********")
#
#     # now, NLCD to n calculate the real Manning's, divide reclassified raster by 10,000
#     arcpy.gp.RasterCalculator_sa(""""nx10000_Overl" /10000.0""", outDir+"/n_Overland")
#     arcpy.gp.RasterCalculator_sa(""""nx10000_Chan" /10000.0""", outDir+"/n_Channel")
#
#     arcpy.AddMessage("########## DEM processing complete ##########")
#
#
#
#     #REclassify to change no data to -9999
#     arcpy.gp.Reclassify_sa(fdr, "Value", "1 1;2 2;4 4;8 8;16 16;32 32;64 64;128 128;NODATA -9999", fdr+"_r", "DATA")
#     arcpy.gp.Reclassify_sa(str, "Value", "0 0;1 1;NODATA -9999", str + "_r", "DATA")
#     arcpy.gp.Reclassify_sa(mask, "Value", "2 1", mask + "_r", "DATA")
#     # arcpy.gp.RasterCalculator_sa(""""mask_c"+.5""", SD)                                                    #creating soil depth raster, len = 1.5
#     arcpy.AddMessage("########## Assigning -9999 to NoData, mask and Soil depth creation  completed ##########")
#
#
#     # after reclassifying
#     str = str +"_r"
#     fdr = fdr +"_r"
#     mask = mask + "_r"
#     DEM = DEM+"_fc"
#
#     # Add n_Channel and n_Overland to layer and then to map document
#     mxd = arcpy.mapping.MapDocument("CURRENT")                      # get the map document
#     df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                   # first data-frame in the document
#
#     fdr_layer = arcpy.mapping.Layer(outDir+"/"+ mask)                 # create a new layer
#     arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")
#
#     fdr_layer = arcpy.mapping.Layer(outDir+"/"+ DEM )                 # create a new layer
#     arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")
#
#     # n_Channel_layer = arcpy.mapping.Layer(outDir+"/n_Channel")      # create a new layer
#     # arcpy.mapping.AddLayer(df, n_Channel_layer ,"TOP")
#
#     n_Overland_layer = arcpy.mapping.Layer(outDir+"/n_Overland")    # create a new layer
#     arcpy.mapping.AddLayer(df, n_Overland_layer,"TOP")
#
#     fdr_layer = arcpy.mapping.Layer(outDir+"/"+fdr)                 # create a new layer
#     arcpy.mapping.AddLayer(df, fdr_layer ,"TOP")
#
#     slope_layer = arcpy.mapping.Layer(outDir+"/"+ slope)                # create a new layer
#     arcpy.mapping.AddLayer(df, slope_layer ,"TOP")
#
# # STEP 4---------------------------------------------------------------------------------------------------------------
# def step4_ssurgo_feature_to_raster(path2ssurgoFolders,outDir,MatchDEM):
#
#     '''
#     Jan 28
#     this program is supposed to take ssurgo datafolder path as input
#     and attach to soilmu_a_xxx the table combined for MUKEY earlier
#
#     Limitations:
#     you have to open the spatial soilmu_a_xxxx file for it to work
#     if/when ssurgo replaces its folder and file naming convention, it wont work
#     ---------------------
#     Improvements:
#     User defined coordinate system
#     Converting to TIFs
#     Soil_properties may be repeated
#     Fixed folder names, but flexible enough to allow users to slit different steps
#     User feedback during processes, including percentage perhaps
#     Tabs are not spaced appropriately
#     Loading Layers into dataframe
#     Names of variables, ksat etc. could also be flexible
#     '''
#
#     arcpy.AddMessage("This script joins ssurgo derived data and export to rasters")
#
#     # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")
#     arcpy.env.snapRaster = MatchDEM                                             # Set Snap Raster environment
#
#     mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
#     df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               # first data-frame in the document
#
#     # create a list of folders containing SSURGO folders only
#     folderList = []
#     [folderList.append(folders) for folders in os.listdir(path2ssurgoFolders)
#         if os.path.isdir(os.path.join(path2ssurgoFolders, folders))]
#
#     # Each ssurgo folder, one at a time
#     for folder in folderList:
#
#         path2ssurgo= path2ssurgoFolders + "/" + folder
#         path2tabular = path2ssurgo+"/tabular"
#         path2Spatial= path2ssurgo+"/spatial"
#         arcpy.env.workspace = arcpy.env.scratchWorkspace = path2ssurgo
#
#         muShapefile = os.listdir(path2Spatial)[1].split('.')[0]                             #muShapefile = 'soilmu_a_ut612'
#         arcpy.AddMessage("### ***'%s'***  shapefile found was " %muShapefile)
#
#         #project the shapefile in ssurgo table, FILE SELECTION
#         arcpy.Project_management(in_dataset=path2ssurgo+"/spatial/" + muShapefile +".shp",
#                                  out_dataset=outDir + "/"+ muShapefile +"_prj",
#                                  out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="")
#         arcpy.AddMessage("### Shapefile projected ###")
#
#         # to add the projected shapefile from ssurgo, as a layer to the map at the bottom of the TOC in data frame 0
#         muShapefileAsLayer = muShapefile +"_prj"
#
#         layer1 = arcpy.mapping.Layer(outDir + "/"+ muShapefileAsLayer+ ".shp" ) # create a new layer
#         arcpy.mapping.AddLayer(df, layer1,"TOP")             #added to layer because this will be used code below
#
#
#         try:
#          # join the table that had mUKEY mapped to all soil properties
#          arcpy.AddJoin_management(muShapefileAsLayer, "MUKEY", path2ssurgo+"/MUKEY-Vs-Values.csv", "MUKEY")
#          arcpy.AddMessage("Field Successfully added")
#
#          #NAMING CONVENTION: -s for ssurgo, and -t for lookup table
#          soilProperties = [["ksat_r_WtAvg", "KSAT-s_"+folder ],
#                            ["Ks_WtAvg", "KSAT-t_"+folder ],
#                            ["ResidualWaterContent_WtAvg", "RSM-t_"+folder ],
#                            ["Porosity_WtAvg","POR-t_"+folder ],
#                            ["EffectivePorosity_WtAvg","EFPO-t_" +folder ] ,
#                            ["BubblingPressure_Geometric_WtAvg", "BBL-t_"+folder ] ,
#                            ["PoreSizeDistribution_geometric_WtAvg_y","PSD-t_"+folder]
#                            ]
#
#
#          #soilProperties = [[ "ksat_r_WtAvg", "Ksat-s_UT612" ], ["Ks_WtAvg", "Ksat-t_ut612" ], .... ]
#          for a_soil_property in soilProperties:
#
#              '''
#              covert from features to rasters
#              take first element of a_soil_property to find values in joint table,
#              and second element to name the raster
#              '''
#
#              firstNameOfSoilProperty = a_soil_property[1].split('_')[0]                 #e.g. Ksat-s, Bblpr-t, PoreSz-t etc.
#
#              if not os.path.exists(outDir+"/"+firstNameOfSoilProperty):
#                  dir4eachRaster = outDir+"/"+firstNameOfSoilProperty
#                  os.makedirs(dir4eachRaster)
#                  arcpy.AddMessage("' %s' *** , made "%dir4eachRaster )
#
#              try:
#
#                  tempOutputRasterFullpath = outDir+"/"+firstNameOfSoilProperty+"/"+ firstNameOfSoilProperty+ "_"+folder
#
#                  arcpy.FeatureToRaster_conversion(in_features=muShapefileAsLayer,
#                                                   field="MUKEY-Vs-Values.csv." + a_soil_property[0] ,
#                                                   out_raster= tempOutputRasterFullpath   , cell_size= MatchDEM  )
#
#                  arcpy.gp.ExtractByMask_sa(tempOutputRasterFullpath, MatchDEM, tempOutputRasterFullpath+"X")       #c=clipped
#
#                  # to clip the rasters to the consistent extent, so that their (nrows x ncol) matches
#                  arcpy.Clip_management(in_raster=tempOutputRasterFullpath+"X",
#                           out_raster= tempOutputRasterFullpath+"c" , in_template_dataset=MatchDEM, nodata_value="-9999",
#                           clipping_geometry="NONE", maintain_clipping_extent="MAINTAIN_EXTENT")
#
#                  arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%sc'"%tempOutputRasterFullpath,
#                                                       Output_Workspace=outDir, Raster_Format="TIFF")
#                  arcpy.AddMessage("Raster %sc created " %tempOutputRasterFullpath)
#
#                  #convert the raster to tif format
#                  #arcpy.RasterToOtherFormat_conversion(Input_Rasters=tempOutputRasterFullpath, Output_Workspace=outDir+"/"+firstNameOfSoilProperty , Raster_Format="TIFF")
#
#                  newRasterlayer = arcpy.mapping.Layer(tempOutputRasterFullpath+"c")    # create a new layer
#                  arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")
#
#              except Exception, e:
#                  arcpy.AddMessage("!!!!!!!!!!Error encouncered at line 114 :"+ str(e))
#
#          print "Folder done: ", folder
#         except Exception, e:
#          print "failed in folder ", folder
#
#
#     soilProperties = [ ["ksat_r_WtAvg", "KSAT-s_"+folder ],
#                        ["Ks_WtAvg", "KSAT-t_"+folder ],
#                        ["ResidualWaterContent_WtAvg", "RSM-t_"+folder ],
#                        ["Porosity_WtAvg","POR-t_"+folder ],
#                        ["EffectivePorosity_WtAvg","EFPO-t_" +folder ] ,
#                        ["BubblingPressure_Geometric_WtAvg", "BBL-t_"+folder ] ,
#                        ["PoreSizeDistribution_geometric_WtAvg_y","PSD-t_"+folder]
#                        ]
#
#     try:
#
#         #merge rasters present in outDir
#         FOLDERSOFRASTERS = [folder.split('_')[0] for folder in [list[1] for list  in soilProperties]]
#
#         for afolderOfRaster in FOLDERSOFRASTERS:
#             arcpy.env.workspace = outDir+"/"+afolderOfRaster
#             raster_list=arcpy.ListRasters("", "tif")
#             arcpy.CompositeBands_management(raster_list, outDir+"/"+afolderOfRaster+".tif") #will save output on the same folder
#
#             newRasterlayer = arcpy.mapping.Layer(outDir+"/"+afolderOfRaster +".tif")    # create a new layer
#             arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")
#
#     except Exception,e :
#         arcpy.AddMessage("!!!!!!!!!!Error in merging encouncered, at line 159 :"+ str(e))

