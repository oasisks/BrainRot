from __future__ import annotations
from typing import Callable, Tuple, List
from dataclasses import dataclass
import sys

sys.path.append("../")
from PostData import PostData, Reply


#defines the data stored in the post
@dataclass
class PostData:
    user: str
    title: str
    text: str
    images: List[bytes]
    replies: List[Reply]


@dataclass
class Reply:
    user: str
    parent: Reply
    child: List[Reply]
    content: str
    images: List[bytes]

#arguments: none (might modify this)
#return: PostData
getPostCall = Callable[[], PostData]

#arguments: PostData
#return: video (in bytes), duration (in ms)
makePostVideoCall = Callable[[PostData], Tuple[bytes, int]]

#arguments: duration (in ms)
#return: video (in bytes)
makeBrainrotVideoCall = Callable[[int], bytes]

#arguments: postVideo (in bytes), brainrotVideo (in bytes)
#return: compiled video (in bytes)
compileVideoCall = Callable[[bytes, bytes], bytes]

class VideoMaker:
    def __init__(self, getPost: getPostCall, makePostVideo: makePostVideoCall, makeBrainrotVideo: makeBrainrotVideoCall, compileVideo: compileVideoCall) -> None:
        self.getPost = getPost
        self.makePostVideo = makePostVideo
        self.makeBrainrotVideo = makeBrainrotVideo
        self.compileVideo = compileVideo

    def makeVideo(self) -> bytes:
        post = self.getPost()
        postVideo, duration = self.makePostVideo(post)
        brainrotVideo = self.makeBrainrotVideo(duration)
        return self.compileVideo(postVideo, brainrotVideo)

