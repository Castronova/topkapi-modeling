#-------------------------------------------------------------------------------
# Name:        Run AutoHMS
# Purpose:     Create .BASIN script for HEC-HMS modeling.
#
# Author:      Cynthia V. Castro
#
# Created:     09/20/2015
# Copyright:   (c) Cynthia V. Castro 2015
# ArcGIS:      10.3
# Python:      2.7
#-------------------------------------------------------------------------------

import arcpy
import os
import time
from time import strftime

# Input Parameters
inGDB = arcpy.GetParameterAsText(0)
outDir = arcpy.GetParameterAsText(1)
fileName = arcpy.GetParameterAsText(2)

# Set Environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = arcpy.env.scratchWorkspace = inGDB
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(102008)
arcpy.CheckOutExtension("spatial")

# Geodatabase
arcpy.MakeFeatureLayer_management("Subbasin", "Subbasin")
arcpy.MakeFeatureLayer_management("Reach", "Reach")
arcpy.MakeRasterLayer_management("SoilsHSG", "Soils")
arcpy.MakeRasterLayer_management("Land_Use", "LandUse")
arcpy.MakeRasterLayer_management("DEM", "DEM_Whole")
arcpy.MakeRasterLayer_management("Impervious", "Imperviousness")

# Percent Impervious
arcpy.CopyRaster_management("Imperviousness", "pctImpervious", "", "", "", "", "", "8_BIT_UNSIGNED")
arcpy.BuildRasterAttributeTable_management("pctImpervious", "Overwrite")
arcpy.gp.ZonalStatisticsAsTable_sa("Subbasin", "FEATUREID", "pctImpervious", "Table_Imp", "DATA", "ALL")

imp = {}
basins = []
with arcpy.da.SearchCursor("Table_Imp", ["featureid", "MEAN"]) as cursor:
    for row in cursor:
        imp[row[0]]=row[1]
        basins.append(row[0])
del row, cursor

arcpy.AddField_management("Subbasin", "Imp", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "Imp"]) as cursor:
    for row in cursor:
        if row[1] in basins:
            row[1] = round(imp[row[0]],2)
        else:
            row[1] = 0
        cursor.updateRow(row)
del row, cursor

# Slope of Watershed
arcpy.gp.Slope_sa("DEM", "DEM_Slope", "PERCENT_RISE", "")
arcpy.gp.ZonalStatisticsAsTable_sa("Subbasin", "FEATUREID", "DEM_Slope", "Table_Slope", "DATA", "ALL")

slope = {}
with arcpy.da.SearchCursor("Table_Slope", ["FEATUREID", "MEAN"]) as cursor:
    for row in cursor:
        slope[row[0]]=(row[1])
del row, cursor

arcpy.AddField_management("Subbasin", "slope", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "slope"]) as cursor:
    for row in cursor:
        row[1]= round(slope[row[0]], 4)
        cursor.updateRow(row)
del row, cursor

# Reclassify Land Use
reclass = '11 1;21 2;22 5;23 6;24 7;31 9;41 4;42 4;43 4;52 10;71 10;81 3;82 3;90 8;95 8;12 1;72 10;73 10;74 10;51 10'
arcpy.gp.Reclassify_sa("LandUse", "Value", reclass, "LandUse_Reclass", "DATA")
arcpy.RasterToPolygon_conversion("LandUse_Reclass", "LandUse_Poly", "NO_SIMPLIFY", "VALUE")

# Classify Soils
arcpy.CopyRaster_management("SoilsHSG", "Soils2", "", "", "", "", "", "8_BIT_UNSIGNED")
arcpy.BuildRasterAttributeTable_management("Soils2", "Overwrite")
arcpy.gp.ZonalStatisticsAsTable_sa("Subbasin", "FEATUREID", "Soils2", "Table_Soils", "DATA", "ALL")

HSGvalue = {}
with arcpy.da.SearchCursor("Soils", ["Value", "ClassName"]) as cursor:
    for row in cursor:
        HSGvalue[row[0]] = row[1]
del row, cursor

domHSG = {}
sBasins = []
with arcpy.da.SearchCursor("Table_Soils", ["FEATUREID", "MAJORITY"]) as cursor:
    for row in cursor:
        domHSG[row[0]] = HSGvalue[row[1]].encode('ascii','ignore')
        sBasins.append(row[0])
del row, cursor

arcpy.AddField_management("Subbasin", "HSG", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "HSG"]) as cursor:
    for row in cursor:
        if row[0] in sBasins:
            row[1] = domHSG[row[0]]
        else:
            row[1] = 'C'
        cursor.updateRow(row)
