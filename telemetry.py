from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import gpxpy
import moviepy as mp
import json

lat = []
lon = []

fig = plt.figure(facecolor = '1')
# plt.figure()

# ax = plt.Axes(fig, [0.1, 0.1, 1., 1.], )
# ax.set_aspect('equal')
# ax.set_axis_off()
plt.axis('off') 
# fig.add_axes(ax)

frop = mp.VideoFileClip('20250327_131046.mp4')

print( frop.reader.infos.get('metadata').get('creation_time'))

print(frop.duration)

gpx_filename = 'activity_18651877796.gpx'
gpx_file = open(gpx_filename, 'r', encoding='utf-8')
gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            lat.append(point.latitude)
            lon.append(point.longitude)

print(len(lat))
plt.plot(lon, lat, color = 'red', lw = 1, alpha = 1)

lat = []
lon = []

distance = gpx.length_2d()

plt.figtext(.5,.9,'Pace', fontsize=30, ha='center')
# plt.figtext(.135,.85,'Days: 4',fontsize=15,ha='left',color='blue')
# plt.figtext(.135,.82,'Miles: %i' %distance,fontsize=15,ha='left',color='blue')

# plt.ylabel("Latitude",fontsize=25, ha='center')
# plt.xlabel("Longitude",fontsize=25, ha='center')

plt.savefig('gpx_plot.png', dpi=300,transparent=True)

# plt.savefig('gpx_plot.png', dpi=300, bbox_inches='tight')
# plt.show()
gpx_file.close()

# https://zulko.github.io/moviepy/getting_started/quick_presentation.html

# Load file example.mp4 and extract only the subclip from 00:00:10 to 00:00:20


# Generate a text clip. You can customize the font, color, etc.
txt_clip = mp.TextClip(
    font="Arial", text="km's: " + str(distance), font_size=70, color="white"
)
img_clip = mp.ImageClip("gpx_plot.png").with_duration(frop.duration)
# Say that you want it to appear for 10s at the center of the screen
txt_clip = txt_clip.with_position("center").with_duration(frop.duration)

# Overlay the text clip on the first video clip
video = mp.CompositeVideoClip([frop, txt_clip, img_clip])

# Write the result to a file (many options available!)
video.write_videofile("result.mp4")


# print(frop.metadata)


