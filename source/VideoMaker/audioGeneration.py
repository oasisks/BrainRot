
from typing import List
import torchaudio
import torch
import torchaudio.functional as F
from elevenlabs import generate, save
import os

CHUNK_SIZE = 1024
model_path = "vosk-model-small-en-us-0.15"


#might take a write function instead of dir and user
#func returns AudioClip
#discuss with hao
class Audio:
    def __init__(self, API: str, voice: str, dir: str, user: str) -> None:
        self._API = API
        self._voice = voice
        self._heading = dir + user

    #saves generated audio to file
    #returns name of file
    def generateAudio(self, text: str, filename: str) -> str:
        generated = generate(api_key=self._API, text=text, voice=self._voice, model="eleven_multilingual_v2")
        save(generated, self._heading + filename + '.mp3')
        return self._heading + filename + '.mp3'
    

    #forced alignment
    #WIP
    def analyzeAudio(self, text: str, filename: str) -> List[float]:
        waveform, _ = torchaudio.load(filename)
        transcript = text.split()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        bundle = torchaudio.pipelines.MMS_FA
        model = bundle.get_model(with_star=False).to(device)
        with torch.inference_mode():
            emission, _ = model(waveform.to(device))

        DICTIONARY = bundle.get_dict(star=None)
        
        tokenized_transcript = [DICTIONARY[c] for word in transcript for c in word.lower()]

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

        num_frames = emission.size(1)
        ratio = waveform.size(1) / num_frames

        starts = [int(ratio * spans[0].start) / bundle.sample_rate for spans in word_spans]
        ends = [int(ratio * spans[-1].end) / bundle.sample_rate for spans in word_spans]

        times = [end - start for start, end in zip(starts, ends)]
        print(times)
        return times
