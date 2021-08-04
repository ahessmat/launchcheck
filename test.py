import socket
import requests	#needed to query CelesTrak

HOST = '127.0.0.1'
PORT = 10001

#TODO
#implement multi-threaded calls to celestrak
#https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/

#implement client/server model

celestrak_lists = ['active','geo','amateur','analyst','argos','beidou','2012-044','cosmos-2251-debris','cubesat','dmc','resource','education','engineering','1999-025','galileo','geodetic','globalstar','glo-ops','gnss','goes','gorizont','gps-ops','2019-006','intelsat','iridium','iridium-33-debris','iridium-NEXT','tle-new','military','molniya','nnss','noaa','oneweb','orbcomm','other','other-comm','planet','radar','raduga','musson','sbas','satnogs','sarsat','ses','science','stations','spire','starlink','tdrss','weather']

dic = {}

for satlist in celestrak_lists:
	req = requests.get("http://celestrak.com/NORAD/elements/" + satlist + ".txt")
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



def test():
	print("WORKS")
