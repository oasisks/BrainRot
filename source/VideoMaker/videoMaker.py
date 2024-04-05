from typing import Callable, List, Tuple
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
    def __init__(self, getPost: getPostCall, makePostVideo: makePostVideoCall, makeBrainrotVideo: makeBrainrotVideoCall, compileVideo: compileVideoCall, video_dir: str, username: str) -> None:
        self._getPost = getPost
        self._makePostVideo = makePostVideo
        self._makeBrainrotVideo = makeBrainrotVideo
        self._compileVideo = compileVideo
        self._video_dir = video_dir
        self._username = username

    def makeVideo(self, *args) -> List[str]:
        post = self._getPost(*args)
        post.text = textfilter(post.text)
        post.title = textfilter(post.title)

        parts = splitpost(post)
        ids: List[str] = []
        for part in parts:
            print("making video number", part)
            postVideo = self._makePostVideo(part)
            brainrotVideo = self._makeBrainrotVideo()
            clip = self._compileVideo(postVideo, brainrotVideo)
            clip.write_videofile(self._video_dir + self._username + "_" + part.id + ".mp4", fps = 60)
            ids.append(part.id)
        return ids
    
def textfilter(text: str) -> str:
    return text

def splitpost(post: PostData) -> List[PostData]:
    #word tolerance
    min = 5
    max = 100
    lowtol = 2
    hightol = 200
    if len(post.text.split()) < max:
        return [post]
    
    #split by par
    blocks, lowest, highest = splitter(post.text, min = min, max = max)

    #if fail try split by sentence
    if lowest < lowtol or highest > hightol:
        newblocks, newlowest, newhighest = splitter(post.text, token=". ", min = min, max = max)
        if newlowest >= lowest and newhighest <= highest:
            blocks = newblocks
    
    #make post per thing
    posts = [PostData()] * len(blocks)
    for index, block in enumerate(blocks):
        posts[index] = PostData(user = post.user, title = "Part " + str(index + 1) + " of " + post.title, text = block, id = post.id + "_part_" + str(index + 1), source=post.source, images=post.images, replies=post.replies)

    return posts



def splitter(text: str, token: str = "\n", min: int = 50, max: int = 200) -> Tuple[List[str], int, int]:
    blocks = []
    newblocks = text.split(sep = token)
    i = 0
    while len(blocks) != len(newblocks):
        i += 1
        prevtiny = False
        previndex = -1
        blocks = newblocks
        newblocks = []
        for index, block in enumerate(blocks):
            #first block
            if index == 0:
                newblocks.append(block)
                previndex += 1
                prevtiny = len(block.split()) < min
                continue

            # a small block
            if len(block.split()) < min:
                #addable to previous block
                if len((block + newblocks[previndex]).split()) < 200:
                    newblocks[previndex] = newblocks[previndex] + " " + block
                    prevtiny = len(newblocks[previndex]) < min

                #make new block
                else:
                    newblocks.append(block)
                    prevtiny = True
                    previndex += 1
            else:
                if prevtiny:
                    if len((block + newblocks[previndex]).split()) < 200:
                        newblocks[previndex] = newblocks[previndex] + " " + block
                        prevtiny = len(newblocks[previndex]) < min
                    else:
                        newblocks.append(block)
                        prevtiny = False
                        previndex += 1
                else:
                    newblocks.append(block)
                    prevtiny = False
                    previndex += 1
    
    
    minlength = max
    maxlength = 0
    blocks = newblocks
    newblocks = []
    index = -1
    for block in blocks:
        if index != -1 and len(newblocks[index] + block) < max:
            newblocks[index] = newblocks[index] + " " + block
        else:
            newblocks.append(block)
            index += 1 

    for block in newblocks:
        minlength = low(minlength, len(block))
        maxlength = high(maxlength, len(block))
    return newblocks, minlength, maxlength

def low(num1, num2):
    return min(num1, num2)

def high(num1, num2):
    return max(num1, num2)

