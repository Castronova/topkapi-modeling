'''
The purpose of this script is to convert FDR tiff's into connectivity rasters
'''

import numpy
from osgeo import gdal
import argparse
import os, sys
from multiprocessing import Process
import time

def new_raster_from_base(base, output, format, nodata, datatype):
    """
    creates and empty raster object using a base raster as a template
    http://gis.stackexchange.com/questions/31568/gdal-rasterizelayer-doesnt-burn-all-polygons-to-raster
    :param base: base raster layer to use as a template
    :param output: output raster object
    :param format: format of the raster object
    :param nodata: nodata value
    :param datatype: value datatype
    :return: empty raster object
    """

    projection = base.GetProjection()
    geotransform = base.GetGeoTransform()
    bands = base.RasterCount

    driver = gdal.GetDriverByName(format)
    r,c = base.GetRasterBand(1).ReadAsArray().shape
    new_raster = driver.Create(str(output), c, r, bands, datatype)
    new_raster.SetProjection(projection)
    new_raster.SetGeoTransform(geotransform)

    for i in range(bands):
        new_raster.GetRasterBand(i + 1).SetNoDataValue(nodata)
        new_raster.GetRasterBand(i + 1).Fill(nodata)

    return new_raster


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

def save(base, out, out_path):
    #base is fdr or tif input

    try:

        # #driver = gdal.GetDriverByName('GTiff')
        baseRaster = gdal.Open(base)
        rd = new_raster_from_base(baseRaster, out_path, 'GTiff', -9999, gdal.GDT_Int32)
        rd.GetRasterBand(1).WriteArray(out)
        rd.FlushCache()


        # # save results
        # with open(out_path, 'w') as f:
        #     flat_ids = numpy.reshape(ids, (ids.size, 1))
        #     flat_out = numpy.reshape(out, (out.size, 1))
        #     a = numpy.hstack([flat_ids, flat_out])
        #     numpy.savetxt(f, a, fmt='%d', delimiter=' ')
    except Exception, e:
        print e
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
    save(fdr_tiff_path, out, out_tiff_path)
    # proc = Process(target=save, args=(ids, out, out_tiff_path))
    # proc.start()
    # while proc.is_alive():
    #     time.sleep(.5)
    #     sys.stdout.write('.')
    #     sys.stdout.flush()
    # proc.join()

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





