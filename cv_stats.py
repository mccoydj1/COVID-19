import csv
import numpy as np
from operator import itemgetter

def cv_stats(cvpath):

    with open(cvpath, newline='\n') as f:
        reader = csv.reader(f)
        data = list(reader)

    countries = [row[1] for row in data]
    countriesregion = [row[0:2] for row in data[1:-1]]

    for i in countriesregion:
        if i[0] == "":
            i[0] = i[1]

    uniq_countries = list(set(countries[1:-1]))
    uniq_countries_num = len(uniq_countries)

    usdata = [[data[0], float(data[-1])] for data in data if data[1] == 'US']
    usdata = sorted(usdata, key=itemgetter(1), reverse=True)
    uscases = sum([row[1] for row in usdata])

    lastfourdays = [row[-5:-1] for row in data]

    finallist = list()

    ct = 0
    for countrydata in lastfourdays[1:-1]:

        countrydata_num = [float(i) for i in countrydata]
        suspect_country = countriesregion[ct][0]
        increase1, increase2, amt1, amt2, amt3, acc, increasetype = assess_increase(countrydata_num)
        finallist.append([suspect_country, increase1, increase2, amt1, amt2, amt3, acc, increasetype])

        ct = ct + 1

    emaillist = [row for row in finallist if row[1] > 0]

    return emaillist, uniq_countries_num, usdata, uscases


def assess_increase(raw_countrydata_num):

    countrydata_num = smooth(raw_countrydata_num, 2)

    increase1 = 0
    increase2 = 0
    amt1 = 0
    amt2 = 0
    amt3 = 0
    acc = 0
    increasetype = ''

    # Assume the very first data point is greater than 0 and the last data point is greater than 10
    if countrydata_num[0] > 0 and countrydata_num[2] > 10:

        delta1 = countrydata_num[1] - countrydata_num[0]
        delta2 = countrydata_num[2] - countrydata_num[1]

        perc_increase1 = 100 * delta1 / countrydata_num[0]
        perc_increase2 = 100 * delta2 / countrydata_num[1]

        largecase = delta1 > 500 and delta1 > 500
        normalincrease = delta1 > 10 and delta2 > 10 and perc_increase1 > 10 and perc_increase2 > 10
        temp_acc = delta2 - delta1

        # If you find a likely suspect
        if largecase or normalincrease:
            increase1 = perc_increase1
            increase2 = perc_increase2
            amt1 = raw_countrydata_num[-3]
            amt2 = raw_countrydata_num[-2]
            amt3 = raw_countrydata_num[-1]
            acc = delta2 - delta1
            increasetype = 'rapid'

        elif perc_increase1 > 10 and perc_increase2 > 10 and temp_acc > 0:
            increase1 = perc_increase1
            increase2 = perc_increase2
            amt1 = raw_countrydata_num[-3]
            amt2 = raw_countrydata_num[-2]
            amt3 = raw_countrydata_num[-1]
            acc = delta2 - delta1
            increasetype = 'emerging'

    # Return all values
    return increase1, increase2, amt1, amt2, amt3, acc, increasetype


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth
