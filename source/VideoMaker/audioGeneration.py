import requests
from moviepy.editor import *
import torchaudio
import torch
import torchaudio.functional as F
import wave

CHUNK_SIZE = 1024
model_path = "vosk-model-small-en-us-0.15"


#might take a write function instead of dir and user
#func returns AudioClip
class Audio:
    def __init__(self, API: str, voice: str, dir: str, user: str) -> None:
        self._API = API
        self._voice = voice
        self._dir = dir
        self._user = user

    #copied from 11labs
    def generateAudio(self, text: str, id: str) -> AudioClip:
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + self._voice

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self._API
        }

        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        with open(self._dir + self._user + id + '.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        return AudioFileClip(self._dir + self._user + id + '.mp3')
    

    #forced alignment
    #WIP
    def analyzeAudio(self, audio: AudioClip, text: str, id: str):
        waveform, _ = torchaudio.load()
        transcript = text.split()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        bundle = torchaudio.pipelines.MMS_FA
        model = bundle.get_model(with_star=False).to(device)
        with torch.inference_mode():
            emission, _ = model(waveform.to(device))


        LABELS = bundle.get_labels(star=None)
        DICTIONARY = bundle.get_dict(star=None)

        tokenized_transcript = [DICTIONARY[c] for word in transcript for c in word]

        def align(emission, tokens):
            targets = torch.tensor([tokens], dtype=torch.int32, device=device)
            alignments, scores = F.forced_align(emission, targets, blank=0)

            alignments, scores = alignments[0], scores[0]  # remove batch dimension for simplicity
            scores = scores.exp()  # convert back to probability
            return alignments, scores


        aligned_tokens, alignment_scores = align(emission, tokenized_transcript)
        token_spans = F.merge_tokens(aligned_tokens, alignment_scores)

        def unflatten(list_, lengths):
            assert len(list_) == sum(lengths)
            i = 0
            ret = []
            for l in lengths:
                ret.append(list_[i : i + l])
                i += l
            return ret


        word_spans = unflatten(token_spans, [len(word) for word in transcript])
        print(text)
        print(word_spans)
        return
