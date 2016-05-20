import os
import arcpy
from STEP1_Get_DEM_LANDUSE import step1_get_dem_landuse
from STEP2_DEM_Processing import step2_dem_processing
# from STEP3_Merge_SSURGO import step3_merge_ssurgo
from STEP4_Join_Merge_Export import STEP4_Join_Merge_Export


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
path2statsgoFolders = arcpy.GetParameterAsText(9)
outCS = arcpy.GetParameterAsText(10)

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
    arcpy.AddMessage(e)



# Step1, download the data
# step1_get_dem_landuse(inUsername,inPassword,raw_files_outDir,wshedBoundary,bufferDi,cell_size, outCS)

# Step2
DEM = os.path.join(raw_files_outDir, "DEM_Prj")
land_use = os.path.join(raw_files_outDir, "Land_Use_Prj")
step2_dem_processing(DEM, land_use ,raw_files_outDir , outlet_point_sf, threshold)

# Step4
MatchRaster = os.path.join(raw_files_outDir, "mask_r")
STEP4_Join_Merge_Export (path2ssurgoFolders, path2statsgoFolders, ssurgo_outDir, MatchRaster )

# To tif
for outRaster in ["mask_r", "DEM_Prj_fc", "Land_Use_Prj_c",  "n_Overland", "fdr_c_r"  , "slope_c", "SD"]:
    arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(raw_files_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

for outRaster in ["bbl-tc", "efpo-tc", "ksat-tc",  "psd-tc", "rsm-tc" ]:
    arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(ssurgo_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

