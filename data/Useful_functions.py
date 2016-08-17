import os, sqlite3, csv
import pandas as pd

def download_and_resample_discharge_data(USGS_Gage, begin_date='2015-01-01', end_date='2015-12-31',out_fname='Q_cfs.txt', resampling_time = '1D', resampling_method='mean'):
    """
    Downloads, and then resamples the discharge data from USGS using the url of the format:
    http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no=10109000&period=&begin_date=2015-10-01&end_date=2015-10-31
    INPUT:
    USGS_Gage :     string, e.g. 10109000
    begin_date=     string, e.g. '2015-01-01'
    end_date=       string, e.g. '2015-12-31'
    out_fname=      string, e.g. 'Q_cfs'
    resampling_time=  string, e.g. '1D'
    resampling_method=string, e.g.'mean'
    """

    import urllib2
    import pandas as pd

    urlString3 = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no=%s&period=&begin_date=%s&end_date=%s'%(USGS_Gage, begin_date, end_date)

    response = urllib2.urlopen(urlString3)  # instance of the file from the URL
    html = response.read()                  # reads the texts into the variable html

    with open('Q_raw.txt', 'w') as f:
        f.write(html)

    df = pd.read_csv('Q_raw.txt', delimiter='\t' , skiprows=26, names=['agency_cd', 'USGS_Station_no', 'datatime', 'timezone', 'Q_cfs','Quality'])

    # convert datetime from string to datetime
    df.iloc[:, 2] = pd.to_datetime(df.iloc[:, 2])

    # create a different dataframe with just the values and datetime
    df_datetime_val = df[['datatime', 'Q_cfs']]

    # convert the values to series
    values = []
    dates = []

    # add values to the list a
    for v in df_datetime_val.iloc[:,1]:
        values.append(float(v))

    # add datatime to list b
    for v in df_datetime_val.iloc[:, 0]:
        dates.append(v)

    # prepare a panda series
    ts = pd.Series(values, index=dates)

    # resample to daily or whatever
    # ts_mean = ts.resample('1D', how='mean') #or
    # ts_mean = ts.resample('1D').mean()
    ts_mean = ts.resample(resampling_time, how=resampling_method)


    # save
    ts_mean.to_csv(out_fname)


def txt_to_mysql(path_to_txt, fields_that_are_string, db_name, table_name):
    # http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
    # https://docs.python.org/2/library/sqlite3.html
    import sqlite3
    import csv

    # Connecting to the database file
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # # STEP-1 # #
    # Get Data from text
    with open(path_to_txt, 'rb') as f:
        reader = csv.reader(f)
        all_data = list(reader)

    # seperate rows as header and datavalues rows
    headers = all_data[0]
    data_list = all_data[1:]

    # a primary key for each row
    pk_val = range(1,len(data_list)+1) # 1,23,...,n

    # Modify data_list to add a col, primary key (PK), in front of each row
    for i in range(len(data_list)):
        data_list[i].insert(0,pk_val[i])

    data_in_tuple = [tuple(item) for item in data_list]

    # # STEP-2 # #
    # Creating a fresh table, with just primary key in it
    c.execute('create table %s  (PK int);' %table_name)

    # adding fields now, from the given csv files header
    # by default, fields are assumed integer, unless their indices are mentioned in the list: fields_that_are_string

    for i in range(len(headers)):
        field_name = headers[i].replace('\n','')
        field_type = 'REAL'

        if i in fields_that_are_string:
            field_type = 'TEXT'

        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}" \
                  .format(tn=table_name, cn=field_name, ct=field_type))

    # # STEP-3 # #
    # add data to the created table
    helper_string = '?'+ ',?'* (len(headers))
    c.executemany('INSERT INTO %s VALUES (%s)'%(table_name, helper_string), data_in_tuple)

    conn.commit()
    conn.close()

