import os
import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps



execpath = os.getcwd()

path = os.path.join(execpath,'run_the_model')
os.chdir(path)

pytopkapi.run('TOPKAPI.ini')

plot_Qsim_Qobs_Rain.run('plot-flow-precip.ini')

#plot_soil_moisture_maps.run('plot-soil-moisture-maps.ini')
