
import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps
import os

os.chdir(r"C:\Users\WIN10-HOME\Documents\topkapi-modeling\simulations\TEST SIMULAITON5\run_the_model")

# pytopkapi.run('TOPKAPI.ini')

plot_Qsim_Qobs_Rain.run('plot-flow-precip.ini')

#plot_soil_moisture_maps.run('plot-soil-moisture-maps.ini')
