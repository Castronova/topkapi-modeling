import gdal
# write numpy array to tif
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
import matplotlib.pylab as plt

input_raster = r"C:\Users\WIN10-HOME\Downloads\tif\CAP_Landuse_1985.tif"
output_tiff=r"C:\Users\WIN10-HOME\Downloads\tif\hello.tiff"

def read_tiff_as_numpy_array(input_raster):
    ds = gdal.Open(input_raster)
    raster_as_array = ds.GetRasterBand(1).ReadAsArray()
    return raster_as_array

def write_numpy_array_to_tiff(array, xy_min_xy_max, output_tiff):
    """
    :param array:
    :param xy_min_xy_max: [xmax, xmin, ymax, ymin]
    :param output_tiff:
    :return:
    """

    xmax, xmin, ymax, ymin = xy_min_xy_max

    nrows, ncols = np.shape(array)
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform=(xmin,xres,0,ymax,0, -yres)
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),
    #         top left y, rotation (0 if North is up), n-s pixel resolution)
    # I don't know why rotation is in twice???

    output_raster = gdal.GetDriverByName('GTiff').Create(output_tiff,ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    #srs = osr.SpatialReference()                 # Establish its coordinate encoding
    #srs.ImportFromEPSG(4326)                     # This one specifies WGS84 lat long.
                                                 # Anyone know how to specify the
                                                 # IAU2000:49900 Mars encoding?
    #output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system
                                                       # to the file
    output_raster.GetRasterBand(1).WriteArray(array)   # Writes my array to the raster
    return

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

array = read_tiff_as_numpy_array(input_raster)
new_raster_from_base(input_raster, output_tiff, array)

#write_numpy_array_to_tiff(array, output_tiff)