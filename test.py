import socket
import requests	#needed to query CelesTrak
import threading	#needed for multi-threading
from queue import Queue #needed for shared queue
import time	#needed for sleep() function

HOST = '127.0.0.1'
PORT = 10001

#TODO
#implement multi-threaded calls to celestrak
#https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/

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
			#print(req.status_code)
			if req.status_code == 200:
				t = req.text.splitlines()
				dic[item] = t[0]
			#listQ.task_done()
		else:
			print("EXITING")
			break

#Populate listQ	
for satlist in celestrak_lists:
	listQ.put(satlist)
print()
print("##############")
print()
#Create threadpool
for x in range(5):
	thread = threading.Thread(target = threadtask)
	#thread.daemon = True
	thread.start()
	thread.join()	#This has all the threads rejoin after all of the requests are processed

print(dic)

"""
for satlist in celestrak_lists:
	req = requests.get("http://celestrak.com/NORAD/elements/" + satlist + ".txt")
	if req.status_code == 200:
		dic[satlist] = req.text
print("DONE")





with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST,PORT))
	s.listen()
	conn, addr = s.accept()
	with conn:
		print('Connected by', addr)
		while True:
			data = conn.recv(1024)
			if not data:
				break
			conn.sendall(data)
"""


def test():
	print("WORKS")
