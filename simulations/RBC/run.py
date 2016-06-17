import sys
sys.path.append('../../PyTOPKAPI')

import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps
import os
import h5py
# from PIL import Image

os.chdir("./run_the_model")

pytopkapi.run('TOPKAPI.ini')

plot_Qsim_Qobs_Rain.run('plot-flow-precip.ini')

plot_soil_moisture_maps.run('plot-soil-moisture-maps.ini')

# results
result_sim5 = h5py.File("../../simulations/TEST SIMULAITON5/run_the_model/results/results.h5")
channel_flows = result_sim5['Channel/Qc_out'][...]
flow = channel_flows[:,0]

soil_stores = result_sim5['Soil/V_s'][...]
soil = soil_stores[:, :10]

# channel_flow = result_sim5['Channel']['Qc_out'][:]
# w, h = channel_flow.shape
# img = Image.fromarray(channel_flow, 'RGB')
