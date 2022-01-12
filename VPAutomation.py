from moviepy.audio.AudioClip import AudioClip
import moviepy.editor as mp
from moviepy.editor import *
from scipy.io.wavfile import read
import numpy as np
import math
import statistics
import os
import tempfile
from pathlib import Path
path = Path.home()/"Videos"/"VPAutomation"
if os.path.exists(path) == True:
    os.chdir(path)
else:
    os.makedirs(path)
    os.chdir(path)

#get locations of video files and final file name
video1_location =''
video1_valid = False
while video1_valid == False:
    video1_location = input("Input location of video file 1 (Host file): ")
    if os.path.exists(video1_location):
        video1_valid = True
    else:
        print("The file does not exist or the path is incorrect") 

video2_location = ''
video2_valid = False
while video2_valid == False:
    video2_location = input("Input location of video file 2: ")
    if os.path.exists(video2_location):
        video2_valid = True
    else:
        print("The file does not exist or the path is incorrect") 

final_name = input("Input final video file name: ")
final_name+='.mp4'
video1=mp.VideoFileClip(video1_location)
video2=mp.VideoFileClip(video2_location)

##code for audio
video1.audio.write_audiofile(r"audio1.wav")
video2.audio.write_audiofile(r"audio2.wav")
def get_dBs(audio_file):#returns array of average decibel values for every 1 second chunk
    samprate, wavdata = read(audio_file)
    chunks = np.array_split(wavdata, (wavdata.size/(samprate/2)/4)) #all samples in wav file, each array in chunks is all the samples in a one second segment.
    #len of chunks is approx. equal to number of seconds
    mean = []
    for chunk in range(len(chunks)):
        mean.append(np.mean(np.square(np.array(chunks[chunk],dtype='int64')))) #takes the mean of all amplitudes in each one second chunk 
    dbs = []
    for chunk in range(len(mean)):
        dbs.append(20*math.log10(math.sqrt(mean[chunk])+0.000000001)) #converts all amplitudes to dBs, number added is to avoid log10 errors when volume is 0
    return(dbs)
audio1_dBs = get_dBs("audio1.wav")
audio2_dBs = get_dBs("audio2.wav")
audio1_dBs = np.around(audio1_dBs,4)
audio2_dBs = np.around(audio2_dBs,4)

#compare dBs for both files
loudest = [] #each index represents one second, number in index is what audio is louder
for i in range(max(len(audio1_dBs), len(audio2_dBs))):
    minimum = min(len(audio1_dBs), len(audio2_dBs)) #used to prevent checking dB array past the length
    shortest = 0
    if minimum == len(audio1_dBs):
        shortest = 1
    else:
        shortest = 2
    if i < minimum:
        compare = max(audio1_dBs[i],audio2_dBs[i])
        if audio1_dBs[i]==audio2_dBs[i]:
            loudest.append(loudest[i-1])
        else:
            if compare == audio1_dBs[i]:
                loudest.append(1)
            else:
                loudest.append(2)
    if i >=minimum:
        if shortest == 1:
            loudest.append(2)
        else:
            loudest.append(1)
os.remove("audio1.wav")
os.remove("audio2.wav")

#clip videos based on which audio is louder
segments = [] #timestamp ranges for when a video is louder
i = 0
while i < len(loudest):
    start_time = i
    end_time = start_time+1
    while i<len(loudest)-1 and loudest[i+1]==loudest[i]: #extends timestamp if the same audio is louder in next second
        end_time+=1
        i+=1
    i+=1
    segments.append([start_time, end_time])
current_video=loudest[0] ##set which video is currently the loudest
clips=[] ##list of video segments
for start_seconds, end_seconds in segments:
    if current_video==1:
        c = video1.subclip(start_seconds, end_seconds)
        clips.append(c)
        current_video=2
    else:
        c=video2.subclip(start_seconds, end_seconds)
        clips.append(c)
        current_video=1

#combine and render video
aclip1 = video1.audio
aclip2 = video2.audio
final_clip = mp.concatenate_videoclips(clips, method='compose')
compo = CompositeAudioClip([aclip1, aclip2])
final_clip.audio=compo
final_clip.write_videofile(final_name)
final_clip.close()
print('Video rendered to ' + str(path) + str(os.path.sep) + final_name)


