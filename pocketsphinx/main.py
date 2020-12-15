#!/usr/bin/env python3

# from . import detector
import os
import argparse
from pocketsphinx import LiveSpeech, get_model_path
from detector import LiveSpeechDetector
from urllib.parse import urljoin, urlencode, quote

parser = argparse.ArgumentParser(description='Hey Rodney')
parser.add_argument('-k', '--keyphrase', dest='keyphrase', default='rodney',
                    help='keyphrase to detect')
parser.add_argument('-t', '--threshold', dest='threshold', default='1e-20',
                    type=float, help='KWS threshold (default: 1e-20)')
parser.add_argument('-i', '--input', dest='input', help='Input device for recording')
parser.add_argument('-o', '--output', dest='output', help='Output device for notification sounds')
parser.add_argument('-e', '--endpoint', dest='endpoint', help='Cloud side endpoint', required=True)
parser.add_argument('-u', '--user', dest='username', help='Username of the device in the cloud')
parser.add_argument('-p', '--password', dest='password', help='Password of the device in the cloud')
parser.add_argument('-d', '--device-id', dest='device', help='Device ID', required=True)
parser.add_argument('-m', '--model-id', dest='model', help='Model ID', default='ctron.hey.rodney:1.0.0')
parser.add_argument('-M', '--mime-type', dest='mime', help='The mime type used to send the audio snippet',
                    default='audio/wav')
parser.add_argument('--agc', dest='agc')
args = parser.parse_args()

force_alsa = os.getenv("FORCE_ALSA", "false")

endpoint_user = args.username
endpoint_password = args.password
if endpoint_user is not None and endpoint_password is not None:
    auth = (endpoint_user, endpoint_password)
else:
    auth = None

model_id = args.model
device_id = quote(args.device)

endpoint = args.endpoint
path = f"/publish/{device_id}/voice"
query = "?" + urlencode(dict(model_id=model_id))
url = urljoin(endpoint, path + query)

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
    'url': url,
    'auth': auth,
    'mime_type': args.mime,
    'force_alsa': force_alsa,
    'agc': args.agc,
}

speech = LiveSpeechDetector(**config)

for phrase in speech:
    print(phrase.segments(detailed=True))
