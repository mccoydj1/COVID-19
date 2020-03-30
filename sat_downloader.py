from sentinelsat import SentinelAPI
from geopy.geocoders import Nominatim
import os

def sat_downloader(userid, password, allcities_list):

    # Connect with the database
    apiurl = 'https://s5phub.copernicus.eu/dhus'
    testAPI = SentinelAPI(user=userid, password=password, api_url=apiurl)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # For all cities
    for precity in allcities_list:

        city = precity[0]

        # Determine the GPS location needed to search
        geolocator = Nominatim(user_agent="testApp")
        targetcity = geolocator.geocode(city)

        timeframes = ['beginposition:[NOW-1DAYS TO NOW]', 'beginposition:[2020-02-01T00:00:00.000Z TO 2020-02-02T00:00:00.000Z]', 'beginposition:[2020-01-05T00:00:00.000Z TO 2020-01-06T00:00:00.000Z]']

        # Determine what files meet the criteria specified
        #timeframe = 'beginposition:[NOW-1DAYS TO NOW]'
        #timeframe = 'beginposition:[2020-02-01T00:00:00.000Z TO 2020-02-02T00:00:00.000Z]'
        #timeframe = 'beginposition:[2020-01-05T00:00:00.000Z TO 2020-01-06T00:00:00.000Z]'

        for timeframe in timeframes:

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