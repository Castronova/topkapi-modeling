import os
from STEP1_Get_DEM_LANDUSE import step1_get_dem_landuse
from STEP2_DEM_Processing import step2_dem_processing
from STEP4_Join_Merge_Export import STEP4_Join_Merge_Export
import arcpy
try:
    from STEP3_Merge_SSURGO import step3_merge_ssurgo
except Exception,e:
    arcpy.AddMessage(e)

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# inputs, from ArcGIS toolbox
inUsername = arcpy.GetParameterAsText(0)
inPassword = arcpy.GetParameterAsText(1)
projDir = arcpy.GetParameterAsText(2)           # RAW FILES
wshedBoundary = arcpy.GetParameterAsText(3)     # Bounding Box, as layer
bufferDi= arcpy.GetParameterAsText(4)
cell_size = arcpy.GetParameterAsText(5)
outlet_fullpath = arcpy.GetParameterAsText(6)   # as layer again
threshold = arcpy.GetParameterAsText(7)         # Threshold for defining stream
path2ssurgoFolders = arcpy.GetParameterAsText(8)
path2statsgoFolders = arcpy.GetParameterAsText(9)
outCS = arcpy.GetParameterAsText(10)

# if script ran as standalone
if projDir == "":
    # inputs for standalone operation
    projDir = r"E:\Research Data\del"
    outlet_fullpath = r"E:\Research Data\00 Red Butte Creek\RBC_point_Area\RawFiles.gdb\RBC_outlet"
    threshold = ""
    wshedBoundary = r"E:\Research Data\00 Red Butte Creek\RBC_point_Area\RawFiles.gdb\RBC_Box"
    inUsername = "prasanna_usu"
    inPassword = "Hydrology12!@"
    bufferDi = ""
    cell_size = ""
    projection_file = ""
    outCS = ""
    path2ssurgoFolders =r"E:\Research Data\00 Red Butte Creek\SSURGO_Folders"
    path2statsgoFolders = r"E:\Research Data\00 Red Butte Creek\STATSGO_Folders"

    #DEM_fullpath = r"E:\Research Data\00 Red Butte Creek\RBC_3\RawFiles.gdb\DEM_Prj"
    #land_use_fullpath = r"E:\Research Data\00 Red Butte Creek\RBC_3\RawFiles.gdb\Land_Use_Prj"

# list of empty directories to be made
folders_to_create = ['DEM_processed_rasters', 'SSURGO_rasters', 'TIFFS', 'BinaryGrid']

# Out Directories
raw_files_outDir = os.path.join(projDir, "Raw_files.gdb")
downloads_outDir = os.path.join(projDir, "Downloads.gdb")
DEM_processed_projDir = os.path.join(projDir, folders_to_create[0])
ssurgo_outDir = os.path.join(projDir,folders_to_create[1])
tiffs_outDir = os.path.join(projDir, folders_to_create[2])
binaryGrid_outDir = os.path.join(projDir, folders_to_create[3])

# # make the empty directories
# try:
#     for folder in folders_to_create:
#         directory = os.path.join(projDir,folder)
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         arcpy.CreateFileGDB_management(projDir, "Raw_files.gdb")
#         arcpy.CreateFileGDB_management(projDir, "Downloads.gdb")
#
# except Exception, e:
#     arcpy.AddMessage(e)
#
# arcpy.env.workspace = arcpy.env.scratchWorkspace = projDir
#
#
# # Step1, download the data
# step1_get_dem_landuse(inUsername,inPassword,downloads_outDir ,wshedBoundary,bufferDi,cell_size, outCS)
#
# # Step2
# DEM_fullpath = os.path.join(downloads_outDir, "DEM_Prj")
# land_use_fullpath = os.path.join(downloads_outDir, "Land_Use_Prj")
# step2_dem_processing(DEM_fullpath, land_use_fullpath ,raw_files_outDir , outlet_fullpath, threshold)
#
# # Step4
# MatchRaster = os.path.join(raw_files_outDir, "mask_r")
# STEP4_Join_Merge_Export (path2ssurgoFolders, path2statsgoFolders, ssurgo_outDir, MatchRaster )

# To tif, and flt
for outRaster in ["mask_r", "DEM_Prj_fc", "NLCD_c",  "n_Overland", "fdr_cr" , "str_cr" , "slope_c", "SD"]:
    arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(raw_files_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

for outRaster in ["bbl-tc.tif", "efpo-tc.tif", "ksat-tc.tif",  "psd-tc.tif", "rsm-tc.tif" ]:
    arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(ssurgo_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

try:
    for outRaster in ["mask_r", "DEM_Prj_fc", "NLCD_c",  "n_Overland", "fdr_cr" , "str_cr" , "slope_c", "SD","str_c","str_cr9999"]:
        arcpy.RasterToFloat_conversion(in_raster="'%s'"%(os.path.join(raw_files_outDir, outRaster)), out_float_file=os.path.join(binaryGrid_outDir, outRaster+".flt"))
    for outRaster in ["bbl-tc.tif", "efpo-tc.tif", "ksat-tc.tif",  "psd-tc.tif", "rsm-tc.tif" ]:
        arcpy.RasterToFloat_conversion(in_raster="'%s'"%(os.path.join(ssurgo_outDir, outRaster)), out_float_file=os.path.join(binaryGrid_outDir, outRaster.split(".")[0]+".flt"))
except Exception,e:
    arcpy.AddMessage(e)