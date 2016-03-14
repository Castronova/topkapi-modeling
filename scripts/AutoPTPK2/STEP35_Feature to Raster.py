import arcpy
from arcpy import env
import os

'''
To convert the file once the field has been added
'''


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

path2ssurgoFolders = arcpy.GetParameterAsText(0)
outDir = arcpy.GetParameterAsText(1)                                       #output rasters and the projected polygon shapefile will be saved
MatchDEM = arcpy.GetParameterAsText(2)


#NAMING CONVENTION: -s for ssurgo, and -t for lookup table
soilProperties = [["ksat_r_WtAvg", "KSAT-s_"+folder ],
               ["Ks_WtAvg", "KSAT-t_"+folder ],
               ["ResidualWaterContent_WtAvg", "RSM-t_"+folder ],
               ["Porosity_WtAvg","POR-t_"+folder ],
               ["EffectivePorosity_WtAvg","EFPO-t_" +folder ] ,
               ["BubblingPressure_Geometric_WtAvg", "BBL-t_"+folder ] ,
               ["PoreSizeDistribution_geometric_WtAvg_y","PSD-t_"+folder]
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
     arcpy.AddMessage("### ***' %s' *** , made ###"%dir4eachRaster )


 try:


     tempOutputRasterFullpath    = outDir+"/"+firstNameOfSoilProperty+"/"+ firstNameOfSoilProperty+ "_"+folder

     arcpy.FeatureToRaster_conversion(in_features=muShapefileAsLayer,
                                      field="MUKEY-Vs-Values.csv." + a_soil_property[0] ,
                                      out_raster= tempOutputRasterFullpath   , cell_size= MatchDEM  )


     arcpy.gp.ExtractByMask_sa(tempOutputRasterFullpath, MatchDEM, tempOutputRasterFullpath+"c")       #c=clipped

     arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%sc'"%tempOutputRasterFullpath,
                                          Output_Workspace=outDir, Raster_Format="TIFF")
     arcpy.AddMessage("### Raster %sc created ###" %tempOutputRasterFullpath)


     #convert the raster to tif format
     #arcpy.RasterToOtherFormat_conversion(Input_Rasters=tempOutputRasterFullpath, Output_Workspace=outDir+"/"+firstNameOfSoilProperty , Raster_Format="TIFF")

     newRasterlayer = arcpy.mapping.Layer(tempOutputRasterFullpath+"c")    # create a new layer
     arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")



 except Exception, e:
     arcpy.AddMessage("!!!!!!!!!!Error encouncered at line 114 :"+ str(e))

print "Folder done: ", folder




