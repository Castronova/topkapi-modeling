import os
import numpy as np


np.set_printoptions(formatter={'float': '{: 0.5f}'.format})

def compare_rainfall_file(example_rain, simulation_rain):
    """

    :param example_rain: path to example rainfields.h5
    :param simulation_rain: path to rainfall file used in the simulations
    :return:
    """
    import tables as h5
    import h5py

    eg_rain = h5py.File(example_rain , "r")
    sim_rain = h5py.File(simulation_rain, "r")

    print '*** Checking Keys ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain.keys(), sim_rain.keys())

    print '*** Checking the keys in the group "sample_event" ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain['sample_event'].keys(), sim_rain['sample_event'].keys())

    print '*** Checking the shape of the group "sample_event/rainfall" ***'
    print 'keys in Example are %s and in our simulation are %s ' %(eg_rain['sample_event/rainfall'].shape, sim_rain['sample_event/rainfall'].shape)

    #~~~~Rainfall
    group_name = 'sample_event'
    h5file_in = h5.openFile(simulation_rain,mode='r')
    group = '/'+group_name+'/'
    node = h5file_in.getNode(group+'rainfall')
    ndar_rain = node.read()
    print ndar_rain
    h5file_in.close()

    return

def check_hdf5(hdf5_filename):

    import matplotlib.pyplot as plt
    import h5py

    with  h5py.File(hdf5_filename , "r") as f:

        print "The groups in the h5 files are: "
        for group in f.keys():
            print "\t\t" , group,
        # print items / tables inside the group

        for group in f.keys():
            print "\n the Items in the group %s are:"%group
            try:
                for table in f[group]:
                    # if table == 'Qc_out':
                    print "\t\t" , table

                    print 'The size of the hdf5 table is ', f[group][table].shape
                    print 'And, the unique values in the tables are: \n'
                    print np.unique(f[group][table])

                    values_in_1D = f[group][table][:].reshape(-1)
                    plt.hist(values_in_1D,bins=20)
                    plt.show()
            except:
                pass

def sqllite_test():
    import sqlite3

    sqlite_file = 'my_first_db.sqlite'  # name of the sqlite database file
    table_name1 = 'my_table_1'  # name of the table to be created
    table_name2 = 'my_table_2'  # name of the table to be created
    new_field = 'my_1st_column'  # name of the column
    field_type = 'INTEGER'  # column data type

    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Creating a new SQLite table with 1 column
    c.execute('CREATE TABLE {tn} ({nf} {ft})' \
              .format(tn=table_name1, nf=new_field, ft=field_type))

    # Creating a second table with 1 column and set it as PRIMARY KEY
    # note that PRIMARY KEY column must consist of unique values!
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)' \
              .format(tn=table_name2, nf=new_field, ft=field_type))

    conn.commit()

    c.execute("Select * from %s"%table_name1)
    all_rows = c.fetchall()
    print all_rows


    conn.close()

def sqlite_userInputCommand_during_run(sqlite_db):
    # A minimal SQLite shell for experiments

    import sqlite3

    con = sqlite3.connect(sqlite_db)   #was   ":memory:"
    con.isolation_level = None
    cur = con.cursor()

    buffer = ""

    print "Enter your SQL commands to execute in sqlite3."
    print "Enter a blank line to exit."

    while True:
        line = raw_input()
        if line == "":
            break
        buffer += line
        if sqlite3.complete_statement(buffer):
            try:
                buffer = buffer.strip()
                cur.execute(buffer)

                if buffer.lstrip().upper().startswith("SELECT"):
                    print cur.fetchall()
            except sqlite3.Error as e:
                print "An error occurred:", e.args[0]
            buffer = ""

    con.close()

