import os
import h5py
import tables as h5
import numpy as np
import matplotlib.pyplot as plt

np.set_printoptions(formatter={'float': '{: 0.5f}'.format})

def compare_rainfall_file(example_rain, simulation_rain):
    """

    :param example_rain: path to example rainfields.h5
    :param simulation_rain: path to rainfall file used in the simulations
    :return:
    """
    eg_rain = h5py.File(example_rain , "r")
    sim_rain = h5py.File(simulation_rain, "r")

    print '*** Checking Keys ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain.keys(), sim_rain.keys())

    print '*** Checking the keys in the group "sample_event" ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain['sample_event'].keys(), sim_rain['sample_event'].keys())

    print '*** Checking the shape of the group "sample_event/rainfall" ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain['sample_event/rainfall'].shape, sim_rain['sample_event/rainfall'].shape)

    #~~~~Rainfall
    group_name = 'sample_event'
    h5file_in = h5.openFile(simulation_rain,mode='r')
    group = '/'+group_name+'/'
    node = h5file_in.getNode(group+'rainfall')
    ndar_rain = node.read()
    print ndar_rain
    h5file_in.close()

    return

def check_hdf5(hdf5_filename):
    with  h5py.File(hdf5_filename , "r") as f:

        print "The groups in the h5 files are: "
        for group in f.keys():
            print "\t\t" , group,
        # print items / tables inside the group

        for group in f.keys():
            print "\n the Items in the group %s are:"%group
            for table in f[group]:
                print "\t\t" , table

                print np.unique(f[group][table])
                plt.hist(f[group][table])
                plt.show()


eg_rain = "../../PyTOPKAPI/example_simulation/forcing_variables/rainfields.h5"
eg_ET = "../../PyTOPKAPI/example_simulation/forcing_variables/ET.h5"
sim_rain = "../../simulations/RBC/run_the_model/forcing_variables/rainfields_RBC.h5"

check_hdf5(eg_rain)