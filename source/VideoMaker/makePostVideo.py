
from typing import Callable, Tuple, List
from moviepy.editor import *
import sys

sys.path.append("../")
from PostData import PostData


class MakePostVideo:
    def __init__(self, makeAudio: Callable[[str, str], str], analyzeAudio: Callable[[str, str], Tuple[List[str], List[float]]], screensize: Tuple[int, int]) -> None:
        self._makeAudio = makeAudio
        self._analyzeAudio = analyzeAudio
        self._screensize = screensize
    
    def makePostVideo(self, post: PostData) -> VideoClip:
        fileID = post.source + "_" + post.id
        #Generates the title video
        titleAudio = self._makeAudio(post.title, fileID + "_title")
        titleWords, titleBreaks = self._analyzeAudio(post.title, titleAudio)
        titleColors = ['yellow' if word is not None else 'transparent' for word in titleWords]
        titleWords = [word if word is not None else 'a' for word in titleWords]
        titleClips = [TextClip(word, color = color, size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration, color in zip(titleWords, titleBreaks, titleColors)]
        title = concatenate_videoclips(titleClips)
        title.audio = AudioFileClip(titleAudio)

        #Generates the interlude video
        interDuration = 1
        interlude = TextClip("a", color = 'transparent', size = self._screensize).set_duration(interDuration)

        #Generates the text video
        textAudio = self._makeAudio(post.text, fileID + "_text")
        textWords, textBreaks = self._analyzeAudio(post.text, textAudio)
        textColors = ['orange' if word is not None else 'transparent' for word in textWords]
        textWords = [word if word is not None else 'a' for word in textWords]
        textClips = [TextClip(word, color = color,size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration, color in zip(textWords, textBreaks, textColors)]
        text = concatenate_videoclips(textClips)
        text.audio = AudioFileClip(textAudio)

        #returns concatenated clips
        return concatenate_videoclips([title, text], transition=interlude)