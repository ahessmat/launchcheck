from skyfield.api import Loader,load,Topos,EarthSatellite, wgs84
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.basemap import Basemap
import PIL
import sys	#needed for ingesting commandline arguments
import os.path
from os import path
import argparse	#needed for parsing commandline arguments
from datetime import datetime	#Needed for checking launch day
import requests	#needed to query CelesTrak
from math import radians,cos,sin,asin,sqrt
from tqdm import tqdm	#Added for loading bar

#Function for calculating the distance between 2 points given their latitudes/longtitudes
def haversine(lat1,lon1,lat2,lon2):
	R = 6372.8	#Earth radius km
	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))

	return R*c

#References
#https://space.stackexchange.com/questions/27688/how-do-i-determine-the-ground-track-period-of-a-leo-satellite
#https://www.nasa.gov/mission_pages/station/news/orbital_debris.html
	#4x50x50km box

today = datetime.now()
#Get default date
yy = today.year
mm = today.month
dd = today.day
hh = today.hour
mi = today.minute
def_date = str(yy) + "-" + str(mm) + "-" + str(dd)

#datetime uses 24hr clock, but 01-09 get abbreviated as 1-9
if hh < 10:
	hh = "0"+str(hh)
if mi < 10:
	mi = "0"+str(mi)
def_time = str(hh)+str(mi)
print("CURRENT DATE: " + def_date)
print("CURRENT TIME: " + def_time)

#Configure command line arguments
argp = argparse.ArgumentParser(description="Program for observing space debris relative to a launch position")
argp.add_argument("-d", "--date", help="Date of launch (YYYY-MM-DD)", default=def_date)
argp.add_argument("-t", "--time", help="Time of launch (0000 thru 2359)", default=def_time)
argp.add_argument("-s", "--site", choices=['1','2'], help="Select launch site: (1) Vandenberg, (2) Cape Canaveral", default="1")
group = argp.add_mutually_exclusive_group(required=True)
#group.add_argument("-a", "--alt", help="The max altitude (in km) the launch will achieve")
group.add_argument("-L", help="LEO: Launch will stay under 2000km", action='store_true')
group.add_argument("-M", help="MEO: Launch altitude is 2000km < alt < 35,786km", action='store_true')
group.add_argument("-G", help="GEO: Launch altitude is greater than 36,786km; this is the default", action='store_true')
parsed=argp.parse_args()

LEO = False
MEO = False
GEO = False
if parsed.L:
	LEO = True
if parsed.M:
	MEO = True
if parsed.G:
	GEO = True

#Verify that the date is properly formatted
date = parsed.date
date_arr = date.split('-')
if len(date_arr) != 3 or len(date_arr[0]) != 4 or (len(date_arr[1]) > 2 or len(date_arr[1]) < 1) or (len(date_arr[2]) > 2 or len(date_arr[2]) < 1):
	print("[-] Date format incorrect!")
	sys.exit(0)
else:
	#Assuming there are a correct number of date inputs, validate inputs are numbers
	for num in date_arr:
		if not (num.isdigit()):
			print("[-] Incorrect date entry")
			sys.exit(0)
	yr = int(date_arr[0])
	month = int(date_arr[1])
	day = int(date_arr[2])
	if month > 12 or month < 1:
		print("[-] Month doesn't exist")
		sys.exit(0)
	#Account for leap years
	if month == 2 and yr % 4 == 0 and (day > 29 or day < 1):
		print("[-] Day doesn't exist")
		sys.exit(0)
	#Account for February on non-leap years
	elif month == 2 and yr % 4 != 0 and (day > 28 or day < 1):
		print("[-] Day doesn't exist")
		sys.exit(0)
	elif month % 2 == 0 and (day > 30 or day < 1):
		print("[-] Day doesn't exist")
		sys.exit(0)
	elif month % 2 == 1 and (day > 31 or day < 1):
		print("[-] Day doesn't exist")
		sys.exit(0)

#Verify that the time is formatted appropriately
time = parsed.time
#Time provided should be formatted as HHMM
if len(time) > 4 or len(time) < 2 or not time.isdigit():
	print("[-] Time format incorrect!")
	sys.exit(0)
else:
	if len(time) == 4:
		hour = int(time[:2])
		minute = int(time[2:])
	else:
		hour = int(time[:1])
		minute = int(time[1:])
	if hour > 24 or hour < 0:
		print("[-] Hour incorrectly formatted")
		sys.exit(0)
	elif minute > 59 or minute < 0:
		print("[-] Minute incorrectly formatted")
		sys.exit(0)

