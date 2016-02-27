'''
The purpose of this script is to convert FDR tiff's into connectivity rasters
'''

import numpy
from osgeo import gdal
import argparse
import os, sys
from multiprocessing import Process
import time



def new_raster_from_base(base, output, output_data, nodata=-9999, datatype=gdal.GDT_Int32):
    """
    creates and empty raster object using a base raster as a template. Note this function assumes only a single raster band GeoTiff output
    http://gis.stackexchange.com/questions/31568/gdal-rasterizelayer-doesnt-burn-all-polygons-to-raster
    :param base: base raster layer to use as a template, opened as gdal object
    :param output: output path for the new raster
    :param output_data: numpy array of the data to set in the output raster
    :param nodata: nodata value (e.g. -1, -9999) 
    :param datatype: value datatype (e.g. gdal.GDT_Int32)
    :return: empty raster object
    """

    # grab the projection, transformation from the base
    projection = base.GetProjection()
    geotransform = base.GetGeoTransform()

    # create a new raster from the base image
    driver = gdal.GetDriverByName('GTiff')
    r,c = output_data.shape
    new_raster = driver.Create(str(output), c, r, 1, datatype, options =['PHOTOMETRIC=MINISBLACK'])
    new_raster.SetProjection(projection)
    new_raster.SetGeoTransform(geotransform)
   
    # set nodata, and datavalues
    new_raster.GetRasterBand(1).SetNoDataValue(nodata)
    new_raster.GetRasterBand(1).WriteArray(output_data)
    new_raster.FlushCache()
    return new_raster


def calc_connectivity_coords(fdr, value, rdiff, cdiff):
   
    # get all raster values that match the desired value
    r,c  = numpy.where(fdr == value)
    
    # calculate the new coordinate values
    to_c = c + cdiff
    to_r = r + rdiff

    # get the min and max array indices
    xmax, xmin = (fdr.shape[1], -1)
    ymax, ymin = (fdr.shape[0], -1)

    # check if each x, y coordinate is within the min and max array indixes
    x_isvalid = numpy.logical_and(to_c > xmin, to_c < xmax)
    y_isvalid = numpy.logical_and(to_r > ymin, to_r < ymax)

    # select the coordinates where both x and y indices are valid
    isvalid = numpy.logical_and(x_isvalid, y_isvalid)

    # only select the new coordinates that are valid
    valid_to_coordinates = numpy.array(zip(to_r,to_c))[isvalid]
    valid_from_coordinates = numpy.array(zip(r,c))[isvalid]

    # return lists of valid_from and valid_to coordinates
    return zip(*valid_from_coordinates), zip(*valid_to_coordinates)


def save(fdr_raster, out, out_path):

    try:
        # save results in new GTiff
        new_raster_from_base(fdr_raster, out_path, out)
    except Exception, e:
        print 'Encountered and error while saving the connectivity results: %s' % e
        sys.exit(1)

def spinning_cursor():
    """
    Just a function that will give a spinning cursor to illustrate that the script is working
    :return: next cursor position
    """
    while True:
        for cursor in '|/-\\':
            yield cursor

def connectivity(fdr_tiff_path, out_tiff_path):
    
    print 'reading the geotiff and building numpy arrays'
    # read the input geotiff as a numpy array 
    ds = gdal.Open(fdr_tiff_path)
    fdr = numpy.array(ds.GetRasterBand(1).ReadAsArray())

    # build index array
    ids = numpy.arange(1, fdr.size + 1, 1)
    ids = numpy.reshape(ids, fdr.shape)

    # build output array (initialize to -9999)
    out = numpy.full(fdr.shape, -9999, numpy.int32)

    cases = [   (1, 1, 0),      # case 1
                (2, 1, 1),      # case 2
                (4, 0, 1),      # case 4
                (8, -1, 1),    # case 8
                (16, -1, 0),    # case 16
                (32, -1, -1),    # case 32
                (64, 0, -1),    # case 64
                (128, 1, -1)]   # case 128

    # evaluate each case
    for value, xdiff, ydiff in cases:
        print 'determining connectivity for fdr = %d' % value
        fcoords, tcoords = calc_connectivity_coords(fdr, value, ydiff, xdiff)
        if len(tcoords) > 0:
            out[fcoords] = ids[tcoords]
    
    # save the results using a separate processing since this can freeze the terminal 
    proc = Process(target=save, args=(gdal.Open(fdr_tiff_path), out, out_tiff_path))
    proc.start()
    spinner = spinning_cursor()
    while proc.is_alive():
        message = 'saving connectivity results to GeoTiff ' + spinner.next()
        sys.stdout.write('\r' + str(message))
        sys.stdout.flush()
        time.sleep(0.1)
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
    
    print '\n#'
    print '# Build Connectivity Completed Successfully'
    print '#'
    print '# output saved to %s' % args.output
    print '#                 %s' % args.output
    print '#'





