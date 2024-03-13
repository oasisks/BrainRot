from PostData import PostData
from VideoMaker.makePostVideo import MakePostVideo
from VideoMaker.videoMaker import VideoMaker
from VideoMaker.audioGeneration import Audio
from Posts.redditPosts import RedditPost
from DataPool.DataPool import DataPool

from moviepy.editor import *
from bson import ObjectId
from dotenv import load_dotenv
import os

#determines screensize
height = 1080
length = int(round(height * 9 / 16, -1))
screensize = (1080, 1920)

#constants that can be changed
VIDEO_DIR = "final_videos/"
USERNAME = "hello"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


#returns a PostData with given info
def dummyPost(title, text, id):
    return PostData(title = title, text=text, id=id)

#returns the resized and centered brainrot video
def dummyBrainrotMaker():
    return VideoFileClip("brainrot_videos/new_format_shorts.mp4", audio=False).resize(height = screensize[1]).set_position("center")

#placed the brainrot as background
def dummyCompiler(post: VideoClip, brainrot):
    return CompositeVideoClip([brainrot, post], size=screensize).set_duration(post.duration)

#main
if __name__ == '__main__':
    #create the appropriate makers
    load_dotenv()
    post = RedditPost()
    dataPool = DataPool()

    audio = Audio(os.getenv("ELEVEN_API_KEY"), VOICE_ID, "temp_audio/", USERNAME)
    postMaker = MakePostVideo(audio.generateAudio, audio.analyzeAudio, screensize)
    videoMaker = VideoMaker(post.getPost, postMaker.makePostVideo, dummyBrainrotMaker, dummyCompiler)

    #try to make the video
    try:
        subreddit = "pettyrevenge"
        title = "Testing Timing"
        message = "$200 gift éóñ !! card"
        clip, id = videoMaker.makeVideo(subreddit, str(dataPool.getMostRecentEntry().__id))
        clip.write_videofile(VIDEO_DIR + USERNAME + "_" + id + ".mp4", fps = 60)
    except Exception as E: 
        raise E

