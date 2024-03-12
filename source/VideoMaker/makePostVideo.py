
from typing import Callable, Tuple, List
from moviepy.editor import *
import sys

sys.path.append("../")
from PostData import PostData


class MakePostVideo:
    def __init__(self, makeAudio: Callable[[str, str], AudioClip], analyzeAudio: Callable[[AudioClip, str], List[int]], screensize: Tuple[int, int]) -> None:
        self._makeAudio = makeAudio
        self._analyzeAudio = analyzeAudio
        self._screensize = screensize
    
    def makePostVideo(self, post: PostData) -> VideoClip:
        fileID = post.source + "_" + post.id
        #Generates the title video
        titleAudio = self._makeAudio(post.title, fileID + "_title")
        titleBreaks = self._analyzeAudio(titleAudio, post.title)
        titleWords = post.title.split(" ") #may need a more robust function
        titleClips = [TextClip(word, color = 'yellow', size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration in zip(titleWords, titleBreaks)]
        title = concatenate_videoclips(titleClips)
        title.audio = titleAudio

        #Generates the interlude video
        interDuration = 1
        interlude = TextClip("a", color = 'transparent', size = self._screensize).set_duration(interDuration)

        #Generates the text video
        textAudio = self._makeAudio(post.text, fileID + "_text")
        textBreaks = self._analyzeAudio(textAudio, post.text)
        textWords = post.text.split(" ")
        textClips = [TextClip(word, color = 'orange',size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration in zip(textWords, textBreaks)]
        text = concatenate_videoclips(textClips)
        text.audio = textAudio

        #returns concatenated clips
        return concatenate_videoclips([title, text], transition=interlude)