import arcpy
from arcpy import env
import os


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

path2statsgo = arcpy.GetParameterAsText(0)



path2statsgo = r"C:\Users\Prasanna\Box Sync\00 Red Butte Creek\STATSGO_Folder\wss_gsmsoil_UT_[2006-07-06]"
path2tabular = path2statsgo+"/tabular"
path2Spatial= path2statsgo+"/spatial"
arcpy.env.workspace = arcpy.env.scratchWorkspace = path2statsgo
outDir = path2statsgo
muShapefile = os.listdir(path2Spatial)[1].split('.')[0]                             #muShapefile = 'soilmu_a_ut612'
arcpy.AddMessage("### ***'%s'***  shapefile found was " %muShapefile)

#project the shapefile in statsgo table, FILE SELECTION
arcpy.Project_management(in_dataset=path2statsgo+"/spatial/" + muShapefile +".shp",
                         out_dataset=outDir + "/"+ muShapefile +"_prj",
                         out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="")
arcpy.AddMessage("### Shapefile projected ###")


# to add the projected shapefile from statsgo, as a layer to the map at the bottom of the TOC in data frame 0
muShapefileAsLayer = muShapefile +"_prj"


mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               #first dataframe in the document

layer1 = arcpy.mapping.Layer(outDir + "/"+ muShapefileAsLayer+ ".shp" ) # create a new layer
arcpy.mapping.AddLayer(df, layer1,"TOP")             #added to layer because this will be used code below


try:
 # join the table that had mUKEY mapped to all soil properties
 arcpy.AddJoin_management(muShapefileAsLayer, "MUKEY", path2statsgo+"/MUKEY-Vs-Values.csv", "MUKEY")

 arcpy.AddMessage("Field Successfully added")

 newRasterlayer = arcpy.mapping.Layer(muShapefileAsLayer)    # create a new layer
 arcpy.mapping.AddLayer(df, newRasterlayer,"TOP")

 arcpy.AddMessage("Field Successfully added")

except Exception, e:
    print e

