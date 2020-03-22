from netCDF4 import Dataset
import numpy as np
from operator import itemgetter
from scipy import spatial
from geopy.geocoders import Nominatim
import re
import os
import csv
import glob

def analyze_satellite_data(allcities_list):

    # Grab all cities that are needed for the test
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Find all data files that need to be analyzed
    presatpath = dir_path + r'\datafiles'
    files_to_run = glob.glob(presatpath + '/*.nc')

    # Look at existing results
    resultspath = dir_path + '\\no2_results.csv'
    with open(resultspath, newline='\n') as f:
        reader = csv.reader(f)
        allresults = list(reader)

    # Find out what files haven't been run yet..
    allresults_paths = [allresults[3] for allresults in allresults]
    new_files_to_run = list(set(files_to_run).difference(set(allresults_paths)))

    # For all paths that need to be run...
    for satpath in new_files_to_run:

        #fname = r'\S5P_OFFL_L2__NO2____20200201T180837_20200201T195007_11937_01_010302_20200204T232112.nc'
        #satpath = presatpath + fname

        num_dpts = 20

        res = re.findall('L2__NO2____(\d\d\d\d)(\d\d)(\d\d)',satpath)
        datestr = res[0][0] + '/' + res[0][1] + '/' + res[0][2]
        read_sat_data(satpath, allcities_list, num_dpts, resultspath, datestr)

    return resultspath


def read_sat_data(satpath, allcities_list, num_dpts, resultspath, datestr):

    # Read the data in once..
    print('Reading data for ' + satpath)
    fh = Dataset(satpath, mode='r')

    # Grab latitude / longitude / no2 from the files
    lons = fh.groups['PRODUCT'].variables['longitude'][:][0, :, :]
    lats = fh.groups['PRODUCT'].variables['latitude'][:][0, :, :]
    no2 = fh.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column_precision'][0, :, :]

    # Turn the matrix of lat / long into ordered pairs of coordinates
    flat_lons = np.ndarray.flatten(lons)
    flat_lats = np.ndarray.flatten(lats)
    coords = num_merge(flat_lats, flat_lons)

    # Finds a certain number of lat/long pairs that are close to the origin then uses that index to find sum(NO2)
    tree = spatial.KDTree(coords)

    # For all cities..
    for mycitylist in allcities_list:

        mycity = mycitylist[0]
        print(mycity)

        # Find lat/long data for the target city
        geolocator = Nominatim(user_agent="testApp")
        targetcity = geolocator.geocode(mycity)
        mylat = targetcity.latitude
        mylong = targetcity.longitude

        res = tree.query([(mylat, mylong)], num_dpts)

        # If you found a city that was reasonably close to the data in the file...
        if min(res[0][0]) < 1:
            flat_no2 = np.ndarray.flatten(no2)
            no2array = itemgetter(*res[1][0])(flat_no2)
            #mycoords = itemgetter(*res[1][0])(coords)

            # Return the result
            # Not exactly sure what the units are on this...
            total_no2 = 1000 * sum(no2array)

            # As long as its a number, record the value
            if isinstance(total_no2, float):

                # Create the path to put the data
                results_data = [mycity, datestr, str(total_no2), satpath]

                # Output the results to a results file
                with open(resultspath, 'a', newline='\n') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerow(results_data)

def num_merge(list1, list2):
    merged_list = tuple(zip(list1, list2))
    return merged_list