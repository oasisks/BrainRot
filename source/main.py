from PostData import PostData
from VideoMaker.makePostVideo import MakePostVideo
from VideoMaker.videoMaker import VideoMaker
from VideoMaker.audioGeneration import Audio
from Posts.redditPosts import RedditPost
from DataPool.DataPool import DataPool

from moviepy.editor import *
from dotenv import load_dotenv
import os

#determines screensize
height = 1080
length = int(round(height * 9 / 16, -1))
screensize = (1080, 1920)

#constants that can be changed
VIDEO_DIR = "final_videos/"
USERNAME = "hello"
VOICE_ID = "Nicole"


#returns a PostData with given info
def dummyPost(title, text, id):
    return PostData(title = title, text=text, id=id)

#returns the resized and centered brainrot video
def dummyBrainrotMaker():
    return VideoFileClip("brainrot_videos/0404 (2)(1).mp4", audio=False).resize(height = screensize[1]).set_position("center")

#placed the brainrot as background
def dummyCompiler(post: VideoClip, brainrot):
    endbuffer = 0.3
    dur = post.duration
    target = min(brainrot.duration, 60) - endbuffer
    print("duration: ", dur)
    if dur > 90:
        raise Exception("too long")

    if dur > target:
        print("speedup: ", dur / target)
        post = post.fx(vfx.speedx, dur / target)
        dur = target
    
    return CompositeVideoClip([brainrot, post], size=screensize).set_duration(dur + endbuffer)

#main
if __name__ == '__main__':
    #test variables
    subreddit = "pettyrevenge"
    title = "Testing Timing"
    message = "Help. \nI really need help. \nTest. \nTest this fucker please I beg of you. \nStrain it to its fullest extent. \nBoy do I have the test for you. You've been a good boy Varun. I hope you like this voice Varun."
    collection = "Reddit"


    #title = "Am I wrong for telling my husband the only way I will agree to a paternity test is if he schedules it"
    #message = "I (30f) have been married to my husband (36m) for 5 years. I am currently 4 months pregnant. This wasn't a surprise pregnancy we planned it and actively tried to get pregnant. So, it came out of left field when a few weeks ago, my husband told me he wanted a paternity test. I asked him how he or why he thinks I am cheating on him. He said he didn't think I was. But that makes absolutely no sense. I asked him to explain how this child could not be his if he is the only person I slept with and I didn't cheat on him. He had no answer for that. I was a mess for a few days afterward. Once I calmed down, I told him that if he wanted to get the test, then he could schedule it and tell me where and when to be there. He asked me if I could be the one to make the appointment."

    #get necessary information
    load_dotenv()
    dataPool = DataPool()
    post = RedditPost(dataPool)
    audio = Audio(os.getenv("ELEVEN_API_KEY"), VOICE_ID, "temp_audio/", USERNAME)

    #create the appropriate makers
    postMaker = MakePostVideo(audio.generateAudio, audio.analyzeAudio, screensize)
    #videoMaker = VideoMaker(post.getPost, postMaker.makePostVideo, dummyBrainrotMaker, dummyCompiler) #this is for actually getting the post
    videoMaker = VideoMaker(dummyPost, postMaker.makePostVideo, dummyBrainrotMaker, dummyCompiler) #this is for manually inputting text
    #try to make the video
    try:
        #videos = videoMaker.makeVideo("", None, "hot", 10, "https://www.reddit.com/r/amiwrong/comments/1boff73/my_girlfriend_cheated_on_me_with_my_brother_and/")
        videos = videoMaker.makeVideo(title, message, "parttest")
        for clip, id in videos:
            clip.write_videofile(VIDEO_DIR + USERNAME + "_" + id + ".mp4", fps = 60)
            dataPool.add_video_to_collection(collection_name="testing", file_dir=VIDEO_DIR + USERNAME + "_" + id + ".mp4")
    except Exception as E: 
        raise E
    

