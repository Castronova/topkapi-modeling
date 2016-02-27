import pytopkapi
import os
import inspect

from pytopkapi.parameter_utils.create_file import generate_param_file

filename = inspect.getframeinfo(inspect.currentframe()).filename
execpath = os.path.dirname(os.path.abspath(filename))
drive_letter  = execpath[0]

execpath = r"C:\Users\Prasanna\Google Drive\RESEARCH\SharedWithDrCastronova\2016\PyCharmWorkspace\FEB\NL_C03_2"
os.chdir(execpath)

fn_ini = 'create_the_parameter_files/create_file_2.ini'

generate_param_file(fn_ini, isolated_cells=False)

