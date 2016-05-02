
##### my code #####
import os, h5py , numpy
os.chdir(r'E:\Dropbox\CLASSES\Hydroinformatics\PyProject_HI\PROJECT_RESEARCH\TOPKAPI_Example\run_the_model\forcing_variables')

with h5py.File('rainfields_RedButteCreek.h5','w') as f2:
    f2.create_group('sample_event')
    f2['sample_event'].create_dataset('rainfall', shape=(170, 87322), dtype='f' )

    rainArray =  f2['sample_event']['rainfall']
    data = []
    for i in range(170):
        no_cell = 87323
        one_time_ppt_all_cell = numpy.random.rand(no_cell,1)* i
        data.append(one_time_ppt_all_cell)

    rainArray = data



with h5py.File('ET_RedButteCreek.h5','w' ) as f1:
    f1.create_group('sample_event')
    f1['sample_event'].create_dataset('ETo', shape=( 170, 87323), dtype='f' )
    f1['sample_event'].create_dataset('ETr', shape=( 170, 87323), dtype='f' )

    EToArray =  f1['sample_event']['ETo']
    ETrArray =  f1['sample_event']['ETr']

    data = []
    for i in range(170):
        no_cell = 87323
        one_time_ppt_all_cell = numpy.random.rand(no_cell,1)* i
        data.append(one_time_ppt_all_cell)

    EToArray = data
    ETrArray = data

