import os
import ConfigParser
from ConfigParser import SafeConfigParser
import shutil

def create_config_files_create_file(simulation_folder, tiff_folder,pVs_t0=90., Vo_t0=9000., Qc_t0=0, Kc=1 ):
    if not os.path.exists(simulation_folder):
        os.makedirs(simulation_folder)

    configWrite = ConfigParser.RawConfigParser()
    configWrite.add_section('raster_files')
    configWrite.set('raster_files', 'dem_fname', tiff_folder+"/DEM_Prj_fc.tif")
    configWrite.set('raster_files', 'mask_fname', tiff_folder+  "/mask_r.tif" )
    configWrite.set('raster_files', 'soil_depth_fname', tiff_folder + "/SD.tif")
    configWrite.set('raster_files', 'conductivity_fname', tiff_folder + "/ksat-tc.tif")
    configWrite.set('raster_files', 'hillslope_fname',tiff_folder+ "/slope_c.tif")
    configWrite.set('raster_files', 'sat_moisture_content_fname', tiff_folder+ '/por-tc.tif')
    configWrite.set('raster_files', 'resid_moisture_content_fname', tiff_folder+ '/rsm-tc.tif' )
    configWrite.set('raster_files', 'bubbling_pressure_fname',tiff_folder+ '/bbl-tc.tif')
    configWrite.set('raster_files', 'pore_size_dist_fname', tiff_folder+ '/psd-tc.tif' )
    configWrite.set('raster_files', 'overland_manning_fname', tiff_folder+ '/n_Overland.tif' )
    configWrite.set('raster_files', 'channel_network_fname', tiff_folder+ '/str_cr255.tif')
    configWrite.set('raster_files', 'flowdir_fname', tiff_folder+ '/fdr_cr.tif' )
    configWrite.set('raster_files', 'channelMannings_fname', tiff_folder+ '/n_Channel.tif' )
    configWrite.set('raster_files', 'flowdir_source',  'ArcGIS' )


    configWrite.add_section('output')
    configWrite.set('output', 'param_fname', simulation_folder+"/cell_param_unmodified.dat")

    configWrite.add_section('numerical_values')
    configWrite.set('numerical_values', 'pVs_t0', pVs_t0)
    configWrite.set('numerical_values','Vo_t0', Vo_t0 )
    configWrite.set('numerical_values','Qc_t0',Qc_t0 )
    configWrite.set('numerical_values','Kc', Kc)

    with open(os.path.join(simulation_folder,'create_file.ini'), 'wb') as configFile:
        configWrite.write(configFile)

    return

def create_config_files_zero_slope_mngmt(simulation_folder, cell_size=30.92208078 ):
    if not os.path.exists(simulation_folder):
        os.makedirs(simulation_folder)

    configWrite = ConfigParser.RawConfigParser()
    configWrite.add_section('input_files')
    configWrite.set('input_files', 'file_cell_param', simulation_folder+'/cell_param_unmodified.dat')

    configWrite.add_section('output_files')
    configWrite.set('output_files', 'file_cell_param_out',simulation_folder+'/cell_param.dat')


    configWrite.add_section('numerical_values')
    configWrite.set('numerical_values', 'nb_param', 21)
    configWrite.set('numerical_values', 'X', cell_size)

    with open(os.path.join(simulation_folder,'zero_slope_management.ini'), 'wb') as configFile:
        configWrite.write(configFile)

    return

def create_config_files_plot_flow_precip(simulation_folder, outlet_ID ,calibration_start_data='01/01/2015' ):
    if not os.path.exists(simulation_folder+"/results"):
        os.makedirs(simulation_folder+"/results")

    configWrite = ConfigParser.RawConfigParser()
    configWrite.add_section('files')
    configWrite.set('files', 'file_Qsim', '/results/results.h5')
    configWrite.set('files', 'file_Qobs', '/Runoff.dat')
    configWrite.set('files', 'file_rain', '/rainfields.h5')
    configWrite.set('files', 'image_out', '/results')

    configWrite.add_section('groups')
    configWrite.set('groups', 'file_cell_param_out','cell_param.dat')


    configWrite.add_section('parameters')
    configWrite.set('parameters', 'outlet_ID', outlet_ID)
    configWrite.set('parameters', 'graph_format', 'png')
    configWrite.set('parameters', 'start_calibration', calibration_start_data  +" ;dd/mm/yyyy")

    configWrite.add_section('flags')
    configWrite.set('flags', 'Qobs', 'True')
    configWrite.set('flags', 'Pobs', 'True')
    configWrite.set('flags', 'nash', 'True')
    configWrite.set('flags', 'R2', 'True')
    configWrite.set('flags', 'RMSE', 'True')
    configWrite.set('flags', 'RMSE_norm', 'True')
    configWrite.set('flags', 'Diff_cumul', 'True')
    configWrite.set('flags', 'Bias_cumul', 'True')
    configWrite.set('flags', 'Err_cumul', 'True')
    configWrite.set('flags', 'Abs_cumul', 'True')


    with open(os.path.join(simulation_folder,'plot-flow-precip.ini'), 'wb') as configFile:
        configWrite.write(configFile)

    return

