'''
The purpose of this script is to convert FDR tiff's into connectivity rasters
'''

import numpy
from osgeo import gdal
import argparse
import os, sys
from multiprocessing import Process
import time


def calc_connectivity_coords(fdr, value, rdiff, cdiff):
   
    # get all raster values that match the desired value
    r,c  = numpy.where(fdr == value)
    
    # calculate the new coordinate values
    to_c = c + cdiff
    to_r = r + rdiff

    # find all values that are within the min and max coordinate indices
    xmax, xmin = (fdr.shape[1], -1)
    ymax, ymin = (fdr.shape[0], -1)
    xmatches = numpy.logical_and(to_c > xmin, to_c < xmax)
    ymatches = numpy.logical_and(to_r > ymin, to_r < ymax)
    matches = numpy.logical_and.reduce((xmatches, ymatches))
    to_coordinates = numpy.array(zip(to_r,to_c))[matches]
    from_coordinates = numpy.array(zip(r,c))[matches]

    return zip(*from_coordinates), zip(*to_coordinates)

def save(ids, out, out_path):

    try:
        # save results
        with open(out_path, 'w') as f:
            flat_ids = numpy.reshape(ids, (ids.size, 1))
            flat_out = numpy.reshape(out, (out.size, 1))
            a = numpy.hstack([flat_ids, flat_out])
            numpy.savetxt(f, a, fmt='%d', delimiter=' ')     
    except:
        print 'Encountered and error while saving the connectivity results'
        sys.exit(1)


def connectivity(fdr_tiff_path, out_tiff_path):
    
    print 'reading the geotiff and building numpy arrays'
    # read the input geotiff as a numpy array 
    ds = gdal.Open(fdr_tiff_path)
    fdr = numpy.array(ds.GetRasterBand(1).ReadAsArray())

    # build index array
    ids = numpy.arange(1, fdr.size + 1, 1)
    ids = numpy.reshape(ids, fdr.shape)

 #   # build output array (initialize to -9999)
    out = numpy.full(fdr.shape, -9999)

    cases = [   (1, 1, 0),      # case 1
                (2, 1, 1),      # case 2
                (4, 0, 1),      # case 4
                (8, -1, 1),     # case 8
                (16, -1, 0),    # case 16
                (32, -1, -1),   # case 32
                (64, 0, -1),    # case 64
                (128, 1, -1)]   # case 128

    # evaluate each case
    for value, xdiff, ydiff in cases:
        print 'determining connectivity for fdr = %d' % value
        fcoords, tcoords = calc_connectivity_coords(fdr, value, ydiff, xdiff)
        if len(tcoords) > 0:
            out[fcoords] = ids[tcoords]
    
    # save the results using a separate processing since this can freeze the terminal
    
    sys.stdout.write('saving connectivity results ')
    proc = Process(target=save, args=(ids, out, out_tiff_path))
    proc.start()
    while proc.is_alive():
        time.sleep(.5)
        sys.stdout.write('.')
        sys.stdout.flush()
    proc.join()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help="input flow direction GeoTiff")
    parser.add_argument('-o', '--output', required=True, help="output flow direction connectivity ascii file")
    args = parser.parse_args()

    if os.path.exists(args.output):
        response = raw_input('Output file already exists. Do you want to delete it? [Y/n]')

        # delete the file
        if response != 'n':
            os.remove(args.output)

    if not os.path.exists(args.input):
        print 'Could not find input fdr GeoTiff, please make sure the path is correct'
        sys.exit(1)

    try:
        gdal.Open(args.input)
    except:
        print 'An error was encountered when reading the input fdr GeoTiff.  Make sure that this file is in GeoTiff format.' 
        sys.exit(1) 

    connectivity(args.input, args.output)
    
    print '#'
    print '# Build Connectivity Completed Successfully'
    print '#'
    print '# output saved to ', args.output
    print '#'
    print '# to view the results use '
    print '#    less %s' % args.output
    print '#'