def download_daily_discharge(USGS_siteCode, beginDate, endDate,outFile, Q_max_min_mean= "mean"):
    """
    HW7  in hydroinformatics
    startDate, endDate: string,  format-  yyyy-mm-dd
    Q_max_min_mean: string, "max", "mean" or "min"
    """

    # GetValuesObject from a WaterOneFlow web service
    # Then create a time series plot using matplotlib
    from suds.client import Client
    from pandas import Series
    # import matplotlib.pyplot as plt

    # Create the inputs needed for the web service call
    wsdlURL = 'http://hydroportal.cuahsi.org/nwisuv/cuahsi_1_1.asmx?WSDL'
    siteCode = 'NWISUV:%s'%USGS_siteCode
    variableCode = 'NWISUV:00060'

    # Create a new object named "NWIS" for calling the web service methods
    NWIS = Client(wsdlURL).service

    # Call the GetValuesObject method to return datavalues
    response = NWIS.GetValuesObject(siteCode, variableCode, beginDate, endDate)

    # Get the site's name from the response
    siteName = response.timeSeries[0].sourceInfo.siteName

    # Create some blank lists in which to put the values and their dates
    a = []  # The values
    b = []  # The dates

    # Get the values and their dates from the web service response
    values = response.timeSeries[0].values[0].value

    # Loop through the values and load into the blank lists using append
    for v in values:
        a.append(float(v.value))
        b.append(v._dateTime)

    # Create a Pandas Series object from the lists
    # Set the index of the Series object to the dates
    ts = Series(a, index=b)

    # # resample is like group by clause in SQL
    # # summed = ts.resample('1D', how='sum')                            #ts.resample('1440T', how='sum')
    # ts_maxx = ts.resample('1D', how='max')
    # ts_minn = ts.resample('1D', how='min')
    # ts_mean = ts.resample('1D', how='mean')

    # # Use MatPlotLib to create a plot of the time series
    # # Create a plot of the streamflow statistics
    # # ------------------------------------------
    # # Create a figure object and add a subplot
    # # figure() creates  a big area where we can create multiple or single drawings
    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)  # arguments for add_subplot - add_subplot(nrows, ncols, plot_number)
    #
    # # Call the plot() methods on the series object to plot the data
    # ts.plot(color='0.9', linestyle='solid', label='15-minute streamflow values')
    # ts_maxx.plot(color='red', linestyle='solid', label='Daily streamflow values', marker="o")
    # ts_mean.plot(color='green', linestyle='solid', label='Daily streamflow values', marker="o")
    # ts_minn.plot(color='blue', linestyle='solid', label='Daily streamflow values', marker="o")
    #
    # # Set some properties of the subplot to make it look nice
    # ax.set_ylabel('Discharge, cubic feet per second')
    # ax.set_xlabel('Date')
    # ax.grid(True)
    # ax.set_title(siteName)
    #
    # # Add a legend with some customizations
    # legend = ax.legend(loc='upper left', shadow=True)
    #
    # # Create a frame around the legend.
    # frame = legend.get_frame()
    # frame.set_facecolor('0.95')

    # # Set the font size in the legend
    # for label in legend.get_texts():
    #     label.set_fontsize('large')
    #
    # for label in legend.get_lines():
    #     label.set_linewidth(1.5)  # the legend line width
    #
    # plt.savefig("HW7.png")
    # plt.show()

    if Q_max_min_mean.lower() == "max":
        ts_maxx = ts.resample('1D').max()
        r = ts_maxx
    elif Q_max_min_mean.lower() == "min":
        ts_minn = ts.resample('1D').min
        r = ts_minn
    else:
        # old syntax was  ts_mean = ts.resample('1D' , how='mean')
        ts_mean = ts.resample('1D').mean()
        r = ts_mean

    r.to_csv(outFile)

    # change format of the date in the saved file
    # replace - with ,
    f = file(outFile, "r")
    str_to_save = f.read().replace('-',",")
    f.close()

    #save it again
    f = file(outFile, "w")
    f.write(str_to_save)

    f = np.loadtxt(outFile, delimiter=",")
    q = f[:,-1]
    q = q * 0.028316847

    # to make shape of q (x,1) instead of (x,)
    qq = np.zeros((q.shape[0], 1))
    qq[:, 0] = q


    # take the first 3 columns,
    # add two extra colum = 0 0 for min and sec
    # add third column = q
    # save by seperating by space " "
    date_part = f[:,:-1]
    empty_col = np.zeros((f.shape[0],1))
    date_n_hour = np.append(date_part,empty_col, axis =1 )
    date_hour_n_min = np.append(date_n_hour, empty_col, axis=1)
    date_hr_min_n_Q = np.append(date_hour_n_min,qq, axis=1)
    np.savetxt(outFile,date_hr_min_n_Q, fmt='%i %i %i %i %i %f' , delimiter= "\t")

    return






eg_rain = "../../PyTOPKAPI/example_simulation/forcing_variables/rainfields.h5"
eg_ET = "../../PyTOPKAPI/example_simulation/forcing_variables/ET.h5"
sim_rain = "e:/trial_sim/rainfields.h5"
result = "../../simulations/Onion_1/run_the_model/results/results.h5"

download_daily_discharge('10126000', '2013-01-01', '2013-07-31',"../../simulations/Bear_1000/runoff.dat", Q_max_min_mean= "mean")