import sys
sys.path.append('../../PyTOPKAPI')

import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps
from pytopkapi.parameter_utils.create_file import generate_param_file
from pytopkapi.parameter_utils import modify_file
import os


fn_ini = 'create_the_parameter_files/create_file.ini'
#
# # Generate Parameter Files
# generate_param_file(fn_ini, isolated_cells=False)
# print "Cell Parameter file created"
#
# # slope corrections
# modify_file.zero_slope_management('create_the_parameter_files/zero_slope_management.ini')
# print "Zero Slope corrections made"

# # run the model
pytopkapi.run('./run_the_model/TOPKAPI.ini')

# Plot the hydrograph
plot_Qsim_Qobs_Rain.run('./run_the_model/plot-flow-precip.ini')

# # # Plot soil moisture
# plot_soil_moisture_maps.run('./run_the_model/plot-soil-moisture-maps.ini')