def ssurgo_to_sqlite(path_to_ssurgo):
    path_to_tabular = path_to_ssurgo + '\\tabular'

    db_name = path_to_tabular + '\\' + os.path.basename(
        path_to_ssurgo) + '.sqlite'  # folder will be the name of the database

    tables = []
    for file in os.listdir(path_to_tabular):
        if file.endswith('csv'):
            tables.append(os.path.basename(file).split(".")[0])

    for table in tables:
        path_to_txt = os.path.join(path_to_tabular, table + ".csv")
        table_name = table.replace('-', '_')  # replaced - because sqlite does not accept - as table name
        if table == 'chorizon':
            fields_that_are_string = [0]
        if table == 'chtextur':
            fields_that_are_string = [0]
        if table == 'merged':
            fields_that_are_string = [0, 5, 8, 10]
        if table == 'muaggatt_Removed_HydrGRP':
            fields_that_are_string = [1]
        if table == 'OverallMergedWithTexture' or 'OverallMergedWithTexture_2':
            fields_that_are_string = [0, 5, 8, 10]

        print 'Adding to Sqlite %s' % table
        txt_to_mysql(path_to_txt, fields_that_are_string, db_name, table_name)

def querry_to_csv(querry, outFile, db, sep='\t'):
    # execute the passed querry on the passed db. Save it as csv / tab separated file
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute(querry)
    to_save = c.fetchall()
    for item in to_save:
        try:
            item.remove('\n')
        except Exception:
            pass

    with open(outFile, 'a') as f:
        file_writer = csv.writer(f, delimiter=',', lineterminator='\n')
        for i in range(len(to_save)):
            file_writer.writerow( to_save[i],)

def interpolate_rain_backup(ppt_fname, tiff_fname, interpolate_method):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html#scipy.interpolate.griddata
    from scipy.interpolate import griddata
    import numpy as np
    import matplotlib.pyplot as plt
    from osgeo import gdal

    # create a grid
    # x1,y1
    #           x2,y2

    dset = gdal.Open(tiff_fname)
    mask = dset.ReadAsArray()

    print 'Shape of tif file', mask.shape

    # if tiff is not mask, creates a mask with 1 for all the cells with values
    mask[mask > -99] = 1

    x0, dx, fy, y0, fx, dy = dset.GetGeoTransform()
    n_row = dset.RasterXSize
    n_col = dset.RasterYSize

    x0 = x0 + dx/2
    y0 = y0 + dy/2
    print ' x0, dx, fy, y0, fx, dy', x0, dx, fy, y0, fx, dy

    start_x, start_y, end_x, end_y = x0 ,    y0+ dy* n_row ,    x0+dx*n_col,    y0


    # grid_x, grid_y = np.meshgrid(np.arange(start_x, end_x, dx), np.arange(start_y, end_y, dy))
    grid_x, grid_y = np.mgrid[start_x:end_x:np.complex(abs(n_col)), start_y:end_y:np.complex(abs(n_row))]

    print 'Shape of tif file', grid_x.shape

    np.savetxt("e:/grid_x.csv", grid_x, delimiter=",")
    np.savetxt("e:/grid_y.csv", grid_y, delimiter=",")

    # # x,y coordinates of all the, PROBABLY NOT REQUIRED SOON
    # Xgeo, Ygeo = compute_cell_coordinates(tiff_fname)
    # ar = np.vstack((Xgeo, Ygeo))
    # XY = ar.transpose()

    # points
    points = np.array([[-1229297.621, -1238297.621,-1222097.621,-1237397.621  ],
              [274705.4016, 270205.4016, 269305.4016, 289705.4016   ]])

    # points = np.array([ [274705.4016, 270205.4016, 269305.4016, 289705.4016],
    #                     [-1229297.621, -1238297.621, -1222097.621, -1237397.621]
    #                     ])
    points = points.T
    # values
    values = np.array([10,20,15,25])

    if interpolate_method.lower() == 'nearest':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')

    if interpolate_method.lower() == 'linear':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='linear')

    if interpolate_method.lower() == 'cubic':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='cubic')

    # draw
    plt.subplot(111)
    plt.imshow(grid_z0.T, origin='lower')
    plt.title(interpolate_method)
    plt.gcf().set_size_inches(6, 6)
    plt.show()
    plt.savefig('Interpolate_%s.png'%interpolate_method)

    # h = plt.contourf(x, y, z)

    np.savetxt("e:/interpolated_grid.csv", grid_z0, delimiter=",")
    return grid_z0

