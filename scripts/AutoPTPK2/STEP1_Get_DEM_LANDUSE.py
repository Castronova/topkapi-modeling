import arcpy
import os
import sys
'''

Future Improvements:
Buffer distance and cell size meaningful values
User defined Projection
Folder and personal gdb naming convention. And their automatic creation
What boundary to use to clip the resulting rasters

Untested:
User defined resolution
Creating folders, and personal gdb
'''


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

inUsername = arcpy.GetParameterAsText(0)
inPassword = arcpy.GetParameterAsText(1)
outDir = arcpy.GetParameterAsText(2)
wshedBoundary = arcpy.GetParameterAsText(3)
bufferDi= arcpy.GetParameterAsText(4)
cell_size = arcpy.GetParameterAsText(5)

arcpy.AddMessage("the inputs are %s %s %s %s %s %s "%(inUsername,inPassword, outDir,wshedBoundary,bufferDi, cell_size))
def step1_get_dem_landuse(inUsername,inPassword,outDir,wshedBoundary,bufferDi,cell_size):
    '''

    :param inUsername: ArcGIS online Username
    :param inPassword: ArcGIS online password
    :param outDir: geodatabase (or directory) where the downlaoded files will be saved
    :param wshedBoundary: polygon shapefile for which the DEM and landuse will be donwloaded
    :param bufferDi: Buffer distance in meters to download DEM and landuse. Serves as factor of safety
    :param cell_size: The resolution or the cell size. A float (or integer) number, e.g. 30 or 100 etc.
    :return: downloads and saves the DEM and landuse rasters. Also, projects them to a UTM zone 12 (for now) CS
    '''

    #defaulted, to make things easier
    if inUsername == "": inUsername = "prasanna_usu"
    if inPassword  == "": inPassword = "Hydrology12!@"
    if bufferDi == "":
        if cell_size == "":
            bufferDi = 100
        else:
            bufferDi = float(cell_size) * 3

    # Set workspace environment
    arcpy.env.workspace  = outDir   # = arcpy.env.scratchWorkspace
    #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(102008) #equal area ... projection
    #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 12N")

    Boundary = "Boundary"

    # # Add Data to Geodatabase
    # arcpy.FeatureClassToFeatureClass_conversion(wshedBoundary, outDir, "Boundary")  # to convert feature to feature class (as contained in geodatabase)
    # arcpy.MakeFeatureLayer_management("Boundary", "Boundary")                         # creates temporary layer

    # Buffer
    arcpy.Buffer_analysis(wshedBoundary, "Buffer", str(bufferDi)+" Meters", "FULL", "ROUND", "NONE", "", "PLANAR")
    arcpy.MakeFeatureLayer_management("Buffer", "Buffer")                        #creates temporary layer

    # Connect to ArcGIS Servers
    out_folder_path = 'GIS Servers'

    out_landscape = 'Landscape.ags'
    server_landscape = 'https://landscape5.arcgis.com:443/arcgis/services/'

    out_elevation = 'Elevation.ags'
    server_elevation = 'https://elevation.arcgis.com:443/arcgis/services/'




    arcpy.mapping.CreateGISServerConnectionFile("USE_GIS_SERVICES",
                                                    out_folder_path,
                                                    out_landscape,
                                                    server_landscape,
                                                    "ARCGIS_SERVER",
                                                    username=inUsername,
                                                    password=inPassword,
                                                    save_username_password=True)

    arcpy.mapping.CreateGISServerConnectionFile("USE_GIS_SERVICES",
                                                    out_folder_path,
                                                    out_elevation,
                                                    server_elevation,
                                                    "ARCGIS_SERVER",
                                                    username=inUsername,
                                                    password=inPassword,
                                                    save_username_password=True)


    # Extract Image Server Data
    """ DEM, 30m NED """
    NED30m_ImageServer = "GIS Servers\\Elevation\\NED30m.ImageServer"
    arcpy.MakeImageServerLayer_management(NED30m_ImageServer, "NED30m_Layer")
    arcpy.gp.ExtractByMask_sa("NED30m_Layer", "Buffer", "DEM")

    arcpy.env.snapRaster = "DEM"                                              # Set Snap Raster environment

    """ Land Use """
    NLCD_ImageServer = "GIS Servers\\Landscape\\USA_NLCD_2011.ImageServer"
    arcpy.MakeImageServerLayer_management(NLCD_ImageServer,"NLCD_Layer")
    arcpy.gp.ExtractByMask_sa("NLCD_Layer", "DEM", "Land_Use")

    arcpy.AddMessage("************DEM and Land Use data, i.e. NLCD , download complete************")




    """ Project DEM to UTM """
    arcpy.ProjectRaster_management(in_raster="DEM", out_raster="DEM_Prj", out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", resampling_type="NEAREST", cell_size="30.922080775934 30.922080775934", geographic_transform="WGS_1984_(ITRF00)_To_NAD_1983", Registration_Point="", in_coor_system="PROJCS['North_America_Albers_Equal_Area_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]")

    """ Project Land Use to UTM """
    arcpy.ProjectRaster_management(in_raster="Land_Use", out_raster="Land_Use_Prj", out_coor_system="PROJCS['WGS_1984_UTM_Zone_12N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", resampling_type="NEAREST", cell_size="30.922080775934 30.922080775934", geographic_transform="WGS_1984_(ITRF00)_To_NAD_1983", Registration_Point="", in_coor_system="PROJCS['North_America_Albers_Equal_Area_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]")

    arcpy.AddMessage("************DEM and Land Use file projected to UTM************")

    #put DEM and Land_Use on maps as a layer
    mxd = arcpy.mapping.MapDocument("CURRENT")                                  # get the map document
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]                               #first dataframe in the document

    #if cell size given, need to resample here
    if cell_size != "":
        """ resample to the user specified resolution """

        arcpy.CopyRaster_management(in_raster="DEM_Prj.tif", out_rasterdataset="DEM_temp", config_keyword="", background_value="", nodata_value="-9999", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="", scale_pixel_value="NONE", RGB_to_Colormap="NONE")

        arcpy.Resample_management(in_raster= "DEM_temp",
                                  out_raster= "DEM_Prj",
                                  cell_size= str(cell_size)+" "+str(cell_size), resampling_type="NEAREST")

        arcpy.CopyRaster_management(in_raster="Land_Use_Prj.tif",
                                    out_rasterdataset="Landuse_temp",
                                    config_keyword="", background_value="",
                                    nodata_value="-9999",
                                    onebit_to_eightbit="NONE",
                                    colormap_to_RGB="NONE",
                                    pixel_type="", scale_pixel_value="NONE",
                                    RGB_to_Colormap="NONE")
        arcpy.Resample_management(in_raster= "Landuse_temp",
                                  out_raster= "Land_Use_Prj",
                                  cell_size=str(cell_size)+" "+str(cell_size), resampling_type="NEAREST")

        arcpy.AddMessage("************Resample DEM and Land Use with cell size %s m completed ************"%cell_size)
        DEM_layer = arcpy.mapping.Layer(outDir+"/DEM_Prj")    # create a new layer
        arcpy.mapping.AddLayer(df, DEM_layer,"TOP")

        LandUse_layer = arcpy.mapping.Layer(outDir+"/Land_Use_Prj")    # create a new layer
        arcpy.mapping.AddLayer(df, LandUse_layer,"TOP")


    DEM_layer = arcpy.mapping.Layer(outDir+"/DEM_Prj")    # create a new layer
    arcpy.mapping.AddLayer(df, DEM_layer,"TOP")

    LandUse_layer = arcpy.mapping.Layer(outDir+"/Land_Use_Prj")    # create a new layer
    arcpy.mapping.AddLayer(df, LandUse_layer,"TOP")

    Buffer_layer = arcpy.mapping.Layer(outDir+"/Buffer")    # create a new layer
    arcpy.mapping.AddLayer(df, Buffer_layer,"TOP")

if __name__ == "__main__":
    step1_get_dem_landuse(inUsername,inPassword,outDir,wshedBoundary,bufferDi,cell_size)

