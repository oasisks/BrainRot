
from typing import Callable, Tuple, List
from moviepy.editor import *
from PostData import PostData


class MakePostVideo:
    def __init__(self, makeAudio: Callable[[str, str], str], analyzeAudio: Callable[[str, str], Tuple[List[str], List[float]]], screensize: Tuple[int, int]) -> None:
        self._makeAudio = makeAudio
        self._analyzeAudio = analyzeAudio
        self._screensize = screensize
    
    def makePostVideo(self, post: PostData) -> VideoClip:
        #creates the file ID
        fileID = post.source + "_" + post.id
        print(post.source)
        
        #Generates the title video
        titleVideo = self.textToVideo(post.title, fileID + "_title", "yellow")

        #Generates the interlude video
        interDuration = 1
        interlude = TextClip("a", color = 'transparent', size = self._screensize).set_duration(interDuration)

        #Generates the text video
        textVideo = self.textToVideo(post.text, fileID + "_text", "blue")

        #returns concatenated clips
        return concatenate_videoclips([titleVideo, textVideo], transition=interlude)
    
    #generates the video based on the text
    #audio file names are based on the id
    #text color is based on color
    def textToVideo(self, text: str, id: str, color: str) -> VideoClip:
        audio = self._makeAudio(text, id)
        words, breaks = self._analyzeAudio(text, audio)
        colors = [color if word is not None else 'transparent' for word in words]
        words = [word if word is not None else 'a' for word in words]
        clips = [TextClip(word, color = color,size = self._screensize, fontsize = int(self._screensize[0]/10)).set_duration(duration) 
                 for word, duration, color in zip(words, breaks, colors)]
        clip = concatenate_videoclips(clips)
        clip.audio = AudioFileClip(audio)
        return clip
