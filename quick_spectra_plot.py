"""
Plot spectra from UV and/or optical for object
from a <xyz>.dat file
"""

from matplotlib import pyplot as plt
from astropy import units as u
import numpy as np
import glob as g

# select file from list of available .dat files
flist = g.glob("*/*.dat")
for i,f in enumerate(flist):
	print("{}\t{}".format(i,f))
fname = flist[int(input("Give index of desired file:\t"))]

plot_data = np.genfromtxt(fname, delimiter=' ', usecols=(0,1))
xmin = np.amin(plot_data[:,0])
xmax = np.amax(plot_data[:,0])
ymin = np.amin(np.log10(plot_data[:,1]))
ymax = np.amax(np.log10(plot_data[:,1]))

plt.figure()
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.plot(plot_data[:,0], np.log10(plot_data[:,1]), c = 'r')
plt.show()
