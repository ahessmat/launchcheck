# launchcheck

## TODO:
-Implement a method for ingesting TLE data
-Implement a means for specifying/plotting launch destination
-Restrict plots of debris to only those that pose risk to launch site/time
-Create server that independently queries for TLE data and serves to test.py; this will speed up performance

## Summary:
This python3 program is intended to identify satellites and space debris that pass near a given launch site on Earth at user-specified time in the future. It leverages the skyfield API for handling orbital mechanics and matplotlib for rendering graphical ground tracks.

The program leverages a client/server interaction on the local machine communicating across port 10001. At startup, server.py queries the available Two Line Element (TLE) data available for free from CelesTrak; server.py will execute additional queries to update its database once every 2 minutes. After getting setup, server.py will be ready to receive requests from client.py

The user may pass a variety of arguments to client.py, customizing the launch site location and time of the launch. After submitting the arguments from the command line, client.py passes the arguments to server.py, which processes the request on client.py's behalf.

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  Date of launch (YYYY-MM-DD)
  -t TIME, --time TIME  Time of launch (0000 thru 2359)
  -s {1,2,3,4,5}, --site {1,2,3,4,5}
	(1) Vandenberg
	(2) Cape Canaveral
	(3) Wengchang Space Launch Site
	(4) Baikonur Cosmodrome
	(5) Satish Dhawan Space Centre
  -L                    LEO: Launch will stay under 2000km
  -M                    MEO: Launch altitude is 2000km < alt < 35,786km
  -G                    GEO: Launch altitude is greater than 36,786km; this is the default


