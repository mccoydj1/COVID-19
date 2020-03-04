import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cv_stats import cv_stats
from operator import itemgetter
import yaml
import git
import os

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

#Grab latest info from JH
git_dir = os. getcwd() + r'\JH'
g = git.cmd.Git(git_dir)
g.pull()

cvpath = git_dir + r'\csse_covid_19_data\csse_covid_19_time_series\time_series_19-covid-Confirmed.csv'

#Grab the latest stats
data, uniq_countries_num, usdata, uscases = cv_stats(cvpath)

emergingdata = [row for row in data if row[7] == 'emerging']
emergingdata = sorted(emergingdata, key=itemgetter(6), reverse=True)

rapiddata = [row for row in data if row[7] == 'rapid']
rapiddata = sorted(rapiddata, key=itemgetter(6), reverse=True)


#Send the email
sender_email = cfg['email']['user']
password = cfg['email']['pass']

#Who is the email going to send to?
receiver_email = [cfg['to']['to1'], cfg['to']['to2']]
#receiver_email = cfg['to']['to1']

message = MIMEMultipart("alternative")
message["Subject"] = "Daily Coronavirus"
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)

# Create the plain-text and HTML version of your message

html = "<html><body>Total countries with coronavirus: " + str(uniq_countries_num) + "<br>" + \
       "Total # of US cases: %d ( %d cities) <br><br>" % (uscases, len(usdata))

rapidspread = "<b>Rapid Spread</b><table><tr><th>Country</th><th>%3DA</th><th>%2DA</th><th>3 days ago</th><th>2 days ago</th><th>Acc</th></tr>"


for country in rapiddata:
    rapidspread = rapidspread + "<tr><td>%s</td><td>%.1f</td><td>%.1f</td><td>%d</td>" \
              "<td>%d</td><td>%.f</td></tr>" % (country[0], country[1], country[2], country[4], country[5], country[6])

rapidspread = rapidspread + "</table><br><br>"


emerging = "<b>Emerging</b><table><tr><th>Country</th><th>%3DA</th><th>%2DA</th><th>3 days ago</th><th>2 days ago</th><th>Acc</th></tr>"

for country in emergingdata:
    emerging = emerging + "<tr><td>%s</td><td>%.1f</td><td>%.1f</td><td>%d</td>" \
              "<td>%d</td><td>%.f</td></tr>" % (country[0], country[1], country[2], country[4], country[5], country[6])

emerging = emerging + "</table><br><br>"


uscities = "<b>US Cities</b><table><tr><th>City</th><th>Count</th></tr>"

for city in usdata:
    uscities = uscities + "<tr><td>%s</td><td>%d</td></tr>" %(city[0], city[1])
uscities = uscities + "</table><br><br>"



html = html + rapidspread + emerging + uscities

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