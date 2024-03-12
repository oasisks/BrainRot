from typing import Callable, Tuple
from moviepy.editor import *
from PostData import PostData


#arguments: any args
#return: PostData
getPostCall = Callable[..., PostData]

#arguments: PostData
#return: video, duration (s)
makePostVideoCall = Callable[[PostData], VideoClip]

#arguments: duration (s)
#return: video
makeBrainrotVideoCall = Callable[[], VideoClip]

#arguments: postVideo, brainrotVideo
#return: compiled video
compileVideoCall = Callable[[VideoClip, VideoClip], VideoClip]

class VideoMaker:
    def __init__(self, getPost: getPostCall, makePostVideo: makePostVideoCall, makeBrainrotVideo: makeBrainrotVideoCall, compileVideo: compileVideoCall) -> None:
        self._getPost = getPost
        self._makePostVideo = makePostVideo
        self._makeBrainrotVideo = makeBrainrotVideo
        self._compileVideo = compileVideo

    def makeVideo(self, *args) -> Tuple[VideoClip, str]:
        post = self._getPost(*args)
        postVideo = self._makePostVideo(post)
        brainrotVideo = self._makeBrainrotVideo()
        return self._compileVideo(postVideo, brainrotVideo), post.id

