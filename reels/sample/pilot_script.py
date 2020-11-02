from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
import pandas
import gizeh
from os import listdir, mkdir
from os.path import isfile, join, exists
import math
import random

# Folders
clip_folder = 'clips/'
filler_folder = 'filler/'
song_folder = 'songs/'
config_folder = 'config/'

for folder in [clip_folder, filler_folder, song_folder, config_folder]:
    if not exists(folder):
        mkdir(folder)

# Song Configuration
song_file = song_folder + 'stressed_out.mp3'
song_segments = [(0, 'verse'),
(27, 'hook'),
(44, 'prechorus'),
(51.7, 'chorus'),
(62.5, 'verse'),
(97.5, 'hook'),
(115.5, 'prechorus'),
(120.5, 'chorus'),
(131, 'bridge'),
(155.5, 'prechorus'),
(160.5, 'chorus'),
(176.5, 'outro')]

bpm = 85

# Configuration Configuration
# ===============================
clip_config_file = config_folder + 'config0.csv'
default_climax = 5.0
raw_clip_file_names = [f for f in listdir(clip_folder) if isfile(join(clip_folder, f))]
raw_filler_file_names = [f for f in listdir(filler_folder) if isfile(join(filler_folder, f))]
with open(clip_config_file, 'r') as config:
    if config.read(1):
        config.seek(0)
        df = pandas.read_csv(config)
    else:
        df = pandas.DataFrame(data=[(f, default_climax) for f in raw_clip_file_names], columns=['name', 'climax'])

clip_dict = {}
clip_list = []
for item in df.to_dict('records'):
    clip_dict[item['name']] = item['climax']
    clip_list.append((item['name'], item['climax']))
for name in raw_clip_file_names:
    if not name in clip_dict:
        print('Adding ' + name)
        clip_dict[name] = default_climax
        clip_list.append((name, default_climax))
        print(clip_dict[item['name']])

pandas.DataFrame(data=[(name, clip_dict[name]) for name in clip_dict], columns=['name', 'climax']).to_csv(clip_config_file, columns=['name', 'climax'], index=False)
# ===============================

period = 60 / bpm * 2
partial_period = period * 2 / 3

song = AudioFileClip(song_file)

filler_index = 0
def get_filler_index():
    return filler_index % len(raw_filler_file_names)
clip_index = 0
def get_clip_index():
    return clip_index % len(clip_list)
total_video_time = 0
segment_index = 0
videos = []

while segment_index < len(song_segments):

    print('\n=== NEW SEGMENT ===')
    print('type: ' + song_segments[segment_index][1])
    print('filler index: ' + str(filler_index))
    print('clip index: ' + str(clip_index))
    print('total video time: ' + str(total_video_time))
    print('segment index: ' + str(segment_index))
    print('videos count: ' + str(len(videos)))

    if segment_index < len(song_segments) - 1:
        segment_duration = song_segments[segment_index + 1][0] - song_segments[segment_index][0]
    else:
        segment_duration = song.duration - song_segments[segment_index][0]

    print('segment duration: ' + str(segment_duration))

    if song_segments[segment_index][1] in ['verse', 'hook', 'bridge', 'outro']:
        to_add = []
        to_add_length = 0
        while to_add_length < segment_duration:
            print('preparing clip: ' + raw_filler_file_names[get_filler_index()])
            clip = VideoFileClip(filler_folder + raw_filler_file_names[get_filler_index()])
            to_add_length += clip.duration
            to_add.append(clip)
            filler_index += 1
        ratio = segment_duration / to_add_length
        for clip in to_add:
            clip = clip.set_duration(clip.duration * ratio)
            videos.append(clip)
            print('added clip of length ' + str(clip.duration))
            total_video_time += clip.duration
        segment_index += 1
    elif song_segments[segment_index][1] in ['prechorus']:
        to_add = []
        to_add_length = 0
        orig_clip_index = clip_index
        clip_count = math.floor(segment_duration / partial_period)
        correction_ratio = (segment_duration / partial_period) / clip_count
        for i in range(clip_count):
            print('preparing clip: ' + clip_list[get_clip_index()][0])
            clip = VideoFileClip(clip_folder + clip_list[get_clip_index()][0])
            clip = clip.subclip(clip_list[get_clip_index()][1] - 1.2*partial_period*correction_ratio, clip_list[get_clip_index()][1] - 0.2*partial_period*correction_ratio)
            to_add_length += clip.duration
            to_add.append(clip)
            clip_index += 1
        for clip in to_add:
            videos.append(clip)
            print('added clip of length ' + str(clip.duration))
            total_video_time += clip.duration
        clip_index = orig_clip_index
        segment_index += 1
    elif song_segments[segment_index][1] in ['chorus']:
        to_add = []
        to_add_length = 0
        if videos:
            videos[-1] = videos[-1].set_end(videos[-1].duration - 0.4*period)
            print('Last video before chorus was fixed')
        clip_count = math.floor((segment_duration + 0.4*period) / period)
        correction_ratio = clip_count / ((segment_duration + 0.4*period) / period)
        for i in range(clip_count):
            print('preparing clip: ' + clip_list[get_clip_index()][0])
            clip = VideoFileClip(clip_folder + clip_list[get_clip_index()][0])
            clip = clip.subclip(clip_list[get_clip_index()][1] - 0.6*period*correction_ratio, clip_list[get_clip_index()][1] + 0.4*period*correction_ratio)
            to_add_length += clip.duration
            to_add.append(clip)
            clip_index += 1
        for clip in to_add:
            videos.append(clip)
            print('added clip of length ' + str(clip.duration))
            total_video_time += clip.duration
        segment_index += 1
    else:
        raise NotImplementedError('The segment type ' + song_segments[segment_index][1] + ' is not supported')


# for s in range(len(showcase_segments)):
#     if s == 0:
#         downtime_length = showcase_segments[s][0] - (period * 0.6)
#     else:
#         downtime_length = (showcase_segments[s][0] - showcase_segments[s - 1][1]) - (period * 0.6)
#     exposition_clip_files = random.sample(clip_files, math.floor(downtime_length / 3.5) )
#     for exp_clip_file in exposition_clip_files:
#         clip = VideoFileClip(join(clip_folder, exp_clip_file))
#         clip = clip.set_duration(downtime_length / len(exposition_clip_files))
#         clips.append(clip)
#         print('Downtime Clip Added!')
#
#     offset = clip_index
#     for i in range(math.floor((showcase_segments[s][1] - showcase_segments[s][0]) / period)):
#         clip = VideoFileClip(join(clip_folder, clip_files[i + offset]))
#         clip = clip.subclip(5 - (period * .6), 5 + (period * .4))
#         clips.append(clip)
#         print('Showcase Clip Added!')
#         clip_index += 1

output = concatenate_videoclips(videos)
output = output.set_audio(CompositeAudioClip([output.audio, song]))
# final_clip = final_clip.set_audio(AudioFileClip(song_file))
output.write_videofile('./output2.mp4')
