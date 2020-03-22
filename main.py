import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cv_stats import cv_stats, createtable
from operator import itemgetter
import yaml
import git
import os
import datetime
import re
import numpy as np
from opensky_api import OpenSkyApi
from get_latest_pollution import get_latest_pollution

userid = 's5pguest'
password = 's5pguest'

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# Get pollution information
no2_text = get_latest_pollution(userid, password)

# Get flight information
api = OpenSkyApi()
s = api.get_states()

flights_in_air = [x for x in s.states if x.on_ground == False]
origin_countries = [flights_in_air.origin_country for flights_in_air in flights_in_air]

[allcountries, ia] = np.unique(origin_countries,return_inverse=True)

flighttracker = []
for ix, country in enumerate(allcountries):
    flightct = len(np.where(ix == ia)[0])
    flighttracker.append([country, flightct])

flighttracker = sorted(flighttracker, key=itemgetter(-1), reverse=True)

flight_html = "<b>Flight Data (" + str(len(ia)) + " flights in " + str(len(allcountries)) + " countries)</b><table><tr><th>Country</th><th>Count</th></tr>"
for flight in flighttracker:
    flight_html = flight_html + "<tr><td>%s</td><td>%d</td></tr>" %(flight[0], flight[1])
flight_html = flight_html + "</table><br><br>"

# Read IL department public health info on COVID-19
# import urllib.request
# page = urllib.request.urlopen('http://www.dph.illinois.gov/topics-services/diseases-and-conditions/diseases-a-z-list/coronavirus')
# html_doc = page.read()
# m = re.findall('Positive \(Confirmed\)</h2>.n<h3>(\d+)</h3>',str(html_doc))
# IL_cases_new = m[0]
# m = re.findall('PUIs Pending</h2>.n<h3>(\d+)</h3>',str(html_doc))
# IL_cases_pending = m[0]

debug = False

#Grab latest info from JH
git_dir = os. getcwd() + r'\JH'
g = git.cmd.Git(git_dir)
g.pull()

cvpath = git_dir + r'\csse_covid_19_data\csse_covid_19_time_series\time_series_19-covid-Confirmed.csv'

#Grab the latest stats
data, uniq_countries_num, usdata, uscases, ildata, ilcases, statelist, midwestdate, azdata = cv_stats(cvpath, cfg['apikey'], debug)

ussummarydata = [row for row in data if row[-1] == 'usdata']
ussummarydata = sorted(ussummarydata, key=itemgetter(-3), reverse=True)

us_statedate = [row for row in data if (row[-1] == 'usdata_small')]
us_statedate = sorted(us_statedate, key=itemgetter(-3), reverse=True)

emergingdata = [row for row in data if row[-1] == 'emerging']
emergingdata = sorted(emergingdata, key=itemgetter(-3), reverse=True)

rapiddata = [row for row in data if row[-1] == 'rapid']
rapiddata = sorted(rapiddata, key=itemgetter(-3), reverse=True)

slowdata = [row for row in data if row[-1] == 'slow']
slowdata = sorted(slowdata, key=itemgetter(-3), reverse=True)

stabledata = [row for row in data if row[-1] == 'stable']
stabledata = sorted(stabledata, key=itemgetter(-3), reverse=True)


#Send the email
sender_email = cfg['email']['user']
password = cfg['email']['pass']

#Who is the email going to send to?


if debug:
    receiver_email = [cfg['to']['to1']]
else:
    # If today is a saturday
    if datetime.datetime.today().weekday() == 5:
        receiver_email = [cfg['to']['to1'], cfg['to']['to2'], cfg['to']['to3'], cfg['to']['to4'], cfg['to']['to5'], cfg['to']['to6']]
    else:
        receiver_email = [cfg['to']['to1'], cfg['to']['to2'], cfg['to']['to4'], cfg['to']['to5'], cfg['to']['to6']]

# Send the email
message = MIMEMultipart("alternative")
message["Subject"] = "Daily Coronavirus"
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)

# Create the plain-text and HTML version of your message
# html = "<html><body>Total countries with coronavirus: " + str(uniq_countries_num) + "<br>" + \
#        "Total # of US cases: %d ( %d cities in %d states) <br><br>" % (uscases, len(usdata), len(statelist))

html = "<html><body>Total countries with coronavirus: " + str(uniq_countries_num) + "<br>" + \
       "Total # of US cases: %d (%d states incl diamond princess & DC)<br><br>" % (uscases, len(statelist))

# html = html + 'Current IL cases: %s (with %s patients under investigation)<br><br>' % (IL_cases_new, IL_cases_pending)

ussummarydata_txt = createtable('USA', ussummarydata)
ussummarydata_slow = createtable('USA (small)', us_statedate)
rapidspread = createtable('Rapid Spread', rapiddata)
emerging = createtable('Emerging', emergingdata)
slow = createtable('Slow', slowdata)
stable = createtable('Stable', stabledata)

ilcities = "<b>IL Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in ildata:
    ilcities = ilcities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
ilcities = ilcities + "</table><br><br>"

midwestcities = "<b>MO/IN/IA Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in midwestdate:
    midwestcities = midwestcities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
midwestcities = midwestcities + "</table><br><br>"

AZcities = "<b>AZ Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in azdata:
    AZcities = AZcities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
AZcities = AZcities + "</table><br><br>"

uscities = "<b>US Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in usdata:
    uscities = uscities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
uscities = uscities + "</table><br><br>"

# John Hopkins stopped reporting on county so this part doesnt work anymore
# html = html + ilcities + ussummarydata_txt + rapidspread + slow + emerging + stable + ussummarydata_slow + midwestcities + AZcities + uscities
html = html + ussummarydata_txt + flight_html + rapidspread + slow + emerging + stable + ussummarydata_slow

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
#message.attach(part1)
message.attach(MIMEText(html, "html"))

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )