from typing import List
from PostData import PostData
from VideoMaker.makePostVideo import MakePostVideo
from VideoMaker.videoMaker import VideoMaker
from VideoMaker.audioGeneration import Audio

from moviepy.editor import *

from dotenv import load_dotenv
import os


#length = 1080
#screensize = (length, int(16 * length / 9))

height = 1080
length = int(round(height * 9 / 16, -1))
screensize = (length, height)

VIDEO_DIR = "final videos/"
USERNAME = "hello"
BREAK = 0.5

def dummyAudio(help: str):
    return b'', BREAK * len(help.split(" "))

def dummyAnal(audio: bytes, help: str):
    return [BREAK] * len(help.split(" "))

def dummyPost(title, text, id):
    return PostData(title = title, text=text, id=id)

def dummyBrainrotMaker(duration):
    return VideoFileClip("brainrot videos/1_min_vid.mp4", audio=False).resize(height = screensize[1]).set_position("center").set_duration(duration)
    # return ImageClip("brainrot videos/winton.png", duration=duration)

def dummyCompiler(post, brainrot):
    return CompositeVideoClip([brainrot, post], size=screensize)

if __name__ == '__main__':
    #post = PostData(title = "Reddit Post Title", text = "today i learned that i could write a bunch of text and have it show on a video")
    #postVideo, duration = postMaker.makePostVideo(post)
    #postVideo.write_videofile(VIDEO_DIR + "complete test.mp4", fps = 8)
    
    load_dotenv()
    audioMaker = Audio(os.getenv("ELEVEN_API"), "21m00Tcm4TlvDq8ikWAM")
    postMaker = MakePostVideo(audioMaker.generateAudio, audioMaker.analyzeAudio, screensize)
    videoMaker = VideoMaker(dummyPost, postMaker.makePostVideo, dummyBrainrotMaker, dummyCompiler)
    try:
        clip, id = videoMaker.makeVideo("Reddit Post Title", "hello there", "testing")
        clip.write_videofile(VIDEO_DIR + USERNAME + "_" + id + ".mp4", fps = 60)
    except Exception as E: 
        print(E)