def interpolate_rain(points, values, tiff_fname, interpolate_method):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html#scipy.interpolate.griddata
    """
    INPUTS:
    points:     ndarray of coordinates. Shape (X,2). If 4stations, shape(4,2)
                e.g. np.array([[-1229297, -1238297,-1222097,-1237397],   [274705, 270205, 269305, 289705 ]])
    values:     ndarray of values (ppt/ET) for the coordinate. Shape (X,2). If 4stations, shape(4,)
                e.g. np.array([10,20,15,25])
    tiff_fname: typically mask (if not other tif) for the watershed, base on which the interpolation is done
    method:     cubic or nearest or linear

    OUTPUT:
    Interpolated grid of the same shape as tiff
    """
    from scipy.interpolate import griddata
    import numpy as np
    import matplotlib.pyplot as plt
    from osgeo import gdal

    dset = gdal.Open(tiff_fname)
    mask = dset.ReadAsArray()

    # if tiff is not mask, creates a mask with 1 for all the cells with values
    mask[mask > -99] = 1

    x0, dx, fy, y0, fx, dy = dset.GetGeoTransform() # x0,y0: coor if left-top corner. dx,dy: cell size. dy is -ve
    n_row = dset.RasterXSize
    n_col = dset.RasterYSize

    x0 = x0 + dx/2.
    y0 = y0 + dy/2.

    start_x, start_y, end_x, end_y = x0 ,    y0+ dy* n_row ,    x0+dx*n_col,    y0  # Origin/start at lower-left corner

    # grid_x, grid_y = np.meshgrid(np.arange(start_x, end_x, dx), np.arange(start_y, end_y, dy))
    grid_x, grid_y = np.mgrid[start_x:end_x:np.complex(abs(n_col)), start_y:end_y:np.complex(abs(n_row))]

    print 'Shape of tif file', grid_x.shape

    # np.savetxt("e:/grid_x.csv", grid_x, delimiter=",")
    # np.savetxt("e:/grid_y.csv", grid_y, delimiter=",")

    # points
    # need to be array of shape (X,2). If 4stations, (4,2)
    points = np.array([[-1229297.621, -1238297.621,-1222097.621,-1237397.621  ],
              [274705.4016, 270205.4016, 269305.4016, 289705.4016   ]])

    points = points.T

    # values
    # needs to be of shape (x,)
    values = np.array([10,20,15,25])

    if interpolate_method.lower() == 'nearest':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')

    if interpolate_method.lower() == 'linear':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='linear')

    if interpolate_method.lower() == 'cubic':
        grid_z0 = griddata(points, values, (grid_x, grid_y), method='cubic')

    # # draw
    # plt.subplot(111)
    # plt.imshow(grid_z0.T, origin='lower')
    # plt.title(interpolate_method)
    # plt.gcf().set_size_inches(6, 6)
    # plt.show()
    # plt.savefig('Interpolate_%s.png'%interpolate_method)

    # h = plt.contourf(x, y, z)

    np.savetxt("e:/interpolated_grid.csv", grid_z0, delimiter=",")
    return grid_z0


def compute_cell_coordinates(tiff_fname):
    from osgeo import gdal
    import numpy as np

    dset = gdal.Open(tiff_fname)
    mask = dset.ReadAsArray()

    # if tiff is not mask, creates a mask with 1 for all the cells with values
    mask[mask > -99] = 1

    x0, dx, fy, y0, fx, dy = dset.GetGeoTransform()

    # Adjust x0 and y0 to give pixel centres. GDAL specifies (x0, y0)
    # as the top left corner of the top left pixel.
    # holds: (Xpixel, Yline) == (0.5, 0.5)
    x0 = x0 + dx / 2.0 + fy / 2.0
    y0 = y0 + fx / 2.0 + dy / 2.0

    Yline, Xpixel = np.nonzero(mask == 1)

    Xgeo = x0 + Xpixel * dx + Yline * fy
    Ygeo = y0 + Xpixel * fx + Yline * dy

    return Xgeo, Ygeo

def climate_station_info(climate_st_fname):
    """
    Input: a csv file with header: Station_ID, Station_name, X, Y, fname
    Output: a dictionary containing values for each station_ID
    """

    import pandas as pd

    climate_st_fname = r"C:\Users\Prasanna\OneDrive\Public\topkapi-modeling\data\discharge\Interpolate\PPT_station_info.csv"

    # read file as pandas dataframe
    df = pd.read_csv(climate_st_fname)

    # create a dictionary
    d = {}
    for i in range(len(df)):
        d[df.iloc[i, :][0]] = [df.iloc[i, :][1], df.iloc[i, :][2], df.iloc[i, :][3], df.iloc[i, :][4]]

    # check if dictionay updated
    station_id = 1
    print 'For station id %s, the X is %s, and Y is %s. Fname is %s'%(station_id, d[station_id][1], d[station_id][2],
                                                                      d[station_id][3] )
    return d