def create_config_files_plot_soil_moisture_map(simulation_folder,t1=1, t2=5, variable=4, fac_L=1., fac_Ks=1., fac_n_o=1., fac_n_c=1. ):
    if not os.path.exists(simulation_folder+"/SM"):
        os.makedirs(simulation_folder+"/SM")

    configWrite = ConfigParser.RawConfigParser()
    configWrite.add_section('files')
    configWrite.set('files', 'file_global_param', 'global_param.dat')
    configWrite.set('files', 'file_cell_param', 'cell_param.dat')
    configWrite.set('files', 'file_sim', '/results/results.h5')

    configWrite.add_section('paths')
    configWrite.set('paths', 'path_out', simulation_folder +"/SM")


    configWrite.add_section('calib_params')
    configWrite.set('calib_params', 'fac_L', fac_L)
    configWrite.set('calib_params', 'fac_Ks', fac_Ks)
    configWrite.set('calib_params', 'fac_n_o', fac_n_o)
    configWrite.set('calib_params', 'fac_n_c', fac_n_c)

    configWrite.add_section('flags')
    configWrite.set('flags', 't1', t1)
    configWrite.set('flags', 't2', t2)
    configWrite.set('flags', 'variable', variable)

    with open(os.path.join(simulation_folder,'plot-soil-moisture-map.ini'), 'wb') as configFile:
        configWrite.write(configFile)

    return

def create_config_files_TOPKAPI_ini(simulation_folder, external_flow_status= 'False', append_output_binary = 'False',fac_L = 1.4, fac_Ks = 1. ,fac_n_o  = 1. ,fac_n_c  = 1., fac_th_s = 1 ):

    if not os.path.exists(simulation_folder):
        os.makedirs(simulation_folder)

    configWrite = ConfigParser.RawConfigParser()

    configWrite.add_section('input_files')
    configWrite.set('input_files', 'file_global_param', simulation_folder+"/global_param.dat")
    configWrite.set('input_files', 'file_cell_param', simulation_folder+ "/cell_param.dat" )
    configWrite.set('input_files', 'file_rain', simulation_folder + "/rainfields.h5")
    configWrite.set('input_files', 'file_ET', simulation_folder + "/ET.h5")

    configWrite.add_section('output_files')
    configWrite.set('output_files', 'file_out', simulation_folder+"/results/results.h5")
    configWrite.set('output_files', 'file_change_log_out', simulation_folder+  "/results/change_result_log.dat" )
    configWrite.set('output_files', 'append_output', append_output_binary )

    configWrite.add_section('groups')
    configWrite.set('groups', 'group_name', 'sample_event')

    configWrite.add_section('external_flow')
    configWrite.set('external_flow', 'external_flow', 'False')
    if external_flow_status.lower() == 'true':
        print "External flow parameters need to be entered here"

    configWrite.add_section('numerical_options')
    configWrite.set('numerical_options', 'solve_s', 1)
    configWrite.set('numerical_options','solve_o',1 )
    configWrite.set('numerical_options','solve_c',1 )
    configWrite.set('numerical_options','only_channel_output', 'False')

    configWrite.add_section('calib_params')
    configWrite.set('calib_params', 'fac_L', fac_L)
    configWrite.set('calib_params', 'fac_Ks', fac_Ks)
    configWrite.set('calib_params', 'fac_n_o', fac_n_o)
    configWrite.set('calib_params', 'fac_n_c', fac_n_c)
    configWrite.set('calib_params', 'fac_th_s', fac_th_s)


    with open(os.path.join(simulation_folder,'TOPKAPI.ini'), 'wb') as configFile:
        configWrite.write(configFile)

    return

