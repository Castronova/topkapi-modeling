

##### my code #####
import os, h5py , numpy

path = "../simulations/TEST SIMULAITON_RBC6/run_the_model/forcing_variables"
rainfall_outputFile = os.path.join(path, "rainfields_RBC.h5")
ET_outputFile = os.path.join(path, "ET_RBC.h5")

time_step = 20 #161
no_of_cell = 19765
rainfall_intensity_perUnitTime = 3  #mm

with h5py.File(rainfall_outputFile,'w') as f2:
    f2.create_group('sample_event')
    f2['sample_event'].create_dataset('rainfall', shape=(time_step, no_of_cell), dtype='f' )

    rainArray =  f2['sample_event']['rainfall']
    data = numpy.zeros((time_step , no_of_cell))
    for i in range(time_step):
        a = numpy.empty( (1,no_of_cell ) )
        a.fill(rainfall_intensity_perUnitTime)  #
        data[i,:] = a

    rainArray[:] = data



with h5py.File(ET_outputFile,'w' ) as f1:
    f1.create_group('sample_event')
    f1['sample_event'].create_dataset('ETo', shape=( time_step, no_of_cell), dtype='f' )
    f1['sample_event'].create_dataset('ETr', shape=( time_step, no_of_cell), dtype='f' )

    EToArray =  f1['sample_event']['ETo']
    ETrArray =  f1['sample_event']['ETr']

    data = numpy.zeros((time_step , no_of_cell))
    for i in range(time_step):
        data[i,:] = numpy.random.rand(1,no_of_cell)*0.

    EToArray = data
    ETrArray = data


# Read and write Below
# with h5py.File(ET_outputFile,'w' ) as f1:
#     f1.create_group('sample_event')
#     f1['sample_event'].create_dataset('ETo', shape=( time_step, no_of_cell), dtype='f' )
#     f1['sample_event'].create_dataset('ETr', shape=( time_step, no_of_cell), dtype='f' )
#
#     EToArray =  f1['sample_event']['ETo']
#     ETrArray =  f1['sample_event']['ETr']
#
#     data = []
#     for i in range(time_step):
#         one_time_ppt_all_cell = numpy.random.rand(no_of_cell,1)*0.1
#         data.append(one_time_ppt_all_cell)
#
#     EToArray = data
#     ETrArray = data
#
# #reading usmmary
# et_h5 = h5py.File("ET.h5" , "r")
# et_h5['sample_event']['ETr'][:]
#
# rain_h5 = h5py.File('rainfields.h5')
# rain_h5['sample_event']['rainfall'][:]
#
# h5py.File('rainfields_sampleWatershed.h5',"r")['sample_event']['rainfall']
# h5py.File('rainfields_sampleWatershed.h5',"r").close()
#
# ###########
# # READING #
# ###########
# os.chdir(r'C:\Users\Prasanna\Google Drive\SharedWithDrCastronova\2016\PyCharmWorkspace\FEB\NL_C03_2\run_the_model\forcing_variables')
#
# # open the file that we created above
# f = h5py.File("ET.h5", "r")
# print '\nf is an h5py File: ',(type(f) == h5py.File)
# print 'f contains elements: ',f.keys()
#
# # get the group
# grp = f['sample_event']
# print '\ngrp is an h5py Group: ',(type(grp) == h5py.Group)
# print 'grp contains elements: ', grp.keys()
#
# # get the dataset
# dset = grp['ETo']
# print '\ndset is an h5py File: ',(type(dset) == h5py.Dataset)
# print 'dset has a shape of: ', dset.shape
#
# # get the data using array indexing
# print '\t',dset[:]
# print '\t',dset[:-4]
# print '\t',dset[:5]
# print '\t',dset[0:2]
# f['sample_event']['ETo'].shape


# f.close()
#
#
#
#
#
#
#
# # ############################################
# # #Reading and writing h5, by Dr. Castronova
# ############################################
# #
# # # This script demonstrates how to build hdf5 files from timeseries data
# # # Most of this content was derived from http://docs.h5py.org/en/latest/quick.html
# #
# #
# # import h5py
# #
# # ###########
# # # WRITING #
# # ###########
# #
# # # create an empty hdf5 file
# # f = h5py.File("mytestfile.h5","w")
# #
# # # create a group
# # #   * a group is a container that can hold multiple datasets
# # grp = f.create_group("climate_data")
# #
# # # add a dataset to the group
# # #   * (10,) indicates the size of the data (rows, cols)
# # #   * dtype indicates the type of data that will be stored 'f' = float
# # dset = grp.create_dataset('prcp', (10,), dtype='f')
# #
# # # NOTE: the group and dataset can be accomplished in a single statement
# # #   create_dataset('climate_data/prcp').
# #
# # # add some data values to the dataset
# # values = range(10)
# # dset[:] = values
# #
# # f.close()
# #
# # # ----------------------------------------------------------------------
# #
# # ###########
# # # READING #
# # ###########
# #
# # # open the file that we created above
# # f = h5py.File("mytestfile.h5", "r")
# # print '\nf is an h5py File: ',(type(f) == h5py.File)
# # print 'f contains elements: ',f.keys()
# #
# # # get the group
# # grp = f['climate_data']
# # print '\ngrp is an h5py Group: ',(type(grp) == h5py.Group)
# # print 'grp contains elements: ', grp.keys()
# #
# # # get the dataset
# # dset = grp['prcp']
# # print '\ndset is an h5py File: ',(type(dset) == h5py.Dataset)
# # print 'dset has a shape of: ', dset.shape
# #
# # # get the data using array indexing
# # print '\t',dset[:]
# # print '\t',dset[:-4]
# # print '\t',dset[:5]
# # print '\t',dset[0:2]
# #
# # f.close()
# #
# # # ----------------------------------------------------------------------
# #
# # ####################
# # # ADVANCED WRITING #
# # ####################
# #
# # import numpy
# #
# # # create some data
# # data = numpy.random.rand(10,10)
# #
# # # open the file
# # with h5py.File('mytestfile2.h5', 'w') as f:
# #     # create group and dataset in one line
# #     dset = f.create_dataset('climate_data/prcp', shape=(10,10), dtype='f')
# #
# #     # set the datavalues for this group
# #     dset[:] = data
# #
# # # check that the data was set properly
# # with h5py.File("mytestfile2.h5", "r") as f:
# #     print '\nf is an h5py File: ',(type(f) == h5py.File)
# #     print 'f contains elements: ',f.keys()
# #
# #     grp = f['climate_data']
# #     print '\ngrp is an h5py Group: ',(type(grp) == h5py.Group)
# #     print 'grp contains elements: ', grp.keys()
# #
# #     dset = grp['prcp']
# #     print '\ndset is an h5py File: ',(type(dset) == h5py.Dataset)
# #     print 'dset has a shape of: ', dset.shape
# #
# #     print '\nData Querying'
# #     print dset[0,:]
# #     print '\n', dset[1:4,1:4]
# #     print '\n',dset[:,1]
# #
