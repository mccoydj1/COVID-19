from sentinelsat import SentinelAPI
from geopy.geocoders import Nominatim
import os

def sat_downloader(userid, password):

    # Current directory
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Connect with the database
    apiurl = 'https://s5phub.copernicus.eu/dhus'
    testAPI = SentinelAPI(user=userid, password=password, api_url=apiurl)

    # Grab all cities that are needed for the test
    f = open(dir_path + r'\\cities_to_run.txt', 'r')
    allcities_list = f.readlines()
    f.close()

    # For all cities
    for city in allcities_list:

        # Determine the GPS location needed to search
        geolocator = Nominatim(user_agent="testApp")
        targetcity = geolocator.geocode(city)

        # Determine what files meet the criteria specified
        timeframe = 'beginposition:[NOW-1DAYS TO NOW]'
        #timeframe = 'beginposition:[2020-02-01T00:00:00.000Z TO 2020-02-02T00:00:00.000Z]'
        satquery_loc = 'footprint:"intersects(' + str(targetcity.latitude) + ',' + str(targetcity.longitude) + ')"'
        products = testAPI.query(raw=satquery_loc + ' AND ' + timeframe + ' AND producttype:L2__NO2___')

        # Based on that, generate paths of available data
        downloadedfile = products[next(iter(products))]['filename']
        datafilesfolder = r'\\datafiles\\'
        downloadedfile_full = dir_path + datafilesfolder + downloadedfile
        firstdownload = dir_path + datafilesfolder.replace(r'datafiles\\', '') + downloadedfile.replace('.nc', '.zip')

        # Check to see if you have already downloaded this file
        if os.path.exists(downloadedfile_full):
            #Exists!
            print('File exists.. skipping')
        else:
            # Otherwise, download all results from the search
            mypath = testAPI.download_all(products)

            # Move the file to where its supposed to go
            os.rename(firstdownload, downloadedfile_full)