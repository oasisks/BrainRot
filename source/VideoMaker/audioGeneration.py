
from typing import List, Tuple
import torchaudio
import torch
import torchaudio.functional as F
from elevenlabs import generate, save
from unidecode import unidecode
import re

# might take a write function instead of dir and user
# func returns AudioClip
# discuss with hao
class Audio:
    def __init__(self, API: str, voice: str, dir: str, user: str) -> None:
        self._API = API
        self._voice = voice
        self._heading = dir + user

    # saves generated audio to file
    # returns name of file
    def generateAudio(self, text: str, filename: str) -> str:
        print("Generating audio")
        generated = generate(api_key=self._API, text=text, voice=self._voice, model="eleven_monolingual_v1")
        save(generated, self._heading + "_" + filename + '.mp3')
        return self._heading + "_" + filename + '.mp3'

    # forced alignment
    # copied from torch API
    # https://pytorch.org/audio/stable/tutorials/ctc_forced_alignment_api_tutorial.html
    # WIP
    def analyzeAudio(self, text: str, filename: str) -> Tuple[List[str], List[float]]:
        print("forced alignment")
        waveform, sample_rate = torchaudio.load(filename)
        final = changeWords(text)
        transcript = [word.lower() for word in final]
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


#issues with dollar and / still


# changes the text into a usable transcript
# takes text
# returns the transcript that can be visibly used
def changeWords(text: str) -> List[str]: 
    # attempts to convert characters to a-Z
    split = unidecode(text).split()

    # split numbers and words
    numsplit: List[str] = []
    isNum = False
    for word in split:
        curStr = ""
        for c in word:
            if not ((c.isnumeric() or c == "." or c == "$") ^ isNum):
                curStr += c
            else:
                numsplit.append(curStr) if curStr != "" else 1
                curStr = c
                isNum = (c.isnumeric() or c == "." or c == "$")
        numsplit.append(curStr)
        

    #deal with dollar
    dollars: List[str] = []
    units = ["thousand", "million", "billion", "trillion"]
    addDollar = False
    for i, word in enumerate(numsplit):
        #do nothing if no dollar
        if re.search("[$]", word) is None:
            #dollar with units
            if addDollar and (not i < len(split) - 1 or not split[i+1].lower() in units):
                dollars.append("dollars")
                addDollar = False
            dollars.append(word)
            continue

        # dollar with number
        if re.search("[0-9]", word):
            split = word.split("$")
            if len(split) == 2:
                if split[0] == '':
                    dollars.append(split[1])
                else:
                    dollars.append(split[0])
                addDollar = True
                continue

        # other dollar
        split = word.split("$")
        for i, new in enumerate(split):
            if new == '':
                dollars.append("dollar")
            elif i > 0 and split[i-1] != '':
                dollars.append("dollar")
                dollars.append(new)
            else:
                dollars.append(new)

    # trailing dollar
    if addDollar:
        dollars.append("dollar")
        
    #deal with symbols
    #does not account for math equations
    symbols = {"~": "tilde", "@": "at", "#": "hash", "%": "percent", "^": "circumflux", "&": "and", "*": "asterisk", "+": "plus", "=": "equal sign"}
    sym: List[str] = []
    for word in dollars:
        #split word for each symbol
        curWords = [word]
        for symbol, replace in symbols.items():
            newWords = []
            for cur in curWords:
                #if sole replacement
                if cur == symbol:
                    newWords.append(replace)
                    continue
                
                #add correct replacement
                split = cur.split(symbol)
                for i, new in enumerate(split):
                    if new == '':
                        newWords.append(replace)
                    elif i > 0 and split[i-1] != '':
                        newWords.append(replace)
                        newWords.append(new)
                    else:
                        newWords.append(new)
            curWords = newWords
        
        #add split words into list
        for new in curWords:
            sym.append(new)

    #deal with decimals
    #does not account for websites
    decimals: List[str] = []
    for word in sym:
        dec = word.split(".")
        for i, num in enumerate(dec):
            decimals.append(num)

            #point for numbers
            if i < len(dec) - 1:
                if num.isnumeric() and dec[i+1].isnumeric():
                    decimals.append("point")


    
    #deal with numbers
    #does not account for fractions

    #dictionaries for converting numbers to strings       
    teens = {"11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen", "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen", "19": "nineteen", "10": "ten"}
    tens = {"0": "zero", "2": "twenty", "3": "thirty", "4": "forty", "5": "fifty", "6": "sixty", "7": "seventy", "8": "eighty", "9": "ninety"}
    ones = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}
                    
    #converts 2 digit numbers to words
    def readTeen(numstr: str) -> List[str]:
        if len(numstr) == 1:
            return [ones[numstr]]
        if numstr[:1] == "1":
            return [teens[numstr]]
        if numstr[:1] == "0":
            return [ones[numstr[1]]]
        return [tens[numstr[0]], ones[numstr[1]]]
    
    #convers 3 digit numbers to words
    def readThree(numstr: str) -> List[str]:
        words: List[str] = []
        if len(numstr) != 3:
            return readTeen(numstr)
        if numstr[0] != "0":
            words.append(ones[numstr[0]])
            if numstr[1:3] == "00":
                words.append("hundred")
                return words
        for word in readTeen(numstr[1:]):
            words.append(word)
        return words

    numbers: List[str] = []
    for word in decimals:
        #not a number
        if not word.replace(",", "").isnumeric():
            numbers.append(word)
            continue

        #number without comma
        if word.isnumeric():
            numstr = word
            size = len(word)

            #read digit by digit
            if size > 4 or numstr[0] == "0":
                for c in numstr:
                    numbers.append(ones[c])

            #number like 2024
            elif size == 4 and int(numstr[0]) < 3:
                for num in readTeen(numstr[:2]):
                    numbers.append(num)
                for num in readTeen(numstr[2:]):
                    numbers.append(num)

            #number like 8094
            elif size == 4:
                numbers.append(ones[numstr[0]])
                numbers.append("thousand")
                for num in readThree(numstr[1:]):
                    numbers.append(num)
            else:
                for num in readThree(numstr):
                    numbers.append(num)
            continue

        #number with comma  
        #gather unit info
        numsplit = word.split(",")

        numsplit.reverse()
        numstr = []
        unitIndex = []

        size = 0
        for num in numsplit:
            if num == '':
                size = 0
                continue
            if len(num) > 3:
                size = -1
            numstr.append(num)
            unitIndex.append(size)
            size += 1
            if len(num) < 3:
                size = 0

        #correct order
        numstr.reverse()
        unitIndex.reverse()

        #get words
        for num, index in zip(numstr, unitIndex):
            #read every digit
            if index == -1:
                for c in num:
                    numbers.append(ones[c])
                continue

            for numWord in readThree(num):
                numbers.append(numWord)
            if index > 0 and index < 5:
                numbers.append(units[index - 1])
    
    #forces all other characters out
    #this might change based on performance
    return ["".join(filter(str.isalpha, word)) for word in numbers if len("".join(filter(str.isalpha, word)))]
