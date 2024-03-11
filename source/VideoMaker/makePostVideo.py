
from typing import Callable, Tuple, List
from moviepy.editor import *
import os
import sys

sys.path.append("../")
from PostData import PostData


class MakePostVideo:
    def __init__(self, makeAudio: Callable[[str], AudioClip], analyzeAudio: Callable[[AudioClip, str], List[int]], screensize: Tuple[int, int]) -> None:
        self._makeAudio = makeAudio
        self._analyzeAudio = analyzeAudio
        self._screensize = screensize
    
    def makePostVideo(self, post: PostData) -> Tuple[VideoClip, int]:
        titleAudio = self._makeAudio(post.title)
        textAudio = self._makeAudio(post.text)
        titleBreaks = self._analyzeAudio(titleAudio, post.title)
        textBreaks = self._analyzeAudio(textAudio, post.text)

        #change to a function that is more robust
        titleWords = post.title.split(" ")
        textWords = post.text.split(" ")

        titleClips = [TextClip(word, color = 'yellow', size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration in zip(titleWords, titleBreaks)]
        title = concatenate_videoclips(titleClips)
        title.audio = titleAudio
        

        interDuration = 1
        interlude = TextClip("a", color = 'transparent', size = self._screensize).set_duration(interDuration)

        textClips = [TextClip(word, color = 'orange',size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration in zip(textWords, textBreaks)]
        text = concatenate_videoclips(textClips)
        text.audio = textAudio

        complete = concatenate_videoclips([title, text], transition=interlude)
        return complete, titleAudio.duration + interDuration + textAudio.duration