import sys
import time
import numpy
from osgeo import gdal
import argparse
import os

def ascii2row(asciiRaster):
    itemsInaList=[]
    c=1
    with open(asciiRaster) as fp:
        for line in fp:
            c=c+1
            tempList = line.strip().split(" ")
            if c > 7:
                for item in tempList:
                    if item != str(-9999):
                        itemsInaList.append(item)

    data = numpy.array(itemsInaList)

    return data.reshape(data.shape[0], 1)

def flatten_tiff(tifpath):
    # read the tif file
    ds = gdal.Open(tifpath)

    # read all the data
    data = numpy.array(ds.GetRasterBand(1).ReadAsArray())

    # filter out the nodata values
    data = data[data >= -100]

    # reshape the data into a single column
    data = data.reshape(data.shape[0], 1)

    return data


#----
path_2_tiffs = r"C:\Users\Prasanna\Box Sync\Red Butte Creek rasters2\TIFFs"
path_2_tiffs= r"C:\Users\Prasanna\Box Sync\Red Butte Creek rastrers6\Tiffs"
path_2_tiffs= r"C:\Users\WIN10-HOME\OneDrive\Public\topkapi-modeling\simulations\TEST SIMULAITON5\create_the_parameter_files\Tiffs"

input_files = ["mask2.tif", "str.tif" ,'DEM_Prj.tif', 'fdr.tif',  "drp.tif", "soildepth.tif", 'resmoisture.tif' ,
               'effporosity.tif','n_Overland.tif', 'n_Channel.tif', 'Land_Use_Prj.tif', 'poresize.tif',
               'bblingpr.tif' , 'kc_fake.tif', 'ksat.tif']

# list of TIF in a different way, all tif from a specified folder
os.chdir(path_2_tiffs)
all_Files = os.listdir(path_2_tiffs)
input_files = []
for file in all_Files:
    if file.split(".")[-1] == 'tif':
        input_files.append(file)


output_file = "cell_param.dat"

if os.path.exists(output_file):
    response = raw_input('Output file already exists. Do you want to delete it? [Y/n]')

    # delete the file
    if response != 'n':
        os.remove(output_file)
data = []

for a_File in input_files:
    data.append(flatten_tiff(a_File))
    print "%s is written and contains %s values " % (a_File,len(flatten_tiff(a_File)))


# write the output
with open(output_file, 'w') as f:
    for i in range(len(data)):
        if data[i].dtype != 'float':
            data[i] = data[i].astype('float')

    # build the output array
    outarr = data[0]
    for i in range(1, len(data)):
        outarr = numpy.hstack([outarr, data[i]])

    # save outarr to text file
    numpy.savetxt(f, outarr, fmt='%1.3f', delimiter=' ')


print 'Data Flattening Completed Successfully'










#-------------------------------------------------------------
#
# if __name__ == "__main__":
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-t', '--type', required=True, choices=['tiff', 'ascii'], help="input file type (tiff or ascii)  [REQUIRED]")
#     parser.add_argument('-o', '--output', required=True, help="path to output file [REQUIRED]")
#     parser.add_argument('-i', '--inputs', required=True, nargs='*', help="input files to process [REQUIRED]")
#     parser.add_argument('--runtests', action='store_true', help="run tests")
#     args = parser.parse_args()
#
#     if os.path.exists(args.output):
#         response = raw_input('Output file already exists. Do you want to delete it? [Y/n]')
#
#         # delete the file
#         if response != 'n':
#             os.remove(args.output)
#     data = []
#     if args.type == 'tiff':
#         for i in range(len(args.inputs)):
#             data.append(flatten_tiff(args.inputs[i]))
#             print "%s is written and contains %s values " % (args.inputs[i],len(flatten_tiff(args.inputs[i])))
#
#     elif args.type == 'ascii':
#         for i in range(len(args.inputs)):
#            data.append(ascii2row(args.inputs[i]))
#
#     # write the output
#     with open(args.output, 'w') as f:
#         for i in range(len(data)):
#             if data[i].dtype != 'float':
#                 data[i] = data[i].astype('float')
#
#         # build the output array
#         outarr = data[0]
#         for i in range(1, len(data)):
#             outarr = numpy.hstack([outarr, data[i]])
#
#         # save outarr to text file
#         numpy.savetxt(f, outarr, fmt='%1.3f', delimiter=' ')
#
#
#     print 'Data Flattening Completed Successfully'
