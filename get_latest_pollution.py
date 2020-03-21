from sat_downloader import sat_downloader
from analyze_satellite_data import analyze_satellite_data
import csv

def get_latest_pollution(userid, password):

    # Download the required files
    sat_downloader(userid, password)

    # Then analyze the required files
    resultspath = analyze_satellite_data()

    # Then create html text for the files
    with open(resultspath, newline='\n') as f:
        reader = csv.reader(f)
        allresults = list(reader)

    return ''