def merge_ppt_stations(station_dict, working_folder):
    """
    INPUT: dictionary, generated by climate_station_info
    OUTPUT: a dataframe that is joint containing datetime (or timestep number) and values for each stations
            also a file
    """

    # station_dict = {1: ['ppt_lb_1', -1229297.621, 274705.40159999998, 'ppt_lb_1.txt'], 2: ['ppt_lb_2', -1238297.621, 270205.40159999998, 'ppt_lb_2.txt'], 3: ['ppt_lb_3', -1222097.621, 269305.40159999998, 'ppt_lb_3.txt'], 4: ['ppt_lb_4', -1237397.621, 289705.40159999998, 'ppt_lb_4.txt']}

    col = station_dict.keys()
    col.insert(0,'Datetime')

    # empty dataframe
    df = pd.DataFrame()
    for stationID in station_dict:

        # open file and add the datavalues (ppt/ et ) to empty dataframe created
        df2 = pd.read_csv(working_folder+'/'+ station_dict[stationID][-1], sep="\t")
        datavalues = df2.iloc[:,-1]
        # df.insert(stationID, stationID, datavalues)
        df.loc[:,stationID] = datavalues

    station_names = [station_dict[st_id][3].split(".")[0] for st_id in station_dict.keys()]
    df.to_csv(working_folder+'/'+"-".join(station_names)+".csv")
    return df


# input
path_to_ssurgo = r"C:\Users\Prasanna\OneDrive\Public\Multiple Watersheds in BRB\SSURGO_folders\UT613"
# ssurgo_to_sqlite(path_to_ssurgo)

q = '''
CREATE TEMPORARY TABLE mergedTable AS
SELECT *

FROM chtextur

INNER JOIN chtexgrp  ON
        chtextur.CHtxtgrpKEY = chtexgrp.CHtxtgrpKEY

INNER JOIN chorizon  ON
        chorizon.CHKEY = chtexgrp.CHKEY

INNER JOIN comp  ON
        comp.COKEY = chorizon.COKEY

INNER JOIN muaggatt  ON
        muaggatt.MUKEY = comp.MUKEY





SELECT MUKEY , ComponentPercent * WeightedAvgKsat/100 as FinalAns

From
(SELECT MUKEY , COKEY,ComponentPercent, sum(VxD) as sumVxD, sum(HorizonDepth2) as TotalDepth , round(sum(VxD)/ sum(HorizonDepth2),3)*10 as  WeightedAvgKsat

from
(select MUKEY,ComponentPercent, concat(CHKEY,":", COKEY) as CHCOkey , COKEY, ks * HorizonDepth2 as VxD, HorizonDepth2

from mergedTable) as chorizonCalc

group by COKEY) as ComponentCalc
group by MUKEY ;
'''

# querry_to_csv(q, path_to_ssurgo+'/tabular/join5.csv', path_to_ssurgo+'/tabular/UT613.sqlite',",")

# txt_to_mysql( path_to_ssurgo+'/tabular/join2.txt', [1,8,21,26], path_to_ssurgo+'/tabular/UT613.sqlite', 'joint')

merge_ppt_stations(climate_station_info("abc"), r"C:\Users\Prasanna\OneDrive\Public\topkapi-modeling\data\discharge\Interpolate")

interpolate_rain('ppt_fname', r'C:\Users\Prasanna\OneDrive\Public\Multiple Watersheds in BRB\LittleBearRiver\TIFFS\mask_r.tif', 'nearest')

















# for station in ['10105900 ' ,'10109000 ' , '10113500 ' , '10104900 ' , '10026500 ', '10132500 ' , '10137500 ','10113500',
#                 '10133980 ', '10153100 ' , '09277500 ', '09285900 ', '10146400 ', '09314280 ', '10149500 ', '10113500 ']:
#     download_and_resample_discharge_data('10109000' , begin_date='2015-01-01',end_date = '2015-12-31',
#                                          out_fname='discharge/Q_cfs_%s.txt'%station, resampling_time = '1D', resampling_method='max')
