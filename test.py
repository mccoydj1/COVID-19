import json

# read file
with open('output.json', 'r') as myfile:
    data=myfile.read()

# parse file
obj = json.loads(data)

print('hi')


#
#
# #Works
# wget -O - "http://finder.creodias.eu/resto/api/collections/Sentinel5P/search.json?_pretty=true&q=Poland&maxRecords=1"
#
#
# #https://creodias.eu/eo-data-finder-api-manual?inheritRedirect=true
#
# # Gets the last file from Sentinel 5P
# wget -O "C:\Users\mccoy\PycharmProjects\untitled\output.json"  "http://finder.creodias.eu/resto/api/collections/Sentinel5P/search.json?_pretty=true&maxRecords=10"
#

#wget "http://finder.creodias.eu/resto/api/collections/Sentinel5p/describe.xml"


#https://sentinel.esa.int/documents/247904/2474726/Sentinel-5P-Level-2-Product-User-Manual-Nitrogen-Dioxide


#wget -O "C:\Users\mccoy\PycharmProjects\untitled\output2.json"  "http://finder.creodias.eu/resto/api/collections/Sentinel5P/search.json?_pretty=true&productIdentifier='/eodata/Sentinel-5P/TROPOMI/L2__NO2___/2020/03/15/S5P_NRTI_L2__NO2____20200315T222350_20200315T222850_12549_01_010302_20200315T230627'"

#http://www.acgeospatial.co.uk/sentinel-5p-and-python/


#USEFUL
#https://pypi.org/project/sentinelsat/
#https://scihub.copernicus.eu/twiki/do/view/SciHubUserGuide/FullTextSearch?redirectedfrom=SciHubUserGuide.3FullTextSearch
#https://github.com/acgeospatial/Sentinel-5P/blob/master/Sentinel_5P.ipynb