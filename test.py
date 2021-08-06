import socket	#needed for client/server communications
import requests	#needed to query CelesTrak
import threading	#needed for multi-threading
from queue import Queue #needed for shared queue
import time	#needed for sleep() function
from tqdm import tqdm	#Added for loading bar
from datetime import datetime	#Needed for checking launch day
from skyfield.api import Loader,load,Topos,EarthSatellite, wgs84
from skyfield.timelib import Time
import matplotlib.pyplot as plt	#needed for matplotlib
from mpl_toolkits.basemap import Basemap	#needed for projecting globe graphic
import numpy as np


#Server overhead
HOST = '127.0.0.1'
PORT = 10001
#Skyfield overhead
data = load('de421.bsp')	#skyfield intuits that it needs to download this file; see "Ephemeris download links"
ts = load.timescale()
earth = data['earth']

#TODO
#implement multi-threaded calls to celestrak
#https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/

#Implement function that returns text of color
#Colors
#{'#bcbd22', '#d62728', '#17becf', '#7f7f7f', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#9467bd', '#8c564b'}
def getColor(code):
	colorcode = {
		'#bcbd22' : "YELLOW",	#Sick yellow
		'#d62728' : "RED",	#Red
		'#17becf' : "CYAN",	#Teal
		'#7f7f7f' : "GREY",	#Grey
		'#ff7f0e' : "ORANGE",	#Orange
		'#2ca02c' : "GREEN",	#Forest Green
		'#1f77b4' : "BLUE",	#Blue
		'#e377c2' : "PINK",	#Pink
		'#9467bd' : "PURPLE",	#Purple
		'#8c564b' : "BROWN"	#Brown
	}
	return colorcode[code]

#Function for calculating the distance between 2 points given their latitudes/longtitudes (haversine)
def haversine(lat1,lon1,lat2,lon2):
	lon1,lat1,lon2,lat2 = map(np.radians, [lon1,lat1,lon2,lat2])
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
	c = 2 * np.arcsin(np.sqrt(a))
	km = 6367 * c
	return km

def siteSelect(s):
	#LATITUDE, LONGITUTE, SITENAME
	sites = {
		"1" : (34.7373367,-120.5843126, "Vandenberg"),	#Vandenberg
		"2" : (28.396837,-80.605659, "Cape Canaveral"),	#Cape Canaveral
		"3" : (110.951133,19.614492, "Wengchang Space Launch Site"),
		"4" : (63.305000,45.965000, "Baikonur Cosmodrome"),
		"5" : (80.230425,13.719939, "Satish Dhawan Space Centre")
	}
	#slat,slong,siteName = sites[s]
	#return (slat,slong,siteName)
	return(sites[s])

def processRequest():
	yr = 2022
	month = 12
	day = 15
	hour = 13
	minute = 15
	slat = 28.396837
	slong = -80.605659
	siteName = "Cape Canaveral"
	LEO = False
	MEO = False
	
	#Setup the figure
	fig = plt.figure(figsize=(10,8))
	m = Basemap(projection='cyl', llcrnrlat=(slat-10), urcrnrlat=(slat+10), llcrnrlon=(slong-10), urcrnrlon=(slong+10),)
	m.shadedrelief()
	#Plot the launch site
	plt.scatter(slong,slat)
	plt.annotate(siteName, (slong,slat))

	for tle in tqdm(dic.values()):
		name = tle[0]
		L1 = tle[1]
		L2 = tle[2]
		
		#Evaluate the debris path 
		time = ts.utc(yr, month, day, hour, range(minute,minute+10))

		satl = EarthSatellite(L1,L2)
		satlloc = satl.at(time)
		satl_alt = satlloc.distance().km - 6371	#Get satellite altitude by subtracing earth's mean radius (km)
		#Scrub satellites that are above destination altitude
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

		#Calculate distance between ground plot and launch site using haversine formula
		distances = haversine(lat,lon,slat,slong)
		np.seterr(all = "ignore")
		closest_km = np.nanmin(distances)
		if np.isnan(closest_km):	#I need to suppress the RunTimeWarning error message at some point
			continue
		idx_closest_km = np.nanargmin(distances)
		timestamp = str(yr) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(minute+idx_closest_km)

		#TODO
		#Matplotlib is not threadsafe
		#Have threads push plot arguments to a queue, then plot in unified process
		p = plt.plot(lon,lat, label=name)
		color = getColor(p[-1].get_color())

		#Scrub ground tracks that do not appear within our mappable window
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

		#tracker.append((name,closest_km,timestamp,color, satl_alt[idx_closest_km]))
		#plt.scatter(lon,lat)
	plt.show()

#implement client/server model

#Identifies the various lists managed by Celestrak
celestrak_lists = ['active','geo','amateur','analyst','argos','beidou','2012-044','cosmos-2251-debris','cubesat','dmc','resource','education','engineering','1999-025','galileo','geodetic','globalstar','glo-ops','gnss','goes','gorizont','gps-ops','2019-006','intelsat','iridium','iridium-33-debris','iridium-NEXT','tle-new','military','molniya','nnss','noaa','oneweb','orbcomm','other','other-comm','planet','radar','raduga','musson','sbas','satnogs','sarsat','ses','science','stations','spire','starlink','tdrss','weather']

dic = {}

#This is a queue that is populated with elements from celestrak_lists periodically for threads to action
listQ = Queue()
listQlock = threading.Lock()
cond = threading.Condition()	#Condition object

def threadtask():
	#Keep processing satlists until they have all been processed
	while True:
		if not (listQ.empty()):
			item = listQ.get()
			req = requests.get("http://celestrak.com/NORAD/elements/" + item + ".txt")
			if req.status_code == 200:
				tle = req.text.splitlines()
				#Process the response from celestrak, updating the 
				for idx,line in enumerate(tqdm(tle)):
					if idx%3 == 0:
						name = line.strip()	#Removes trailing white space
						L1 = tle[idx+1]
						L2 = tle[idx+2]
						catnum = L2.split()[1]
						if catnum in dic.keys():
							continue
						else:
							dic[catnum] = (name, L1, L2)
			#listQ.task_done()
		else:
			print("EXITING")
			break
start = time.time()
#Populate listQ	
for satlist in celestrak_lists:
	listQ.put(satlist)
print()
print("##############")
print()
#Create threadpool
for x in range(1):
	thread = threading.Thread(target = threadtask)
	#thread.daemon = True
	thread.start()
	thread.join()	#This has all the threads rejoin after all of the requests are processed

print(len(dic))
end = time.time()

print(end - start)

"""
for satlist in celestrak_lists:
	req = requests.get("http://celestrak.com/NORAD/elements/" + satlist + ".txt")
	if req.status_code == 200:
		dic[satlist] = req.text
print("DONE")

"""

s_time = datetime.now()
while True:
	print("TEST")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST,PORT))
		s.listen()
		conn, addr = s.accept()
		msg = ""
		with conn:
			print('Connected by', addr)
			while True:
				data = conn.recv(1024)
				msg += data.decode()
				#if data.decode() == "Hello!":
				#if "\r\n\r\n" in msg:
					#print(msg)
					#print("END")
				if not data:
					print((datetime.now() - s_time).total_seconds())
					print(msg)
					client_msg = msg.split(" ")
					myr = client_msg[0]
					mmonth = client_msg[1]
					mday = client_msg[2]
					mhour = client_msg[3]
					mmin = client_msg[4]
					msite = client_msg[5]
					morbit = client_msg[6]
					print(siteSelect(msite))
					#processRequest()
					break
				conn.sendall(data)



def test():
	print("WORKS")
