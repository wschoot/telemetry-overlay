import matplotlib.pyplot as plt
import gpxpy
import datetime
import moviepy as mp
from PIL import Image, ImageFont, ImageDraw 
import os

# Set constants
EXTRA_TIME_AROUND_MOVIE = 10 # seconds
ROUTE_IMAGE_FILE = 'gpx_plot.png'
IMAGE_FILE_RESIZED = 'new_image_resized.png'
RESULTING_MOVIE = 'end_result.mp4'

# get movies
MOVIE_FILES = []
for file in sorted(os.listdir(".")):
    if file.endswith(".mp4") and file != RESULTING_MOVIE:
        MOVIE_FILES.append(file)
    if file.endswith(".gpx"):
        GPX_FILENAME = file

if len(MOVIE_FILES) == 0:
    exit("No movies found")
if GPX_FILENAME is None:
    exit("No GPX found")

# Get GPX info
gpx_file = open(GPX_FILENAME, 'r')
gpx = gpxpy.parse(gpx_file)

gpx_info = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            gpx_info.append({
                "lat": point.latitude,
                "lon": point.longitude,
                "time": point.time
            })
            
distance = gpx.length_2d() / 1000
gpx_file.close()

# Get movie info
all_times = {}
for MOVIE_FILE in MOVIE_FILES:
    # Get the movie file: get info and rotate it
    movie_info = mp.VideoFileClip(MOVIE_FILE)
    creation_time = movie_info.reader.infos['metadata']['creation_time']
    duration = movie_info.duration
    movie_info_rotated = movie_info.resized(movie_info.size[::-1])

    # determine the time period of the movie; Add 10 seconds before+after
    begin_time = datetime.datetime.fromisoformat(creation_time)  - datetime.timedelta(seconds=EXTRA_TIME_AROUND_MOVIE)
    end_time = begin_time + datetime.timedelta(seconds=duration) + datetime.timedelta(seconds=2*EXTRA_TIME_AROUND_MOVIE)
    all_times[MOVIE_FILE] = {
        "begin_time": begin_time,
        "end_time": end_time,
        "movie": movie_info_rotated,
        "duration": duration,
    }
del movie_info, creation_time, duration, movie_info_rotated, begin_time, end_time

videos = []
for movie_iter in all_times.values():
    movie_info = movie_iter['movie']
    # Plot GPX
    fig = plt.figure(facecolor = '1')
    plt.axis('off') 

    for i in range(len(gpx_info)):
        gpx_time = gpx_info[i]['time']
        if i == 0:
            continue
        line_color = 'green'
        for iter in all_times.values():
            iter_begin = iter['begin_time']
            iter_end = iter['end_time']
            if gpx_time >= iter_begin and gpx_time <= iter_end:
                line_color = 'red'
        if gpx_time >= movie_iter['begin_time'] and gpx_time <= movie_iter['end_time']:
                # current part
                line_color = 'yellow'
        plt.plot(
            [gpx_info[i-1]['lon'],gpx_info[i]['lon']], # longitude
            [gpx_info[i-1]['lat'],gpx_info[i]['lat']], # latitude
            color=line_color, # line color
            lw=8, # line width
            alpha = 0.5 # transparancy level
        )

    # Save the route
    plt.savefig(ROUTE_IMAGE_FILE, dpi=300,transparent=True)

    # Create a transparant image of correct size
    width, height = movie_info.size[0], movie_info.size[1]
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

    img_clip = mp.ImageClip(IMAGE_FILE_RESIZED).with_duration(movie_iter['duration'])


    # Overlay the text clip on the first video clip
    video = mp.CompositeVideoClip([movie_iter['movie'], img_clip])
    videos.append(video)
    

# Write the result to a file
# video.preview(fps=5, audio=False)
clips = [videos[0].with_end(4)]
for vid in videos[1:]:
    clips.append(vid.with_start(1).with_effects([mp.vfx.CrossFadeIn(1)]))
final_clip = mp.CompositeVideoClip(clips)

final_clip.write_videofile(RESULTING_MOVIE, fps=4, threads=24, preset='ultrafast')
