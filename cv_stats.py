import csv
import numpy as np
from operator import itemgetter
import requests, json
import pytemperature
import re


def cv_stats(cvpath, apikey):

    with open(cvpath, newline='\n') as f:
        reader = csv.reader(f)
        data = list(reader)

    header = data[0]
    data = [fixdataquality(row) for row in data[1:]]

    # Find all illinois cases
    ildata = [[data[0], float(data[-1])] for data in data if data[0].find('IL') > 0]
    ilcases = sum([row[1] for row in ildata])

    # Find all US cases
    usdata = [[data[0], float(data[-1])] for data in data if data[1] == 'US']
    usdata = sorted(usdata, key=itemgetter(1), reverse=True)
    uscases = sum([row[1] for row in usdata])

    # Convert cities in US states to be their state
    data = convert_cities_to_states(data)

    countries = [row[1] for row in data]
    countriesregion = [row[0:4] for row in data[1:-1]]

    for i in countriesregion:
        if i[0] == "":
            i[0] = i[1]
        elif i[0].find(',') < 0:
            i[0] = i[0] + ', ' + i[1]

    uniq_countries = list(set(countries[1:-1]))
    uniq_countries_num = len(uniq_countries)

    lastfourdays = [row[-4:] for row in data]

    finallist = list()

    ct = 0
    for countrydata in lastfourdays[1:-1]:

        countrydata_num = [float(i) for i in countrydata]
        suspect_country = countriesregion[ct][0]
        country_full = countriesregion[ct][1]

        increase1, increase2, increase3, amt1, amt2, amt3, amt4, acc, increasetype = assess_increase(countrydata_num)

        if len(increasetype) > 0:

            lat = countriesregion[ct][2]
            long = countriesregion[ct][3]
            temp = assess_weather(lat, long, apikey)
            #temp = 40

            if country_full.find('US') >= 0:
                increasetype = 'usdata'

            finallist.append([suspect_country, increase1, increase2, increase3, amt1, amt2, amt3, amt4, acc, temp, increasetype])

        ct = ct + 1

    return finallist, uniq_countries_num, usdata, uscases, ildata, ilcases


def assess_increase(raw_countrydata_num):

    #countrydata_num = smooth(raw_countrydata_num, 2)
    countrydata_num = raw_countrydata_num

    increase1 = 0
    increase2 = 0
    increase3 = 0
    amt1 = 0
    amt2 = 0
    amt3 = 0
    amt4 = 0
    acc = 0
    increasetype = ''

    np.diff(raw_countrydata_num)

    # Assume the very first data point is greater than 0 and the last data point is greater than 10
    if countrydata_num[0] > 0 and countrydata_num[2] > 10:

        delta1 = countrydata_num[-3] - countrydata_num[-4]
        delta2 = countrydata_num[-2] - countrydata_num[-3]
        delta3 = countrydata_num[-1] - countrydata_num[-2]

        perc_increase1 = 100 * delta1 / countrydata_num[-4]
        perc_increase2 = 100 * delta2 / countrydata_num[-3]
        perc_increase3 = 100 * delta3 / countrydata_num[-2]


        # Call it a large case if 2/3 have increases greater than 500
        largecase = sum([delta1 > 500, delta2 > 500, delta3 > 500]) >= 2
        mediumcase = sum([delta1 > 100, delta2 > 100, delta3 > 100]) >= 2
        normalincrease_amt = sum([delta1 > 10, delta2 > 10, delta3 > 10]) >= 2
        rapidincrease_pct = sum([perc_increase1 > 30, perc_increase2 > 30, perc_increase3 > 30]) >= 2
        slowincrease_pct = sum([perc_increase1 > 5, perc_increase2 > 5, perc_increase3 > 5]) >= 2

        temp_acc1 = delta2 - delta1
        temp_acc2 = delta3 - delta2
        temp_acc = max(temp_acc1, temp_acc2)

        # If you find a likely suspect
        if largecase or (rapidincrease_pct and normalincrease_amt):
            increase1 = perc_increase1
            increase2 = perc_increase2
            increase3 = perc_increase3
            amt1 = raw_countrydata_num[-4]
            amt2 = raw_countrydata_num[-3]
            amt3 = raw_countrydata_num[-2]
            amt4 = raw_countrydata_num[-1]
            acc = temp_acc
            increasetype = 'rapid'

        elif mediumcase or (slowincrease_pct and normalincrease_amt):
            increase1 = perc_increase1
            increase2 = perc_increase2
            increase3 = perc_increase3
            amt1 = raw_countrydata_num[-4]
            amt2 = raw_countrydata_num[-3]
            amt3 = raw_countrydata_num[-2]
            amt4 = raw_countrydata_num[-1]
            acc = temp_acc
            increasetype = 'slow'

        elif rapidincrease_pct and temp_acc > 0:
            increase1 = perc_increase1
            increase2 = perc_increase2
            increase3 = perc_increase3
            amt1 = raw_countrydata_num[-4]
            amt2 = raw_countrydata_num[-3]
            amt3 = raw_countrydata_num[-2]
            amt4 = raw_countrydata_num[-1]
            acc = temp_acc
            increasetype = 'emerging'

        elif countrydata_num[-4] > 100:
            increase1 = perc_increase1
            increase2 = perc_increase2
            increase3 = perc_increase3
            amt1 = raw_countrydata_num[-4]
            amt2 = raw_countrydata_num[-3]
            amt3 = raw_countrydata_num[-2]
            amt4 = raw_countrydata_num[-1]
            acc = temp_acc
            increasetype = 'stable'

    # Return all values
    return increase1, increase2, increase3, amt1, amt2, amt3, amt4, acc, increasetype


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

