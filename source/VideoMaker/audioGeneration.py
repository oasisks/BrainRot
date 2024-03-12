
from typing import List, Tuple
import torchaudio
import torch
import torchaudio.functional as F
from elevenlabs import generate, save
from unidecode import unidecode
import re

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
        generated = generate(api_key=self._API, text=text, voice=self._voice, model="eleven_monolingual_v1")
        save(generated, self._heading + "_" + filename + '.mp3')
        return self._heading + "_" + filename + '.mp3'
    

    #forced alignment
    #copied from torch API 
    #https://pytorch.org/audio/stable/tutorials/ctc_forced_alignment_api_tutorial.html
    #WIP
    def analyzeAudio(self, text: str, filename: str) -> Tuple[List[str], List[float]]:
        waveform, sample_rate = torchaudio.load(filename)
        transcript = changeWords(text)
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
        

        num_frames = emission.size(1)
        ratio = waveform.size(1) / num_frames

        starts = [int(ratio * spans[0].start) / sample_rate for spans in word_spans]
        ends = [int(ratio * spans[-1].end) / sample_rate for spans in word_spans]

        times = []
        words = []
        lastend = 0

        for start, end, word in zip(starts, ends, transcript):
            words.append(None)
            times.append(start - lastend)

            words.append(word)
            duration = max(end-start, 0.1)
            times.append(duration)

            lastend = start + duration

        return words, times


teens = {11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 10: "ten"}
tens = {0: "zero", 2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}
ones = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}


#scuffed word changer
#need to figure out how to reserve word length
#or we just use these words
def changeWords(text: str): 
    #get rid of unwanted letters
    text = unidecode(text)
    text = text.lower()

    #deal with money
    split = text.split()
    dollars: List[str] = []

    addDollar = False
    units = ["thousand", "million", "billion", "trillion"]
    for i, word in enumerate(split):
        #check for $
        if re.search("[$]", word) is not None:
            if re.search("[0-9]", word):
                dollars.append(word[1:])
                if i < len(split) - 1 and split[i] in units:
                    addDollar = True
                else:
                    dollars.append("dollars")
            elif len(word.replace("$", "")):
                dollars.append(word.replace("$", ""))
        else:
            dollars.append(word)
            if addDollar:
                dollars.append("dollars")
                addDollar = False

    #deal with percent
    percents: List[str] = []
    for word in dollars:
        percents.append(word.replace("%", "")) if len(word.replace("%", "")) else 1
        if re.search("%", word):
            percents.append("percent")


    #deal with decimals
    decimals: List[str] = []
    for word in percents:
        dec = word.split(".")
        for i, num in enumerate(dec):
            decimals.append(num)
            if i < len(dec) - 1:
                if num.isnumeric() and dec[i+1].isnumeric():
                    decimals.append("point")
                else:
                    decimals.append("dot")

    
    #deal with numbers
    #breaks with leading 0
    numbers: List[str] = []
    for word in decimals:
        numstr = word.replace(",", "")     
        if numstr.isnumeric():
            num = int(numstr)
            size = len(numstr)
            if size % 3 == 1:
                first = int(numstr[:1])
                if size == 1:
                    numbers.append(ones[int(numstr)])
                    continue
                if first == 1:
                    numbers.append(teens[int(numstr[:2])])
                else:
                    numbers.append(tens[first])
                    numbers.append(ones[int(numstr[1:2])])
                
                if size > 3 and size < 15:
                    numbers.append(units[int(size/3) - 1])


                second = int(numstr[2:3])
                if int(numstr[2:4]) == 0:
                    pass
                
                elif second == 1:
                    numbers.append(teens[int(numstr[2:4])])
                else:
                    numbers.append(tens[second])
                    numbers.append(ones[int(numstr[3:4])])
            if size % 3 == 2:
                first = int(numstr[:1])
                if first == 1:
                    numbers.append(teens[int(numstr[:2])])
                else:
                    numbers.append(tens[first])
                    numbers.append(ones[int(numstr[1:2])])
                
                if size > 3 and size < 15:
                    numbers.append(units[int(size/3) - 1])
            
            if size % 3 == 0:
                numbers.append(ones[int(numstr[:1])])
                if int(numstr[:1]) != 0:
                    numbers.append("hundred")

                first = int(numstr[1:2])
                if int(numstr[1:3]) == 0 and int(numstr[:1]) != 0:
                    pass
                elif first == 1:
                    numbers.append(teens[int(numstr[1:3])])
                else:
                    if int(numstr[1:2]) != 0:
                        numbers.append(tens[first])
                    numbers.append(ones[int(numstr[2:3])])
                
                if size > 3 and size < 15:
                    numbers.append(units[int(size/3) - 1])
        else:
            numbers.append(word)
                

    returner = ["".join(filter(str.isalpha, word)) for word in numbers if len("".join(filter(str.isalpha, word)))]

    return returner
    