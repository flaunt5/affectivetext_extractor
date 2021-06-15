import os
import sys
import csv
import random
import copy
from geotext import GeoText
from nltk.tag import pos_tag
import xml.etree.ElementTree as ET

text_choice = 'trial'
filename = "chosen_utterances.csv"

if len(sys.argv) > 1:
    if sys.argv[1] != 'test' and sys.argv[1] != 'trial':
        exit(1)
  
    if len(sys.argv) > 2:
        filename = sys.argv[2] + ".csv"
    
    text_choice = sys.argv[1]

CWD = os.getcwd()
TARGETDIR = os.path.join(CWD, 'AffectiveText/AffectiveText.%s' % text_choice)
text = os.path.join(TARGETDIR, 'affectivetext_%s.xml' % text_choice)
emotions = os.path.join(TARGETDIR, 'affectivetext_%s.emotions.gold' % text_choice)
valence = os.path.join(TARGETDIR, 'affectivetext_%s.valence.gold' % text_choice)

def GetEmotion(row):
    slice = copy.deepcopy(row)
    slice.pop("text")
    slice.pop("surprise")
    slice.pop("valence")

    if all(v < 10 for v in slice.values()):
        return 'neutral'
    
    max_val = max(slice.values())
    max_key = [k for k, v in slice.items() if v == max_val]
    if len(max_key) == 1 and max_val > 30:
        return max_key[0]
    else:
        return False

def GetRandomSample(candidates):
    return random.sample(candidates, 12)

def WriteToCsv(candidates, name):
    for can in candidates:
        res = list(can.values())
        res = [name] + res
        writer.writerow(res)

file = open(os.path.join(CWD, filename), "w")
writer = csv.writer(file, delimiter = ';', quotechar = "\"", quoting=csv.QUOTE_MINIMAL)
writer.writerow(["emotion", "text", "anger", "disgust", "fear", "joy", "sadness", "surprise", "valence"])

values = {}
text_tree = ET.parse(text)
for child in text_tree.getroot():
    id = int(child.attrib["id"])
    content = child.text
    values[id] = {"text": content}

emotions_file = open(emotions, "r")
emotions_lines = emotions_file.readlines()
emotions_file.close()

for line in emotions_lines:
    split = line.split()
    dict = values[int(split[0])]
    dict.update({"anger": int(split[1]), "disgust": int(split[2]), "fear": int(split[3]),
    "joy": int(split[4]), "sadness": int(split[5]), "surprise": int(split[6])} )
    values[int(split[0])] = dict

valence_file = open(valence, "r")
valence_lines = valence_file.readlines()
valence_file.close()

for line in valence_lines:
    split = line.split()
    values[int(split[0])]["valence"] = int(split[1])

candidates = {"anger": list(), "disgust": list(), "fear": list(), "joy": list(), "sadness": list(), "neutral": list()}

for val in values:
    slice = values[val]
    text = slice['text']
    em = GetEmotion(slice)
    print(slice)
    if em is not False:
        candidates[em].append(slice)

joy_candidates_two = list()
for joy in candidates['joy']:
    if joy['joy'] > 50:
        joy_candidates_two.append(joy)

candidates['joy'] = joy_candidates_two

sadness_candidates_two = list()
for sadness in candidates['sadness']:
    if sadness['sadness'] > 50:
        sadness_candidates_two.append(sadness)

candidates['sadness'] = sadness_candidates_two

neutral_candidates_two = list()
for neutral in candidates['neutral']:
    if neutral['anger'] < 5 and neutral['disgust'] < 5 and neutral['fear'] < 5 and neutral['joy'] < 5 and neutral['sadness'] < 5:
        neutral_candidates_two.append(neutral)

candidates['neutral'] = neutral_candidates_two

for can in candidates:
    candidates[can] = GetRandomSample(candidates[can])
    for line in candidates[can]:
        data_to_write = [can] + list(line.values())
        writer.writerow(data_to_write)
