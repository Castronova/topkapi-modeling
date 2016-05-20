#-------------------------------------------------------------------------------
# Name:        GetData
# Purpose:     Extract hydrological data for watershed boundary from
#              ESRI Living Atlas servers.
#
# Author:      Cynthia V. Castro
#
# Created:     10/10/2015
# Copyright:   (c) Cynthia V. Castro 2015
# ArcGIS:      10.3
# Python:      2.7
#-------------------------------------------------------------------------------

import arcpy
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

inUsername = arcpy.GetParameterAsText(0)
inPassword = arcpy.GetParameterAsText(1)
outDir = arcpy.GetParameterAsText(2)
wshedDir = arcpy.GetParameterAsText(3)
catchDir = arcpy.GetParameterAsText(4)
flowDir = arcpy.GetParameterAsText(5)

# Set workspace environment
arcpy.env.workspace = arcpy.env.scratchWorkspace = outDir
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(102008)

# Add Data to Geodatabase
arcpy.FeatureClassToFeatureClass_conversion(catchDir, outDir, "Subbasin")
arcpy.FeatureClassToFeatureClass_conversion(flowDir, outDir, "Reach")
arcpy.FeatureClassToFeatureClass_conversion(wshedDir, outDir, "Boundary")

arcpy.MakeFeatureLayer_management("Subbasin", "Subbasin")
arcpy.MakeFeatureLayer_management("Reach", "Reach")
arcpy.MakeFeatureLayer_management("Boundary", "Boundary")

# Buffer
arcpy.Buffer_analysis("Boundary", "Buffer", "500 Feet", "FULL", "ROUND", "NONE", "", "PLANAR")

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
""" Land Use """
NLCD_ImageServer = "GIS Servers\\Landscape\\USA_NLCD_2011.ImageServer"
arcpy.MakeImageServerLayer_management(NLCD_ImageServer,"NLCD_Layer")
arcpy.gp.ExtractByMask_sa("NLCD_Layer", "Buffer", "Land_Use")

""" Percent Impervious """
Imp_ImageServer = "GIS Servers\\Landscape\\USA_NLCD_Impervious_2011.ImageServer"
arcpy.MakeImageServerLayer_management(Imp_ImageServer, "Impervious_Layer")
arcpy.gp.ExtractByMask_sa("Impervious_Layer", "Buffer", "Impervious")

""" Soils HSG, USDA """
Soils_ImageServer = "GIS Servers\\Landscape\\USA_Soils_Hydrologic_Group.ImageServer"
arcpy.MakeImageServerLayer_management(Soils_ImageServer, "Soils_Layer")
arcpy.gp.ExtractByMask_sa("Soils_Layer", "Buffer", "SoilsHSG")

""" DEM, 30m NED """
NED30m_ImageServer = "GIS Servers\\Elevation\\NED30m.ImageServer"
arcpy.MakeImageServerLayer_management(NED30m_ImageServer, "NED30m_Layer")
arcpy.gp.ExtractByMask_sa("NED30m_Layer", "Buffer", "DEM")