del cursor, row

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "HSG"]) as cursor:
    for row in cursor:
        if row[1] == 'A/D' or 'B/D' or 'C/D':
            row[1] = 'D'
        cursor.updateRow(row)
del cursor, row

# Curve Number
arcpy.RasterToPolygon_conversion("Soils2", "Soils_Poly", "NO_SIMPLIFY", "Value")
arcpy.Union_analysis("LandUse_Poly #;Soils_Poly #", "LandUseSoils_Union", "ALL", "", "GAPS")
arcpy.MakeFeatureLayer_management("LandUseSoils_Union", "Union")
arcpy.SelectLayerByAttribute_management("Union", "NEW_SELECTION", "FID_LandUse_Poly=-1 OR FID_Soils_Poly=-1")
arcpy.DeleteRows_management("Union")

""" Lookup Table """
arcpy.CreateTable_management(inGDB, "Table_CNLookup", "", "")
arcpy.AddField_management("Table_CNLookup", "LandUse", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "Category", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "Description", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "A", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "B", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "C", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Table_CNLookup", "D", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.InsertCursor("Table_CNLookup", ["LandUse", "Category", "Description", "A", "B", "C", "D"]) as cursor:
    cursor.insertRow(("1", "Water", "Open Water, Perennial Ice/Snow", "100", "100", "100", "100"))
    cursor.insertRow(("2", "Developed ROW", "Developed Open Space", "68", "79", "86", "89"))
    cursor.insertRow(("3", "Cultivated Pasture", "Hay/Pasture, Cultivated Crops", "49", "69", "79", "84"))
    cursor.insertRow(("4", "Forest", "Deciduous, Evergreen, Mixed, Shrub/Scrub", "30", "55", "70", "77"))
    cursor.insertRow(("5", "Developed - Low Intensity", "Developed - Low Intensity", "51", "68", "79", "84"))
    cursor.insertRow(("6", "Developed - Medium Intensity", "Developed - Medium Intensity", "57", "72", "81", "86"))
    cursor.insertRow(("7", "Developed - High Intensity", "Developed - High Intensity, Barren Land", "77", "85", "90", "92"))
    cursor.insertRow(("8", "Wetlands", "Emergent Herbaceuous Wetlands, Woody Wetlands", "98", "98", "98", "98"))
    cursor.insertRow(("9", "Barren Land", "Barren Land", "76", "85", "90", "93"))
    cursor.insertRow(("10", "Grassland", "Dwart Scrub, Shrub, Herbaceous, Grasslands, Lichen, Moss", "39", "61", "74", "80"))
del cursor

""" Individual CN """
arcpy.AddField_management("Union", "CNi", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

cn = {}
with arcpy.da.SearchCursor("Table_CNLookup", ["LandUse", "A", "B", "C", "D"]) as cursor:
    for row in cursor:
        cn[row[0]] = (row[1],row[2],row[3],row[4])
del row, cursor

with arcpy.da.UpdateCursor("Union", ["CNi", "gridcode", "gridcode_1"]) as cursor:
    for row in cursor:
        if HSGvalue[row[2]] == 'A':
            row[0] = cn[row[1]][0]
        elif HSGvalue[row[2]] == 'B':
            row[0] = cn[row[1]][1]
        elif HSGvalue[row[2]] == 'C':
            row[0] = cn[row[1]][2]
        elif HSGvalue[row[2]] == 'D':
            row[0] = cn[row[1]][3]
        elif HSGvalue[row[2]] == 'A/D':
            row[0] = cn[row[1]][0] * 0.5 + cn[row[1]][3] * 0.5
        elif HSGvalue[row[2]] == 'B/D':
            row[0] = cn[row[1]][1] * 0.5 + cn[row[1]][3] * 0.5
        elif HSGvalue[row[2]] == 'C/D':
            row[0] = cn[row[1]][2] * 0.5 + cn[row[1]][3] * 0.5
        cursor.updateRow(row)
del row, cursor

""" Composite CN """
arcpy.AddField_management("Subbasin", "CN", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

arcpy.FeatureToRaster_conversion("Union", "CNi", "CNraster", "200")
arcpy.gp.ZonalStatisticsAsTable_sa("Subbasin", "FEATUREID", "CNraster", "Table_CN", "DATA", "ALL")

cn = {}
cBasins = []
with arcpy.da.SearchCursor("Table_CN", ["FEATUREID", "MEAN"]) as cursor:
    for row in cursor:
        cn[row[0]]=(row[1])
        cBasins.append(row[0])
del row, cursor

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "CN"]) as cursor:
    for row in cursor:
        if row[0] in cBasins:
            row[1]=round(cn[row[0]],2)
        else:
            row[1] = 80
        cursor.updateRow(row)
del row, cursor

# Subbasin Geometry
arcpy.AddField_management("Subbasin", "CENTROID_X", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Subbasin", "CENTROID_Y", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Subbasin", "AreaSqMI", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

arcpy.CalculateField_management("Subbasin", "CENTROID_X", "!shape.centroid.x!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Subbasin", "CENTROID_Y", "!shape.centroid.y!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Subbasin", "AreaSqMI", "!SHAPE.AREA@SQUAREMILES!", "PYTHON_9.3", "")

# Reach Geometry
arcpy.AddField_management("Reach", "START_X", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Reach", "START_Y", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Reach", "END_X", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Reach", "END_Y", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Reach", "LengthFT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Reach", "Junction", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

arcpy.CalculateField_management("Reach", "START_X", "!shape.firstPoint.x!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Reach", "START_Y", "!shape.firstPoint.y!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Reach", "END_X", "!shape.lastPoint.x!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Reach", "END_Y", "!shape.lastPoint.y!", "PYTHON_9.3", "")
arcpy.CalculateField_management("Reach", "LengthFT", "!shape.length@feet!", "PYTHON_9.3", "")

length = {}
with arcpy.da.SearchCursor("Reach", ["COMID", "LengthFT"]) as cursor:
    for row in cursor:
        length.update({row[0]: row[1]})
del row, cursor

fromnode = {}
fromnodes = []
with arcpy.da.SearchCursor("Reach", ["COMID", "FromNode"]) as cursor:
    for row in cursor:
        fromnode.update({row[1]: row[0]})
        fromnodes.append(row[1])
del row, cursor

tonode = {}
with arcpy.da.SearchCursor("Reach", ["COMID", "ToNode"]) as cursor:
    for row in cursor:
        tonode[row[0]]=(row[1])
del row, cursor

with arcpy.da.UpdateCursor("Reach", ["COMID", "Junction"]) as cursor:
    for row in cursor:
        row[1]=str('J'+str(tonode[row[0]]))
        cursor.updateRow(row)
del row, cursor

junction = {}
with arcpy.da.SearchCursor("Reach", ["COMID", "Junction"]) as cursor:
    for row in cursor:
        junction[row[0]]=(row[1])
del row, cursor

arcpy.AddField_management("Subbasin", "Junction", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "Junction"]) as cursor:
    for row in cursor:
        row[1]=junction[row[0]]
        cursor.updateRow(row)
del row, cursor

arcpy.AddField_management("Reach", "Downstream", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Reach", ["ToNode", "Downstream"]) as cursor:
    for row in cursor:
        if row[0] in fromnodes:
            row[1]=fromnode[row[0]]
        cursor.updateRow(row)
del row, cursor

ds_nodes = []
reaches = []
with arcpy.da.SearchCursor("Reach", ["Downstream", "COMID"]) as cursor:
    for row in cursor:
        if row[0] not in ds_nodes:
            ds_nodes.append(row[0])
        reaches.append(row[1])
del row, cursor

upstream = list(set(reaches) - set(ds_nodes))
downstream = list(set(reaches) - set(upstream))

# Lag Time (NRCS Watershed Method)
arcpy.AddField_management("Subbasin", "LengthFT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management("Subbasin", "t_lag", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "LengthFT"]) as cursor:
    for row in cursor:
        row[1] = round(length[row[0]],2)
        cursor.updateRow(row)
del row, cursor

with arcpy.da.UpdateCursor("Subbasin", ["FEATUREID", "t_lag", "LengthFT", "CN", "slope"]) as cursor:
    for row in cursor:
        l = row[2]
        CN = row[3]
        s = row[4]
        row[1] = round((math.pow(l,0.8) * math.pow(1000-9*CN,0.7)) / (1900 * math.pow(CN,0.7) * math.pow(s,0.5)),3)
        cursor.updateRow(row)
del row, cursor

lag = {}
subbasins = []
with arcpy.da.SearchCursor("Subbasin", ["FEATUREID", "t_lag"]) as cursor:
    for row in cursor:
        lag[row[0]]=(row[1])
        subbasins.append(row[0])
del row, cursor

arcpy.AddField_management("Reach", "t_lag", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

with arcpy.da.UpdateCursor("Reach", ["COMID", "t_lag"]) as cursor:
    for row in cursor:
        if row[0] in subbasins:
            row[1] = round(lag[row[0]],2)
        else:
            row[1] = 0
        cursor.updateRow(row)
del row, cursor

with arcpy.da.UpdateCursor("Subbasin", ["t_lag"]) as cursor:
    for row in cursor:
        if row[0] < 0.25:
            row[0] = 0.25
        cursor.updateRow(row)
del row, cursor

# .BASIN Script
localdate = strftime("%d %B %Y")
localtime = strftime("%H:%M:%S")

outPath = os.path.join(outDir, fileName+'.BASIN')

script = open(outPath, 'w')

script.write("Basin: {}\n".format(fileName))
script.write("     Last Modified Date:  "+localdate+"\n")
script.write("     Last Modified Time:  "+localtime+"\n")
script.write("     Version 3.5\n")
script.write("     Filepath Separator: \ \n")
script.write("     Unit System: English\n")
script.write("     Missing Flow To Zero: No\n")
script.write("     Enable Flow Ratio: No\n")
script.write("     Allow Blending: No\n")
script.write("     Compute Local Flow At Junctions: No\n")
script.write("\n")
script.write("     Enable Sediment Routing: No\n")
script.write("\n")
script.write("     Enable Quality Routing: No\n")
script.write("End:\n")
script.write("\n")

""" Junctions """
junctions = []
with arcpy.da.SearchCursor("Reach", ["COMID", "Junction", "END_X", "END_Y", "ToNode"]) as cursor:
    for row in cursor:
        if row[1] not in (set(junctions)):
            script.write("Junction: Junction-"+str(row[1])+"\n")
       	    script.write("     Canvas X: "+str(row[2])+"\n")
       	    script.write("     Canvas Y: "+str(row[3])+"\n")
            if row[4] in fromnodes:
                script.write("     Downstream: Flowline-"+str(fromnode[row[4]])+"\n")
       	    script.write("End:\n")
       	    script.write("\n")
        junctions.append(row[1])
del row, cursor

""" Flowlines """
with arcpy.da.SearchCursor("Reach", ["COMID", "START_X", "START_Y",
    "END_X", "END_Y", "t_lag", "Junction"]) as cursor:
    for row in cursor:
        if row[0] not in upstream:
            script.write("Reach: Flowline-"+str(row[0])+"\n")
            script.write("     Description: Routing\n")
            script.write("     Canvas X: "+str(row[3])+"\n")
            script.write("     Canvas Y: "+str(row[4])+"\n")
            script.write("     From Canvas X: "+str(row[1])+"\n")
            script.write("     From Canvas Y: "+str(row[2])+"\n")
            script.write("     Downstream: Junction-"+str(row[6])+"\n")
            script.write("\n")
            script.write("     Route: Lag\n")
            script.write("     Lag: "+str(row[5])+"\n")
            script.write("     Channel Loss: None\n")
            script.write("End:\n")
            script.write("\n")

""" Subbasins """
with arcpy.da.SearchCursor("Subbasin", ["FEATUREID", "CENTROID_X", "CENTROID_Y",
        "AreaSqMI", "t_lag", "Imp", "CN", "Junction"]) as cursor:
    for row in cursor:
        script.write("Subbasin: Catchment-"+str(row[0])+"\n")
    	script.write("     Description: Catchment-"+str(row[0])+"\n")
    	script.write("     Canvas X: "+str(row[1])+"\n")
    	script.write("     Canvas Y: "+str(row[2])+"\n")
    	script.write("     Area: "+str(row[3])+"\n")
        script.write("     Downstream: Junction-"+str(row[7])+"\n")
    	script.write("\n")

        script.write("     LossRate: SCS\n")
        script.write("     Percent Impervious Area: "+str(row[5])+"\n")
        script.write("     Curve Number: "+str(row[6])+"\n")
        script.write("     Initial Abstraction: 0\n")
        script.write("\n")

        script.write("     Transform: SCS\n")
        script.write("     Lag: "+str(row[4])+"\n")
        script.write("     Unitgraph Type: STANDARD\n")
        script.write("End:\n")
        script.write("\n")
del row, cursor

script.write("Basin Schematic Properties:\n")
script.write("     Last View N: 5000.0\n")
script.write("     Last View S: -5000.0\n")
script.write("     Last View W: -5000.0\n")
script.write("     Last View E: 5000.0\n")
script.write("     Maximum View N: 5000.0\n")
script.write("     Maximum View S: -5000.0\n")
script.write("     Maximum View W: -5000.0\n")
script.write("     Maximum View E: 5000.0\n")
script.write("     Extent Method: Elements\n")
script.write("     Buffer: 0\n")
script.write("     Draw Icons: Yes\n")
script.write("     Draw Icon Labels: Yes\n")
script.write("     Draw Map Objects: No\n")
script.write("     Draw Gridlines: No\n")
script.write("     Draw Flow Direction: No\n")
script.write("     Fix Element Locations: No\n")
script.write("     Fix Hydrologic Order: No\n")
script.write("End:\n")

script.close()