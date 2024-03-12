from PostData import PostData
from VideoMaker.makePostVideo import MakePostVideo
from VideoMaker.videoMaker import VideoMaker
from VideoMaker.audioGeneration import Audio

from moviepy.editor import *

from dotenv import load_dotenv
import os

#determines screensize
height = 1080
length = int(round(height * 9 / 16, -1))
screensize = (length, height)

#constants that can be changed
VIDEO_DIR = "final videos/"
USERNAME = "hello"
BREAK = 0.5
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


#returns a dummy audiofile
#outdated
def dummyAudio(help: str):
    return VideoFileClip("brainrot videos/1_min_vid.mp4").set_duration(BREAK * len(help.split(" "))).audio

#returns breaks every BREAK seconds
def dummyAnal(help: str, filename: str):
    return [BREAK] * len(help.split(" "))

#returns a PostData with given info
def dummyPost(title, text, id):
    return PostData(title = title, text=text, id=id)

#returns the resized and centered brainrot video
def dummyBrainrotMaker():
    return VideoFileClip("brainrot videos/1_min_vid.mp4", audio=False).resize(height = screensize[1]).set_position("center")

#placed the brainrot as background
def dummyCompiler(post: VideoClip, brainrot):
    return CompositeVideoClip([brainrot, post], size=screensize).set_duration(post.duration)

#main
if __name__ == '__main__':
    #create the appropriate makers
    load_dotenv()
    audio = Audio(os.getenv("ELEVEN_API_KEY"), VOICE_ID, "temp_audio/", USERNAME)
    postMaker = MakePostVideo(audio.generateAudio, audio.analyzeAudio, screensize)
    videoMaker = VideoMaker(dummyPost, postMaker.makePostVideo, dummyBrainrotMaker, dummyCompiler)

    #try to make the videow
    try:
        title = "Testing Timing"
        message = "This is a test for timing the text to speech. It should line up well."
        clip, id = videoMaker.makeVideo(title, message, "testing")
        clip.write_videofile(VIDEO_DIR + USERNAME + "_" + id + ".mp4", fps = 60)
    except Exception as E: 
        raise E

