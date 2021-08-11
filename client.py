import socket
from datetime import datetime	#Needed for checking launch day
import argparse	#needed for parsing commandline arguments

###################
#ARGUMENT PARSING & HANDLING START
###################
"""
Arguments passed to the server include:
yr (int) = the year of the desired launch date
month (int) = the month of the desired launch date
day (int) = the calendar day of the desired launch date
hour (int) = the hour of the desired launch time
minute (int) = the minute of the desired launch time
LEO (boolean) = if the launch will only go to low earth orbit
MEO (boolean) = if the launch will only go to medium earth orbit
"""

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
argp.add_argument("-s", "--site", choices=['1','2','3','4','5'], help="Select launch site: (1) Vandenberg, (2) Cape Canaveral", default="1")
group = argp.add_mutually_exclusive_group()
#group.add_argument("-a", "--alt", help="The max altitude (in km) the launch will achieve")
group.add_argument("-L", help="LEO: Launch will stay under 2000km", action='store_true')
group.add_argument("-M", help="MEO: Launch altitude is 2000km < alt < 35,786km", action='store_true')
group.add_argument("-G", help="GEO: Launch altitude is greater than 36,786km; this is the default", action='store_true')
parsed=argp.parse_args()

LEO = False
MEO = False
GEO = False
orbit = "GEO"
if parsed.L:
	LEO = True
	orbit = "LEO"
if parsed.M:
	MEO = True
	orbit = "MEO"


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

###################
#ARGUMENT PARSING & HANDLING END
###################

def siteSelect(s):
	#LATITUDE, LONGITUTE, SITENAME
	sites = {
		"1" : (34.7373367,-120.5843126, "Vandenberg"),	#Vandenberg
		"2" : (28.396837,-80.605659, "Cape Canaveral"),	#Cape Canaveral
		"3" : (19.614492,110.951133, "Wengchang Space Launch Site"),
		"4" : (45.965000,63.305000, "Baikonur Cosmodrome"),
		"5" : (13.719939,80.230425, "Satish Dhawan Space Centre")
	}
	#slat,slong,siteName = sites[s]
	#return (slat,slong,siteName)
	return(sites[s])


timestamp = str(yr) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(minute)
print("Launching from " + siteSelect(site)[2] + " at " + timestamp + " into " + orbit)

HOST = '127.0.0.1'
PORT = 10001

msg = str(yr) + " " + str(month) + " " + str(day) + " " + str(hour) + " " + str(minute) + " " + str(site) + " " + orbit

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	s.sendall((msg+"\r\n").encode())
	#data = s.recv(1024)
	fulldata = ''
	while True:
		data = s.recv(1024)
		fulldata += data.decode()
		if "\r\n\r\n" in data.decode():
			break
		
	print('Received:\r\n' + fulldata)	
#print('Received', repr(data))