def create_cell_param( create_file_ini_file, zero_slope_mngmt_ini_file):

    import sys
    sys.path.append('../../PyTOPKAPI')

    from pytopkapi.parameter_utils.create_file import generate_param_file
    from pytopkapi.parameter_utils import modify_file

    # Generate Parameter Files
    generate_param_file(create_file_ini_file, isolated_cells=False)
    print "Cell Parameter file created"

    # slope corrections
    modify_file.zero_slope_management(zero_slope_mngmt_ini_file)
    print "Zero Slope corrections made"

    return

def create_global_param(simulation_folder, A_thres=25000000, X=30.92208078, Dt=86400, W_min=1., W_Max=10.):
    title = ['X', 'Dt', 'Alpha_s', 'Alpha_o', 'Alpha_c', 'A_thres', 'W_min', 'W_max']
    values = [X, Dt, 2.5,1.6666667, 1.6666667, A_thres, W_min , W_Max]
    values = [str(item) for item in values]
    with open(simulation_folder+"/global_param.dat", "wb") as g_param_file:
        string = "\t\t".join(title)+ '\n' + "\t\t".join(values)
        g_param_file.write(string)
        #g_param_file.write(values)

def create_rain_ET_file(simulation_folder, total_no_of_cell, ppt_file_txt ):
    import h5py, numpy

    # output path
    rainfall_outputFile = os.path.join(simulation_folder, "rainfields.h5")
    ET_outputFile = os.path.join(simulation_folder, "ET.h5")

    time_step = 59 #161
    no_of_cell = total_no_of_cell # 3400
    # rainfall_intensity_perUnitTime = 20 #mm
    rainfall_reduction_factor = 1

    # 1_del (for removing file readings)
    rain_from_file = numpy.genfromtxt(ppt_file_txt, delimiter='\t')

    with h5py.File(rainfall_outputFile,'w') as f2:

        f2.create_group('sample_event')
        f2['sample_event'].create_dataset('rainfall', shape=(time_step, no_of_cell), dtype='f' )

        rainArray =  f2['sample_event']['rainfall']
        data = numpy.zeros((time_step , no_of_cell))
        for i in range(time_step):
            # 2_del (for removing file readings)
            rainfall_intensity_perUnitTime = rain_from_file[i][-1] * rainfall_reduction_factor
            a = numpy.empty( (1,no_of_cell ) )
            a.fill(rainfall_intensity_perUnitTime)  #
            data[i,:] = a

        # data[0,:] = numpy.zeros((1,no_of_cell))
        # data[time_step/4,:] = numpy.zeros((1,no_of_cell))
        # data[time_step/2,:] = numpy.zeros((1,no_of_cell))
        # data[time_step/3,:] = numpy.zeros((1,no_of_cell))
        rainArray[:] = data



    with h5py.File(ET_outputFile,'w' ) as f1:
        f1.create_group('sample_event')
        f1['sample_event'].create_dataset('ETo', shape=( time_step, no_of_cell), dtype='f' )
        f1['sample_event'].create_dataset('ETr', shape=( time_step, no_of_cell), dtype='f' )

        EToArray =  f1['sample_event']['ETo']
        ETrArray =  f1['sample_event']['ETr']

        data = numpy.zeros((time_step , no_of_cell))
        for i in range(time_step):
            data[i,:] = numpy.random.rand(1,no_of_cell)*0.0

        EToArray = data
        ETrArray = data

def get_outletID_noOfCell(cell_para_file):
    import numpy as np
    cell_param_array = np.genfromtxt(cell_para_file, delimiter=' ')
    no_of_cell = cell_param_array.shape[0]

    # outlet_ID is the first element (cell lable) of parameter for the cell whose d/s id = -999
    outlet_ID = cell_param_array[cell_param_array[:,14] < -99][0][0]
    return int(outlet_ID), no_of_cell

