from typing import Callable, Tuple
from moviepy.editor import *
import sys

sys.path.append("../")
from PostData import PostData


#arguments: any args
#return: PostData
getPostCall = Callable[..., PostData]

#arguments: PostData
#return: video (in bytes), duration (in ms)
makePostVideoCall = Callable[[PostData], Tuple[VideoClip, int]]

#arguments: duration (in ms)
#return: video (in bytes)
makeBrainrotVideoCall = Callable[[int], VideoClip]

#arguments: postVideo (in bytes), brainrotVideo (in bytes)
#return: compiled video (in bytes)
compileVideoCall = Callable[[VideoClip, VideoClip], VideoClip]

class VideoMaker:
    def __init__(self, getPost: getPostCall, makePostVideo: makePostVideoCall, makeBrainrotVideo: makeBrainrotVideoCall, compileVideo: compileVideoCall) -> None:
        self._getPost = getPost
        self._makePostVideo = makePostVideo
        self._makeBrainrotVideo = makeBrainrotVideo
        self._compileVideo = compileVideo

    def makeVideo(self, *args) -> Tuple[VideoClip, str]:
        post = self._getPost(*args)
        postVideo, duration = self._makePostVideo(post)
        brainrotVideo = self._makeBrainrotVideo(duration)
        return self._compileVideo(postVideo, brainrotVideo), post.id

