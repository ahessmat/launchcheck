from skyfield.api import Loader,load,Topos,EarthSatellite, wgs84
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.basemap import Basemap
import PIL
#References
#https://space.stackexchange.com/questions/27688/how-do-i-determine-the-ground-track-period-of-a-leo-satellite

#Initiate some variables to be used in the construction of Earth's representation
halfpi, pi, twopi = [f*np.pi for f in (0.5, 1, 2)]
degs, rads = 180/pi, pi/180

#Loader() can specify where to load our .bsp file to
#Defaults to wherever the program is ran
#load = Loader('~/Desktop/launchcheck/SkyData')

data = load('de421.bsp')	#skyfield intuits that it needs to download this file; see "Ephemeris download links"
ts = load.timescale()

earth = data['earth']

#Test TLE data of ISS
TLE = """1 25544U 98067A   18157.92534723  .00001336  00000-0  27412-4 0  9990
2 25544  51.6425  69.8674 0003675 158.7495 276.7873 15.54142131116921"""

L1, L2 = TLE.splitlines()
minutes = np.arange(60. * 24 * 1)         # (1) days
time = ts.utc(2018, 6, 1, 0, minutes)  # start June 1, 2018
#time = ts.now()

ISS = EarthSatellite(L1,L2)
sub = ISS.at(time).subpoint()
lon = sub.longitude.degrees
lat = sub.latitude.degrees
breaks   = np.where(np.abs(lon[1:]-lon[:-1]) > 30)  #don't plot wrap-around
lon, lat    = lon[:-1], lat[:-1]
lon[breaks] = np.nan

fig = plt.figure(figsize=(10,8))
m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180,)
m.bluemarble()

plt.plot(lon,lat)

#x, y = m(-122.3, 47.6)
#plt.plot(x, y, 'ok', markersize=5)
#plt.text(x, y, ' Seattle', fontsize=12);
plt.show()
