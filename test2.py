import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
mypath = r'C:\Users\mccoy\PycharmProjects\untitled\gz_2010_us_outline_500k.json'
# products = api.query(footprint,
#                      producttype='SLC',
#                      orbitdirection='ASCENDING')
# api.download_all(products)

testAPI = SentinelAPI(user='s5pguest', password='s5pguest', api_url='https://s5phub.copernicus.eu/dhus')
footprint = geojson_to_wkt(read_geojson(mypath))
#products = testAPI.query(area = footprint, date = "[NOW-20DAYS TO NOW]", platformname='Sentinel-5p')

#Pollution map for the US
products = testAPI.query(area = footprint, date = "[NOW-1DAYS TO NOW]",producttype='L2__NO2___')

# download all results from the search
mypath = testAPI.download_all(products)
downloadedfile = mypath[0][next(iter(mypath[0]))]['path']
dir_path = os.path.dirname(os.path.realpath(__file__))
downloadedfile_full = dir_path + downloadedfile

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
testAPI.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
api.to_geodataframe(products)

#Get all data for the whole world
#products = testAPI.query(date = "[NOW-1DAYS TO NOW]")


print('x')