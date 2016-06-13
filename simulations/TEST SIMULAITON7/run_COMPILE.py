import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps
from pytopkapi.parameter_utils.create_file import generate_param_file
from pytopkapi.parameter_utils import modify_file
import os

# # os.chdir(r"C:\Users\Prasanna\Documents\GitHub\topkapi-modeling\simulations\TEST SIMULAITON6\run_the_model")
# fn_ini = r'create_the_parameter_files\create_file.ini'
#
# # Generate Parameter Files
# generate_param_file(fn_ini, isolated_cells=False)
# print "Cell Parameter file created"
#
# # slope corrections
# modify_file.zero_slope_management('create_the_parameter_files/zero_slope_management.ini')
# print "Zero Slope corrections made"
#
# run the model
os.chdir(r"C:\Users\WIN10-HOME\OneDrive\Public\topkapi-modeling\simulations\TEST SIMULAITON7\run_the_model")
pytopkapi.run('TOPKAPI.ini')

#Plot the hydrograph
os.chdir(r"C:\Users\WIN10-HOME\OneDrive\Public\topkapi-modeling\simulations\TEST SIMULAITON7\run_the_model")
plot_Qsim_Qobs_Rain.run('plot-flow-precip.ini')

# Plot soil moisture
os.chdir(r"C:\Users\WIN10-HOME\OneDrive\Public\topkapi-modeling\simulations\TEST SIMULAITON7\run_the_model")
plot_soil_moisture_maps.run('plot-soil-moisture-maps.ini')
