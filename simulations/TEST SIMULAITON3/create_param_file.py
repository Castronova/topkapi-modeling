import pytopkapi
import os
import inspect

from pytopkapi.parameter_utils.create_file import generate_param_file

fn_ini = 'create_the_parameter_files/create_file_3_1.ini'

generate_param_file(fn_ini, isolated_cells=False)

