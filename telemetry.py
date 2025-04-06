from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import gpxpy

lat = []
lon = []

fig = plt.figure(facecolor = '1')
# plt.figure()

# ax = plt.Axes(fig, [0.1, 0.1, 1., 1.], )
# ax.set_aspect('equal')
# ax.set_axis_off()
plt.axis('off') 
# fig.add_axes(ax)

gpx_filename = 'activity_18651877796.gpx'
gpx_file = open(gpx_filename, 'r')
gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            lat.append(point.latitude)
            lon.append(point.longitude)
    
plt.plot(lon, lat, color = 'red', lw = 1, alpha = 1)

lat = []
lon = []

distance = gpx.length_2d()
distance/=1609.344

# plt.figtext(.5,.9,'Hiking in Colombia, 2019', fontsize=30, ha='center')
# plt.figtext(.135,.85,'Days: 4',fontsize=15,ha='left',color='blue')
# plt.figtext(.135,.82,'Miles: %i' %distance,fontsize=15,ha='left',color='blue')

# plt.ylabel("Latitude",fontsize=25, ha='center')
# plt.xlabel("Longitude",fontsize=25, ha='center')

plt.savefig('gpx_plot.png', dpi=300,transparent=True)

# plt.savefig('gpx_plot.png', dpi=300, bbox_inches='tight')
plt.show()
gpx_file.close()