def step0(ini_fname):
    import arcpy
    from STEP1_Get_DEM_LANDUSE import step1_get_dem_landuse
    from STEP2_DEM_Processing import step2_dem_processing
    from STEP4_Join_Merge_Export import STEP4_Join_Merge_Export


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
    areaThreshold = arcpy.GetParameterAsText(7)     # Threshold for defining stream in km2
    path2ssurgoFolders = arcpy.GetParameterAsText(8)
    path2statsgoFolders = arcpy.GetParameterAsText(9)
    outCS = arcpy.GetParameterAsText(10)

    # INPUTS, if script ran as standalone
    if projDir == "":

        # initializing
        config = SafeConfigParser()
        config.read(ini_fname)

        # path to directories
        path2ssurgoFolders = config.get('directory', 'ssurgo_collection')
        path2statsgoFolders = config.get('directory', 'statsgo_collection')
        projDir = config.get('directory', 'projDir')

        # path to shapefiles
        outlet_fullpath = config.get('input_files', 'outlet_fullpath')
        wshedBoundary = config.get('input_files', 'wshedBoundary')

        # path to other variables
        areaThreshold = config.get('other_parameter', 'areaThreshold')
        inUsername = config.get('other_parameter', 'inUsername')
        inPassword = config.get('other_parameter', 'inPassword')
        bufferDi = config.get('other_parameter', 'bufferDi')
        cell_size = config.get('other_parameter', 'cell_size')
        outCS = config.get('other_parameter', 'outCS')

        # output
        tiff_folder = config.get('output', 'tiff_folder')

        # flags, which help decide whether or no
        download_data = config.get('flags', 'download_data')
        process_dem = config.get('flags', 'process_dem')
        extract_ssurgo_data = config.get('flags', 'extract_ssurgo_data')
        merge_ssurgo_to_raster = config.get('flags', 'merge_ssurgo_to_raster')

        del_downloaded_files = config.get('flags', 'del_downloaded_files')
        del_ssurgo_files = config.get('flags', 'del_ssurgo_files')
        del_demProcessed_files = config.get('flags', 'del_demProcessed_files')


    # list of empty directories to be made
    folders_to_create = ['DEM_processed_rasters', 'SSURGO_rasters', 'TIFFS']

    # Out Directories
    raw_files_outDir = os.path.join(projDir, "Raw_files.gdb")
    downloads_outDir = os.path.join(projDir, "Downloads.gdb")
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
            arcpy.CreateFileGDB_management(projDir, "Downloads.gdb")

    except Exception, e:
        arcpy.AddMessage(e)

    arcpy.env.workspace = arcpy.env.scratchWorkspace = projDir

    if download_data.lower() == 'true':
        # Step1, download the data
        step1_get_dem_landuse(inUsername,inPassword,downloads_outDir ,wshedBoundary,bufferDi, outCS)

    if process_dem.lower() == 'true':
        # Step2
        DEM_fullpath = os.path.join(downloads_outDir, "DEM_Prj")
        land_use_fullpath = os.path.join(downloads_outDir, "Land_Use_Prj")

        if download_data.lower() == 'false':
            DEM_fullpath = os.path.join(downloads_outDir, "DEM")
            land_use_fullpath = os.path.join(downloads_outDir, "Land_Use")

        step2_dem_processing(DEM_fullpath, land_use_fullpath ,raw_files_outDir , outlet_fullpath, areaThreshold,cell_size, outCS)

    if extract_ssurgo_data.lower() == 'true':
        # Step3
        try:
            from STEP3_Merge_SSURGO import step3_merge_ssurgo
            lookupTable = os.path.join(os.getcwd(), "GREENAMPT_LOOKUPTABLE.csv")
            step3_merge_ssurgo(path2ssurgoFolders ,path2lookupTable=lookupTable )
            step3_merge_ssurgo(path2statsgoFolders ,path2lookupTable=lookupTable )
        except Exception,e:
            arcpy.AddMessage(e)

    if merge_ssurgo_to_raster.lower() == 'true':
        # Step4
        MatchRaster = os.path.join(raw_files_outDir, "mask_r")
        STEP4_Join_Merge_Export (path2ssurgoFolders, path2statsgoFolders, ssurgo_outDir, MatchRaster )

    # To tif, and flt
    for outRaster in ["mask_r", "DEM_Prj_fc",  "n_Overland", "n_Channel", "fdr_cr" , "slope_c", "SD", "str_c", "str_cr9999", "str_cr255"]:
        arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(raw_files_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

    for outRaster in ["bbl-tc.tif", "efpo-tc.tif", "ksat-tc.tif",  "psd-tc.tif", "por-tc.tif", "rsm-tc.tif" ]:
        arcpy.RasterToOtherFormat_conversion(Input_Rasters="'%s'"%(os.path.join(ssurgo_outDir, outRaster)), Output_Workspace=tiffs_outDir, Raster_Format="TIFF")

    # delete unnecessary files
    # unnecessary files in TIF folder, that are not tif
    for file in os.listdir(tiffs_outDir):
        if not file.split(".")[-1] in ['tif', "gdb", "xlsx"] :
            os.remove(os.path.join(tiffs_outDir,file))
    for file in os.listdir(ssurgo_outDir):
        if file.split(".")[-1] in ['tif' , 'TEMP']:
            os.remove(os.path.join(ssurgo_outDir,file))

    # copy files
    try:
        # tif_folder = folder where tiff are supposed to be saved for pytopkapi
        # tif_outDir = folder where tiff are created by the script above
        if not os.path.exists(tiff_folder):
            os.mkdir(tiff_folder)
        for file in os.listdir(tiffs_outDir):
            shutil.copy(os.path.join(tiffs_outDir,file), tiff_folder)

        # del downloaded files
        if del_downloaded_files.lower()== 'true':
            shutil.rmtree(downloads_outDir, ignore_errors=True)
            # for file in os.listdir(downloads_outDir):
            #     os.remove(os.path.join(downloads_outDir, file))
            # os.rmdir(downloads_outDir)

        # del DEM processed file
        if del_ssurgo_files.lower()== 'true':
            shutil.rmtree(raw_files_outDir, ignore_errors=True)

        # del SSURGO files
        if del_demProcessed_files.lower()== 'true':
            shutil.rmtree(ssurgo_outDir, ignore_errors=True)
    except Exception, e:
        arcpy.AddMessage( "FAILURE: Deleting temporary files. Error: %s"%e)
    return "SUCCESS: Input Raster files creation"


if __name__ == '__main__':
    initialize_fname = "./Onion_simulation.ini"
    topkapi_simulation_folder = "E:/trial_sim"
    tiff_folder = '../../simulations/Onion_1/create_the_parameter_files/TIFFS_500'
    daily_ppt_file = "../../simulations/Onion_1/run_the_model/forcing_variables/ppt.txt"

    # step0(initialize_fname)

    # create_config_files_create_file(topkapi_simulation_folder,tiff_folder)
    # create_global_param(topkapi_simulation_folder, A_thres=25000000, X=500, Dt=86400, W_min=1., W_Max=10.)
    # create_config_files_zero_slope_mngmt(topkapi_simulation_folder, 500)
    #
    # create_cell_param( topkapi_simulation_folder+'/create_file.ini', topkapi_simulation_folder+'/zero_slope_management.ini')
    #
    # outletID, no_of_cell = get_outletID_noOfCell(os.path.join(topkapi_simulation_folder,"cell_param.dat"))
    #
    #
    # create_config_files_plot_flow_precip(topkapi_simulation_folder, outletID ,calibration_start_data='01/01/2015' )
    # create_config_files_plot_soil_moisture_map(topkapi_simulation_folder,t1=1, t2=5, variable=4, fac_L=1., fac_Ks=1., fac_n_o=1., fac_n_c=1. )
    #
    # # create_cell_param( topkapi_simulation_folder+"/create_file.ini", topkapi_simulation_folder+'/zero_slope_management.ini')
    # create_global_param(topkapi_simulation_folder, A_thres=25000000, X=30.92208078, Dt=86400, W_min=1., W_Max=10.) # better to have in inside step0
    # create_rain_ET_file(topkapi_simulation_folder, total_no_of_cell=no_of_cell,ppt_file_txt= daily_ppt_file )
    #
    # create_config_files_TOPKAPI_ini(topkapi_simulation_folder, append_output_binary = 'False',fac_L = 1.4, fac_Ks = 1. ,fac_n_o  = 1. ,fac_n_c  = 1., fac_th_s = 1 )

    # run the program now
    import sys
    sys.path.append('../../PyTOPKAPI')
    import pytopkapi

    pytopkapi.run(topkapi_simulation_folder+'/TOPKAPI.ini')

    # plot
    from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps

    # Plot the hydrograph
    plot_Qsim_Qobs_Rain.run(topkapi_simulation_folder+'/plot-flow-precip.ini')
