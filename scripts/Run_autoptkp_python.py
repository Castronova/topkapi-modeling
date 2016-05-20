import os
import arcpy
from STEP1_Get_DEM_LANDUSE import step1_get_dem_landuse
from STEP2_DEM_Processing import step2_dem_processing
from STEP3_Merge_SSURGO import step3_merge_ssurgo
from STEP4_Join_Merge_Export import STEP4_Join_Merge_Export

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

inUsername = 'prasanna_usu'
inPassword = 'Hydrology12!@'
projDir = r"E:\Research Data\00 Red Butte Creek\New folder (2)"         # RAW FILES
wshedBoundary = r"E:\Research Data\00 Red Butte Creek\RBC_3\RawFiles.gdb\RBC_Box"    # Bounding Box, as layer
bufferDi= 100
cell_size = 50
outlet_point_sf = r"E:\Research Data\00 Red Butte Creek\RBC_3\RawFiles.gdb\RBC_outlet"
threshold = 300        # Threshold for defining stream
path2ssurgoFolders = r"E:\Research Data\00 Red Butte Creek\SSURGO_Folders"
path2statsgoFolders = r"E:\Research Data\00 Red Butte Creek\STATSGO_Folders"
outCS = arcpy.GetParameterAsText(10)

arcpy.env.workspace = arcpy.env.scratchWorkspace = projDir

def create_project_folders(projDir):
    # list of empty directories to be made
    folders_to_create = ['DEM_processed_rasters', 'SSURGO_rasters', 'TIFFS']

    # Out Directories
    raw_files_outDir = os.path.join(projDir, "Raw_files.gdb")
    DEM_processed_projDir = os.path.join(projDir, folders_to_create[0])
    ssurgo_outDir = os.path.join(projDir,folders_to_create[1])
    tiffs_outDir = os.path.join(projDir, folders_to_create[2])

    # make the empty directories
    try:
        for folder in folders_to_create:
            directory = os.path.join(projDir,folder)
            if not os.path.exists(directory):
                os.makedirs(directory)
            arcpy.CreateFileGDB_management(projDir, "Raw_files.gdb")

    except Exception, e:
        arcpy.AddMessage(e)


    return raw_files_outDir, DEM_processed_projDir, ssurgo_outDir , tiffs_outDir
raw_files_outDir, DEM_processed_projDir, ssurgo_outDir , tiffs_outDir = create_project_folders(projDir)

def rasters_to_tif(raw_files_outDir =raw_files_outDir ,ssurgo_outDir = ssurgo_outDir, tiffs_outDir=tiffs_outDir ):
    # To tif
    try:
        for outRaster in ["mask_r", "DEM_Prj_fc", "Land_Use_Prj_c",  "n_Overland", "fdr_c_r"  , "slope_c", "SD"]:
            arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(raw_files_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

        for outRaster in ["bbl-tc", "efpo-tc", "ksat-tc",  "psd-tc", "rsm-tc" ]:
            arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(ssurgo_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

    except Exception,e:
        arcpy.AddMessage(e)
    return


DEM = os.path.join(raw_files_outDir, "DEM_Prj")
land_use = os.path.join(raw_files_outDir, "Land_Use_Prj")
MatchRaster = os.path.join(raw_files_outDir, "mask_r")


step1_get_dem_landuse(inUsername,inPassword,raw_files_outDir,wshedBoundary,bufferDi,cell_size, outCS)
step2_dem_processing(DEM, land_use ,raw_files_outDir , outlet_point_sf, threshold)
STEP4_Join_Merge_Export(path2ssurgoFolders, path2statsgoFolders, ssurgo_outDir, MatchRaster )
