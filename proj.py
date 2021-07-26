from skyfield.api import Loader,load, EarthSatellite, wgs84
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import PIL

#Initiate some variables to be used in the construction of Earth's representation
halfpi, pi, twopi = [f*np.pi for f in (0.5, 1, 2)]
degs, rads = 180/pi, pi/180

#Loader() can specify where to load our .bsp file to
#Defaults to wherever the program is ran
#load = Loader('~/Desktop/launchcheck/SkyData')

data = load('de421.bsp')	#skyfield intuits that it needs to download this file; see "Ephemeris download links"
ts = load.timescale()

earth = data['earth']

bm = PIL.Image.open('blue_marble.jpg')
#rescale image; divide by 256 for RGB values
#kept readjusted d/# value; lower # means better imaging, but slower rendering balanced at ~20
bm = np.array(bm.resize([int(d/20) for d in bm.size]))/256.

# coordinates of the image - don't know if this is entirely accurate, but probably close
lons = np.linspace(-180, 180, bm.shape[1]) * np.pi/180 
lats = np.linspace(-90, 90, bm.shape[0])[::-1] * np.pi/180 

t = ts.now()
losA = wgs84.latlon(-118.411741,+34.021055)
topo = losA.at(t)
a,b,c = topo.position.km
print(topo.position.km)

fig = plt.figure(figsize=[10,8])
ax = fig.add_subplot(1,1,1, projection='3d')

x = np.outer(np.cos(lons), np.cos(lats)).T
y = np.outer(np.sin(lons), np.cos(lats)).T
z = np.outer(np.ones(np.size(lons)), np.sin(lats)).T
ax.plot_surface(x, y, z, rstride=4, cstride=4, facecolors = bm)
plt.plot(a,b,c)

plt.show()
