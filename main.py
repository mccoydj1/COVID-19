import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cv_stats import cv_stats, createtable
from operator import itemgetter
import yaml
import git
import os
import datetime

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

#Grab latest info from JH
git_dir = os. getcwd() + r'\JH'
g = git.cmd.Git(git_dir)
g.pull()

cvpath = git_dir + r'\csse_covid_19_data\csse_covid_19_time_series\time_series_19-covid-Confirmed.csv'

#Grab the latest stats
data, uniq_countries_num, usdata, uscases, ildata, ilcases = cv_stats(cvpath, cfg['apikey'])

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

debug = True
if debug:
    receiver_email = [cfg['to']['to1']]
else:
    # If today is a saturday
    if datetime.datetime.today().weekday() == 5:
        receiver_email = [cfg['to']['to1'], cfg['to']['to2'], cfg['to']['to3']]
    else:
        receiver_email = [cfg['to']['to1'], cfg['to']['to2']]

# Send the email
message = MIMEMultipart("alternative")
message["Subject"] = "Daily Coronavirus"
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)

# Create the plain-text and HTML version of your message

html = "<html><body>Total countries with coronavirus: " + str(uniq_countries_num) + "<br>" + \
       "Total # of US cases: %d ( %d cities) <br><br>" % (uscases, len(usdata))

rapidspread = createtable('Rapid Spread', rapiddata)
emerging = createtable('Emerging', emergingdata)
slow = createtable('Slow', slowdata)
stable = createtable('Stable', stabledata)

ilcities = "<b>IL Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in ildata:
    ilcities = ilcities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
ilcities = ilcities + "</table><br><br>"

uscities = "<b>US Cities</b><table><tr><th>City</th><th>Count</th></tr>"
for city in usdata:
    uscities = uscities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
uscities = uscities + "</table><br><br>"


html = html + ilcities + rapidspread + slow + emerging + stable + uscities

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