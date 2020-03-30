from sat_downloader import sat_downloader
from analyze_satellite_data import analyze_satellite_data
import csv
import os
import datetime

def get_latest_pollution(userid, password):

    # Current directory
    # Determine what cities to run the analysis with
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + r'\\cities_to_run.txt', newline='\n') as f:
        reader = csv.reader(f, delimiter='|')
        allcities_list = list(reader)

    # Download the required files
    sat_downloader(userid, password, allcities_list)

    # Then analyze the required files
    resultspath = analyze_satellite_data(allcities_list)

    # Then create html text for the files
    with open(resultspath, newline='\n') as f:
        reader = csv.reader(f)
        allresults = list(reader)

    # Make sure everything has been date timed
    allresults = [[results[0], datetime.datetime.strptime(results[1],'%Y/%m/%d'), results[2], results[3]] for results in allresults[1:]]
    allresults.sort(key=lambda x: x[1])

    maxdatestr_final = max([results[1] for results in allresults]).strftime("%m/%d/%Y")

    no2_final_data = []

    # For all cities... capture the results information
    for city in allcities_list:

        # Get all data for the current city
        mycity = city[0]
        results_mycity = [results for results in allresults if results[0] == mycity]
        maxdatestr = max([results[1] for results in results_mycity]).strftime("%m/%d/%Y")
        mycity_dict = {t[1].strftime("%m/%d/%Y"): t[:] for t in results_mycity}

        # Find values for jan, feb, and the most recent entry
        jan1 = float(mycity_dict['01/05/2020'][2])
        feb1 = float(mycity_dict['02/01/2020'][2])
        current = float(mycity_dict[maxdatestr][2])
        perc_change = current / feb1

        no2_final_data.append([mycity, jan1, feb1, current, perc_change])

    # Create the final table
    no2_table_html = "<b>NO2 data</b><table><tr><th>City</th><th>01/01/2020</th><th>02/01/2020</th><th>" + maxdatestr_final + "</th><th>% Change</th></tr>"
    for no2_data in no2_final_data:
        no2_table_html = no2_table_html + "<tr><td>%s</td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>" % (no2_data[0], no2_data[1], no2_data[2], no2_data[3], no2_data[4])
    no2_table_html = no2_table_html + "</table><br><br>"

    return no2_table_html