from ConfigParser import SafeConfigParser
import ConfigParser

ini_fname = "./Pytopkapi_simulation.ini"

config = SafeConfigParser()
config.read(ini_fname)

path2ssurgoFolders = config.get('directory', 'ssurgo_collection')
path2statsgoFolders = config.get('directory', 'statsgo_collection')
projDir = config.get('directory', 'projDir')

outlet_fullpath = config.get('input_files', 'outlet_fullpath')
wshedBoundary = config.get('input_files', 'wshedBoundary')

threshold = config.get('other_parameter', 'threshold')
inUsername = config.get('other_parameter', 'inUsername')
inPassword = config.get('other_parameter', 'inPassword')
bufferDi = config.get('other_parameter', 'bufferDi')
cell_size = config.get('other_parameter', 'cell_size')
outCS = config.get('other_parameter', 'outCS')

all = [path2ssurgoFolders,path2statsgoFolders , projDir, outlet_fullpath,wshedBoundary,
       threshold, inUsername, inPassword, bufferDi, cell_size, outCS]

for i in all:
    print i

import os
os.chdir(projDir)
# configWrite = ConfigParser.RawConfigParser()
# configWrite.add_section('Input')
# configWrite.set('Input', 'ProjectDir', "c:/")
# configWrite.set('Input', 'Inlet', "blabla")
# configWrite.add_section('Output')
# configWrite.set('Output', 'ProjectDir', "D:/")
#
# with open('example.ini', 'wb') as configFile:
#     configWrite.write(configFile)
