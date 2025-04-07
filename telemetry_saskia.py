from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import gpxpy
import datetime
import moviepy as mp
from PIL import Image, ImageFont, ImageDraw 

# Set constants
MOVIE_FILE = '20250327_131825.mp4'
# MOVIE_FILE = '20250327_131046.mp4'
GPX_FILENAME = 'activity_18651877796.gpx'
EXTRA_TIME_AROUND_MOVIE = 10 # seconds
ROUTE_IMAGE_FILE = 'gpx_plot.png'
IMAGE_FILE_RESIZED = 'new_image_resized.png'

# Get the movie file: get info and rotate it
movie_info = mp.VideoFileClip(MOVIE_FILE)
creation_time = movie_info.reader.infos['metadata']['creation_time']
duration = movie_info.duration
movie_info_rotated = movie_info.resized(movie_info.size[::-1])

# determine the time period of the movie; Add 10 seconds before+after
begin_time = datetime.datetime.fromisoformat(creation_time)  - datetime.timedelta(seconds=EXTRA_TIME_AROUND_MOVIE)
end_time = begin_time + datetime.timedelta(seconds=duration) + datetime.timedelta(seconds=2*EXTRA_TIME_AROUND_MOVIE)

# Get GPX file: get info and plot it
fig = plt.figure(facecolor = '1')
plt.axis('off') 

gpx_file = open(GPX_FILENAME, 'r')
gpx = gpxpy.parse(gpx_file)

lat = []
lon = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            lat.append(point.latitude)
            lon.append(point.longitude)
            if point.time >= begin_time and point.time <= end_time:
                line_color = 'red'
            else:
                line_color = 'green'
            plt.plot(lon[-2:], lat[-2:], color=line_color, lw=8, alpha = 0.5)

del lat
del lon

distance = gpx.length_2d() / 1000
gpx_file.close()

# Add km's to the route
# plt.figtext(.5, .9, s=str(round(distance,2)) + ' km', fontsize=30, ha='center')

# Save the route
plt.savefig(ROUTE_IMAGE_FILE, dpi=300,transparent=True)
# plt.show()

# Create a transparant image of correct size
width, height = movie_info.size[1], movie_info.size[0]
transparant_image = Image.new('RGB', (width, height), color='white')
transparant_image.putalpha(0)

# Locally resize route image
base_width = int(width*2/3) # Change this if you want route smaller than whole screen
route = Image.open(ROUTE_IMAGE_FILE)
wpercent = (base_width / float(route.size[0]))
hsize = int((float(route.size[1]) * float(wpercent)))
route = route.resize((base_width, hsize), Image.Resampling.LANCZOS)

# Paste resized route image into transparant image
new_image = transparant_image.copy()
new_image.save(IMAGE_FILE_RESIZED)
new_image = Image.open(IMAGE_FILE_RESIZED) # Need save+open for Draw to work?
new_image.paste(route, (0,height - hsize))
font = ImageFont.load_default(size=80)
draw = ImageDraw.Draw(new_image).text(
    (2/3 * width,height - hsize/2), # coordinates
    "km's: " + str(round(distance,2)), # text
    font=font
)
new_image.save(IMAGE_FILE_RESIZED)

img_clip = mp.ImageClip(IMAGE_FILE_RESIZED).with_duration(duration)


# Overlay the text clip on the first video clip
video = mp.CompositeVideoClip([movie_info_rotated, img_clip])

# Write the result to a file (many options available!)
video.write_videofile("result.mp4", fps=2)