# Fix the quality of the data
def fixdataquality(row):
    if row[-1] == '':
        row[-1] = 0

    return row


def createtable(title, data):
    text = "<b>" + title + ' (' + str(len(data)) + ')' +  "</b><table><tr><th>Country</th><th>%3DA</th><th>%2DA</th><th>%Y</th><th>4DA</th><th>3DA</th><th>2DA</th><th>Yest</th><th>Acc</th></tr>"

    for country in data:
        text = text + "<tr><td>%s (%.1fF)</td><td>%.1f</td><td>%.1f</td><td>%.1f</td>" \
                      "<td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.f</td></tr>" % (
                   country[0], country[-2], country[1], country[2], country[3], country[4], country[5], country[6], country[7], country[8])

    text = text + "</table><br><br>"

    return text

def assess_weather(lat, long, api_key):

    # base_url variable to store url
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # complete_url variable to store
    # complete url address
    #complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    complete_url = base_url + "lat=" + lat + '&lon=' + long +  "&appid=" + api_key

    # get method of requests module
    # return response object
    response = requests.get(complete_url)

    # json method of response object
    # convert json format data into
    # python format data
    x = response.json()

    # Now x contains list of nested dictionaries
    # Check the value of "cod" key is equal to
    # "404", means city is found otherwise,
    # city is not found
    if x["cod"] != "404":
        # store the value of "main"
        # key in variable y
        y = x["main"]

        # store the value corresponding
        # to the "temp" key of y
        current_temperature = pytemperature.k2f(y["temp_max"])

        # store the value corresponding
        # to the "pressure" key of y
        current_pressure = y["pressure"]

        # store the value corresponding
        # to the "humidity" key of y
        current_humidiy = y["humidity"]

        # store the value of "weather"
        # key in variable z
        z = x["weather"]

        # store the value corresponding
        # to the "description" key at
        # the 0th index of z
        weather_description = z[0]["description"]

        return current_temperature


def convert_cities_to_states(data):

    usdata = [data for data in data if data[1] == 'US']
    nonusdata = [data for data in data if data[1] != 'US']

    allstates = []

    for us in usdata:
        state = re.findall(r", (\w\w)", us[0])

        if len(state) == 1:
            mystate = state[0]
        else:
            mystate = 'Unknown'

        us[0] = mystate
        allstates.append(mystate)

    uniq_states = list(set(allstates))

    statelist = []

    for uniq in uniq_states:
        allstate_data_txt = [data[0:4] for data in data if data[0] == uniq]
        allstate_data_num = [[float(x) for x in data[4:]] for data in data if data[0] == uniq]

        newsum = np.sum(allstate_data_num, axis=0).tolist()
        newsum_str = [str(x) for x in newsum]
        newlist = allstate_data_txt[0][0:4] +  newsum_str

        statelist.append(newlist)

    new_revised = nonusdata + statelist

    return new_revised