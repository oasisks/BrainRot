from typing import Callable, Tuple


class MakePostVideo:
    def __init__(self, makeAudio: Callable[[str], Tuple[bytes, int]]) -> None:
        self.makeAudio = makeAudio
    
    def makePostVideo() -> tuple[bytes, int]:
        return