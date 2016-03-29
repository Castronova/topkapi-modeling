import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import pandas as pd
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def rainfall_in_station(file, stationName, date):
    '''
    :param file: csv file with columns Date, StationA, StationB, StationC as headers
    :param stationName: StationA, StationB or StationC
    :param date: in format yyyy/mm/dd
    :return: rainfall for a station and date chosen in the file
    '''
    rain_data = pd.read_csv(file, index_col = "Date" )
    rainfall = rain_data[stationName][date]
    return rainfall

def compute_cell_coordinates(mask_fname):
    dset = gdal.Open(mask_fname)
    mask = dset.ReadAsArray()

    x0, dx, fy, y0, fx, dy = dset.GetGeoTransform()

    # Adjust x0 and y0 to give pixel centres. GDAL specifies (x0, y0)
    # as the top left corner of the top left pixel. PyTOPKAPI expects
    # pixel centres. At the centre of the first pixel the following
    # holds: (Xpixel, Yline) == (0.5, 0.5)
    x0 = x0 + dx/2.0 + fy/2.0
    y0 = y0 + fx/2.0 + dy/2.0

    Yline, Xpixel = np.nonzero(mask == 1)

    Xgeo = x0 + Xpixel*dx + Yline*fy
    Ygeo = y0 + Xpixel*fx + Yline*dy

    return Xgeo, Ygeo





path_to_rainData = "rainfall_fake_data.csv"
coords_station = {'StationA': [100,200] ,'StationB': [150,150] ,'StationC': [200,200] } # values are indices i,j from the top left corner, may be
coords_station = {'StationA': [433385,4518084] ,'StationB': [435914,4518052] ,'StationC': [433268,4515586]} # values are indices i,j from the top left corner, may be
reference_raster  = 'mask_r.tif'
start_date = date(2015, 1, 2)
end_date = date(2015, 1, 5)           # does not include this day though

ds = gdal.Open(reference_raster)
geotransform = ds.GetGeoTransform()
ncol = ds.RasterXSize
nrow = ds.RasterYSize
resolution = geotransform[1]
originX = geotransform[0]             # Location of top left corner, not center
originY = geotransform[3]
xtopleft, xtopright, ytopleft, ybottomleft = originX, originX*ncol*resolution, originY, originY*nrow*resolution
# rain_array = np.empty(ds.ReadAsArray().shape)
# to see if the values are right
print ncol, nrow, resolution, originX, originY, xtopleft, xtopright, ytopleft, ybottomleft





# INTERPOLATE
# http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.interp2d.html
x = [values[1][0] for values in coords_station.iteritems()]
y = [values[1][1] for values in coords_station.iteritems()]
xx, yy = np.meshgrid(x, y)                  # May not be needed
rain_station = np.zeros(xx.shape)
# for key, value in coords_station.iteritems():
#         rain_station[value[0], value[1]] = rainfall_in_station(path_to_rainData , key, start_date)  # for now, one date
rain_station = np.array([[100,0,0],
              [0,0,350],
              [0,120,0]])
f = interpolate.interp2d(x, y, rain_station, kind='linear')

# Use the interpolation function
xx_wshed, yy_wshed = compute_cell_coordinates(reference_raster)   # Watershed mesh grid
rain_wshed = f(xx_wshed, yy_wshed)



# calculate Scipy interpolation for different time period
for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y/%m/%d")
    print date
    rain_station = np.zeros([3,3])
    for key, value in coords_station.iteritems():
        rain_station[value[0], value[1]] = rainfall_in_station(path_to_rainData , key, date)



    #interpolation

    x = np.linspace(xtopleft,xtopright, ncol)
    y = np.linspace(ytopleft,ybottomleft,nrow)
    xx, yy = np.meshgrid(x,y)

    z = rain_array
    #
    # tck = interpolate.bisplrep(xx, yy, z, s=0)
    # znew = interpolate.bisplev(xx[:,0], yy[0,:], tck)





















#
# x, y = np.mgrid[-1:1:20j, -1:1:20j]
#
# z = (x+y) * np.exp(-6.0*(x*x+y*y))
# xnew, ynew = np.mgrid[-1:1:70j, -1:1:70j]
# tck = interpolate.bisplrep(x, y, z, s=0)
# znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
#
#
# x, y = np.mgrid[-1:1:5j, -1:1:5j]
# #z = (x+y) * np.exp(-6.0*(x*x+y*y))
# z = np.empty([5,5])
#
# z[4,4] = 100
# z[2,2]=150
# z[1,1] = 110
# z[z==0] = np.NaN
#
# xnew, ynew = np.mgrid[-1:1:17j, -1:1:17j]
# tck = interpolate.bisplrep(x, y, z, s=0)
# znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
#
#
# rain_data = np.genfromtxt(path_to_rainData ,dtype='str,float,float,float', delimiter=',', names=True )