#Select the launch site
#TODO: add more sites
#Dev note: each degree of latitude is ~111km at equator; ~85km +- 40deg 
site = parsed.site
#LATITUDE, LONGITUTE, SITENAME
sites = {
	"1" : (34.7373367,-120.5843126, "Vandenberg"),	#Vandenberg
	"2" : (28.396837,-80.605659, "Cape Canaveral")	#Cape Canaveral
}
slat,slong,siteName = sites[site]
#slat = int(slat)
#slong = int(slong)


#Initiate some variables to be used in the construction of Earth's representation
halfpi, pi, twopi = [f*np.pi for f in (0.5, 1, 2)]
degs, rads = 180/pi, pi/180

#Loader() can specify where to load our .bsp file to
#This pulls planet-relative data for timescale
#Defaults to wherever the program is ran
data = load('de421.bsp')	#skyfield intuits that it needs to download this file; see "Ephemeris download links"
ts = load.timescale()
earth = data['earth']

#TODO
#Implement function to call Celestrak and scrape TLE data
fig = plt.figure(figsize=(10,8))
#m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180,)
#m = Basemap(projection='cyl', llcrnrlat=19, urcrnrlat=31, llcrnrlon=-92, urcrnrlon=-72,)
m = Basemap(projection='cyl', llcrnrlat=(slat-10), urcrnrlat=(slat+10), llcrnrlon=(slong-10), urcrnrlon=(slong+10),)
#m.bluemarble()
m.shadedrelief()
plt.scatter(slong,slat)
plt.annotate(siteName, (slong,slat))

#active_sats = requests.get("http://celestrak.com/NORAD/elements/iridium-33-debris.txt")
#active_sats = requests.get("http://celestrak.com/NORAD/elements/active.txt")

#tle1 = active_sats.text.splitlines()

tle1 = """ISS
1 25544U 98067A   18157.92534723  .00001336  00000-0  27412-4 0  9990
2 25544  51.6425  69.8674 0003675 158.7495 276.7873 15.54142131116921""".splitlines()

for idx,line in enumerate(tqdm(tle1)):
	if idx%3 == 0:
		name = line.strip()	#Removes trailing white space
		L1 = tle1[idx+1]
		L2 = tle1[idx+2]

		#minutes = np.arange(60. * 24 * 1)         # (1) day
		time = ts.utc(yr, month, day, hour, range(minute-5,minute+5))  # start June 1, 2018
		#time = ts.utc(yr, month, day, hour, minute)

		satl = EarthSatellite(L1,L2)
		satlloc = satl.at(time)
		satl_alt = satlloc.distance().km - 6371	#Get satellite altitude by subtracing earth's mean radius (km)
		if LEO and satl_alt.all() > 2000:
			continue
		if MEO and satl_alt.all() > 36786:
			continue
		sub = satlloc.subpoint()
		lon = sub.longitude.degrees
		lat = sub.latitude.degrees
		#print((lon))
		breaks   = np.where(np.abs(lon[1:]-lon[:-1]) > 30)  #don't plot wrap-around
		lon, lat    = lon[:-1], lat[:-1]
		lon[breaks] = np.nan

		#t = haversine(lat,lon,slat,slong)
		#print(t)
		plt.plot(lon,lat, label=name)

		#"""
		#Check the first longtitude
		if np.isnan(lon[0]) or lon[0] < m.llcrnrlon or lon[0] > m.urcrnrlon:
			end = lon[len(lon)-1]
			#Check the last longtitude
			if np.isnan(end) or end < m.llcrnrlon or end > m.urcrnrlon:
				#If both fall outside of our boundary, don't plot it
				continue
		#Do the same with latitudes
		if np.isnan(lat[0]) or lat[0] < m.llcrnrlat or lat[0] > m.urcrnrlat:
			end = lat[len(lat)-1]
			if np.isnan(end) or end < m.llcrnrlat or end > m.urcrnrlat:
				continue
		#"""
		
		#plt.scatter(lon,lat)
	else:
		continue

###################

#x, y = m(-122.3, 47.6)
#plt.plot(x, y, 'ok', markersize=5)
#plt.text(x, y, ' Seattle', fontsize=12);
#plt.legend()
plt.show()
