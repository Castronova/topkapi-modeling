

##### my code #####
import os, h5py, numpy

# path = "../simulations/TEST SIMULAITON_RBC_demo/run_the_model/forcing_variables"
path = "../../simulations/RBC_3/run_the_model/forcing_variables"
daily_ppt_file = "../../simulations/RBC_3/run_the_model/forcing_variables/ppt.txt"

# output path
rainfall_outputFile = os.path.join(path, "rainfields.h5")
ET_outputFile = os.path.join(path, "ET.h5")

time_step = 59 #161
no_of_cell = 3400
# rainfall_intensity_perUnitTime = 20 #mm
rainfall_reduction_factor = 1

# 1_del (for removing file readings)
rain_from_file = numpy.genfromtxt(daily_ppt_file, delimiter='\t')

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






# ### working, June 25, 2016
#
#
# ##### my code #####
# import os, h5py , numpy
#
# # path = "../simulations/TEST SIMULAITON_RBC_demo/run_the_model/forcing_variables"
# # path = r"../../simulations/RBC_2/run_the_model/forcing_variables"
# path = "."
# rainfall_outputFile = os.path.join(path, "rainfields_RBC.h5")
# ET_outputFile = os.path.join(path, "ET_RBC.h5")
#
# time_step = 20 #161
# no_of_cell = 19765
# rainfall_intensity_perUnitTime = 10 #mm
#
# with h5py.File(rainfall_outputFile,'w') as f2:
#     f2.create_group('sample_event')
#     f2['sample_event'].create_dataset('rainfall', shape=(time_step, no_of_cell), dtype='f' )
#
#     rainArray =  f2['sample_event']['rainfall']
#     data = numpy.zeros((time_step , no_of_cell))
#     for i in range(time_step):
#         a = numpy.empty( (1,no_of_cell ) )
#         a.fill(rainfall_intensity_perUnitTime)  #
#         data[i,:] = a
#
#     data[0,:] = numpy.zeros((1,no_of_cell))
#     data[time_step/4,:] = numpy.zeros((1,no_of_cell))
#     data[time_step/2,:] = numpy.zeros((1,no_of_cell))
#     data[time_step/3,:] = numpy.zeros((1,no_of_cell))
#     rainArray[:] = data
#
#
#
# with h5py.File(ET_outputFile,'w' ) as f1:
#     f1.create_group('sample_event')
#     f1['sample_event'].create_dataset('ETo', shape=( time_step, no_of_cell), dtype='f' )
#     f1['sample_event'].create_dataset('ETr', shape=( time_step, no_of_cell), dtype='f' )
#
#     EToArray =  f1['sample_event']['ETo']
#     ETrArray =  f1['sample_event']['ETr']
#
#     data = numpy.zeros((time_step , no_of_cell))
#     for i in range(time_step):
#         data[i,:] = numpy.random.rand(1,no_of_cell)*0.0
#
#     EToArray = data
#     ETrArray = data
