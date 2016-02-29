import pytopkapi
import os
import inspect

from pytopkapi.parameter_utils.create_file import generate_param_file

# filename = inspect.getframeinfo(inspect.currentframe()).filename
# execpath = os.path.dirname(os.path.abspath(filename))
# drive_letter  = execpath[0]

execpath = os.getcwd()
os.chdir(execpath)

fn_ini = 'create_the_parameter_files/create_file_6.ini'

generate_param_file(fn_ini, isolated_cells=False)

