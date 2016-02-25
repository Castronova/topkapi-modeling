import os
import pytopkapi
from pytopkapi.results_analysis import plot_Qsim_Qobs_Rain, plot_soil_moisture_maps
import inspect

filename = inspect.getframeinfo(inspect.currentframe()).filename
execpath = os.path.dirname(os.path.abspath(filename))
drive_letter  = execpath[0]

#execpath = r"C:\Users\Prasanna\Google Drive\SharedWithDrCastronova\2016\PyCharmWorkspace\FEB\NL_C03_2"

os.chdir(execpath +'\\run_the_model\\')

pytopkapi.run('TOPKAPI.ini')

plot_Qsim_Qobs_Rain.run('plot-flow-precip.ini')

#plot_soil_moisture_maps.run('plot-soil-moisture-maps.ini')