#!/usr/bin/env python3

#from . import detector
import os
import argparse
from pocketsphinx import LiveSpeech, get_model_path
from detector import LiveSpeechDetector

parser = argparse.ArgumentParser(description='Hey Rodney')
parser.add_argument('-k', '--keyphrase', dest='keyphrase', default='rodney',
                    help='keyphrase to detect')
parser.add_argument('-t', '--threshold', dest='threshold', default='1e-20',
                    type=float, help='KWS threshold (default: 1e-20)')
parser.add_argument('-i', '--input', dest='input', help='Input device for recording')
parser.add_argument('-o', '--output', dest='output', help='Output device for notification sounds')
args = parser.parse_args()


model_path = get_model_path()

config = {
    'lm': False,
    'hmm': os.path.join(model_path, 'en-us'),
    'dic': os.path.join(model_path, 'cmudict-en-us.dict'),
    'keyphrase': args.keyphrase,
    'kws_threshold': args.threshold,
    'verbose': True,
    'audio_device': args.input,
    'sound_start': "/hey-rodney/start.wav",
    'sound_end': "/hey-rodney/end.wav",
}


#speech = LiveSpeech(
#    **config
#)

speech = LiveSpeechDetector(
    **config
)

for phrase in speech:
    print(phrase.segments(detailed=True))

