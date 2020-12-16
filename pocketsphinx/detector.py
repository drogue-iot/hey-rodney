# Copyright (c) 1999-2016 Carnegie Mellon University. All rights
# reserved.
# Copyright (c) 2020 Red Hat Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# This work was supported in part by funding from the Defense Advanced
# Research Projects Agency and the National Science Foundation of the
# United States of America, and the CMU Sphinx Speech Consortium.
#
# THIS SOFTWARE IS PROVIDED BY CARNEGIE MELLON UNIVERSITY ``AS IS'' AND
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CARNEGIE MELLON UNIVERSITY
# NOR ITS EMPLOYEES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import io
import sys
import signal
from contextlib import contextmanager
from sphinxbase import *
from pocketsphinx import *
import time
import wave
import pyogg

import requests

DefaultConfig = Decoder.default_config


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_model_path():
    """ Return path to the model. """
    return os.path.join(os.path.dirname(__file__), 'model')


def get_data_path():
    """ Return path to the data. """
    return os.path.join(os.path.dirname(__file__), 'data')


class BasicDetector(Decoder):

    def __init__(self, **kwargs):
        model_path = get_model_path()
        data_path = get_data_path()

        self.goforward = os.path.join(data_path, 'goforward.raw')

        if kwargs.get('dic') is not None and kwargs.get('dict') is None:
            kwargs['dict'] = kwargs.pop('dic')

        if kwargs.get('hmm') is None:
            kwargs['hmm'] = os.path.join(model_path, 'en-us')

        if kwargs.get('lm') is None:
            kwargs['lm'] = os.path.join(model_path, 'en-us.lm.bin')

        if kwargs.get('dict') is None:
            kwargs['dict'] = os.path.join(model_path, 'cmudict-en-us.dict')

        if kwargs.pop('verbose', False) is False:
            if sys.platform.startswith('win'):
                kwargs['logfn'] = 'nul'
            else:
                kwargs['logfn'] = '/dev/null'

        config = DefaultConfig()

        for key, value in kwargs.items():
            if isinstance(value, bool):
                config.set_boolean('-{}'.format(key), value)
            elif isinstance(value, int):
                config.set_int('-{}'.format(key), value)
            elif isinstance(value, float):
                config.set_float('-{}'.format(key), value)
            elif isinstance(value, str):
                config.set_string('-{}'.format(key), value)

        super(BasicDetector, self).__init__(config)

    def __str__(self):
        return self.hypothesis()

    @contextmanager
    def start_utterance(self):
        self.start_utt()
        yield
        self.end_utt()

    @contextmanager
    def end_utterance(self):
        self.end_utt()
        yield
        self.start_utt()

    def decode(self, audio_file=None, buffer_size=2048,
               no_search=False, full_utt=False):
        buf = bytearray(buffer_size)
        with open(audio_file or self.goforward, 'rb') as f:
            with self.start_utterance():
                while f.readinto(buf):
                    self.process_raw(buf, no_search, full_utt)
        return self

    def segments(self, detailed=False):
        if detailed:
            return [
                (s.word, s.prob, s.start_frame, s.end_frame)
                for s in self.seg()
            ]
        else:
            return [s.word for s in self.seg()]

    def hypothesis(self):
        hyp = self.hyp()
        if hyp:
            return hyp.hypstr
        else:
            return ''

    def probability(self):
        hyp = self.hyp()
        if hyp:
            return hyp.prob

    def score(self):
        hyp = self.hyp()
        if hyp:
            return hyp.best_score

    def best(self, count=10):
        return [
            (h.hypstr, h.score)
            for h, i in zip(self.nbest(), range(count))
        ]

    def confidence(self):
        hyp = self.hyp()
        if hyp:
            return self.get_logmath().exp(hyp.prob)


class LiveSpeechDetector(BasicDetector):

    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 16000)
        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.notification_start = kwargs.pop('sound_start', None)
        self.notification_end = kwargs.pop('sound_end', None)
        self.output_device = kwargs.pop('output_device', None)
        self.force_alsa = kwargs.pop('force_alsa', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.url = kwargs.pop('url', None)
        self.auth = kwargs.pop('auth', None)
        self.mime_type = kwargs.pop('mime_type')

        self.buf = bytearray(self.buffer_size)
        self.ad = Ad(self.audio_device, self.sampling_rate)

        self.in_speech = False
        self.recording = None
        self.recording_buffer = None

        payload_format = kwargs.pop('payload_format', None)
        self.use_opus = payload_format == "opus"
        self.opus_application = kwargs.pop('opus_application', 'voip')

        super(LiveSpeechDetector, self).__init__(**kwargs)

    def __iter__(self):
        with self.ad:
            with self.start_utterance():
                while self.ad.readinto(self.buf) >= 0:
                    self.process_raw(self.buf, self.no_search, self.full_utt)

                    if self.recording:
                        self.recording_buffer.extend(self.buf)
                        print(f"\rBuffer len = {len(self.recording_buffer)}", end='')

                    now = time.time()

                    if self.in_speech != self.get_in_speech():
                        # detect speech
                        self.in_speech = self.get_in_speech()

                    if self.recording:

                        # current length of recording
                        reclen = now - self.recording

                        # detect silence after wake word
                        if reclen > 30 or (reclen > 2 and not self.in_speech):
                            print("")
                            # stop after 30 seconds or after 2 seconds of silence after start
                            self.notify_end()
                            print("Recorded %.1f seconds of audio" % reclen)
                            self.send_sample()
                            self.recording = None
                            self.recording_buffer = None

                    if self.keyphrase and self.hyp():
                        # detect wake word
                        with self.end_utterance():
                            self.recording = time.time()
                            self.recording_buffer = bytearray()
                            self.notify_start()
                            yield self

    def stop(self, *args, **kwargs):
        raise StopIteration

    def send_sample(self):
        if self.use_opus:
            self.send_sample_opus()
        else:
            self.send_sample_wav()

    def send_sample_wav(self):
        # print(f'Buffer size: {len(self.recording_buffer)}')
        with io.BytesIO() as f:
            with wave.open(f, mode='wb') as wav:
                wav.setnchannels(1)
                wav.setframerate(self.sampling_rate)
                wav.setsampwidth(2)
                wav.writeframes(self.recording_buffer)

            self.send_sample_payload(f.getvalue(), "audio/vnd.wave;codec=1")

    def send_sample_opus(self):

        now = time.perf_counter_ns()

        encoder = pyogg.OpusBufferedEncoder()
        encoder.set_application(self.opus_application)
        encoder.set_sampling_frequency(self.sampling_rate)
        encoder.set_channels(1)
        encoder.set_frame_size(20)  # 20ms is the opus default

        with io.BytesIO() as f:
            ogg = pyogg.OggOpusWriter(f, encoder)
            ogg.write(self.recording_buffer)
            ogg.close()

            dur = (time.perf_counter_ns() - now) / 1000
            print("Encoding time: %.1f s" % dur)

            self.send_sample_payload(f.getvalue(), "audio/ogg;codecs=opus")

    def send_sample_payload(self, data, mimetype):
        print(f'Payload size: {sizeof_fmt(len(data))}')

        if self.url:
            res = requests.post(self.url, data=data, auth=self.auth, headers={"Content-Type": mimetype})
            print(res)

    def notify_start(self):
        print("Start listening...")
        if self.notification_start:
            self.play_sound(self.notification_start)

    def notify_end(self):
        print('Stop listening!')
        if self.notification_end:
            self.play_sound(self.notification_end)

    def play_sound(self, wav):
        print(f"Playing: {wav}")

        out = ""
        if self.output_device:
            # aplay and paplay use the same argument for selecting a device (--device)
            out = f" --device={self.output_device}"

        if self.force_alsa:
            cmd = f"aplay {wav}{out}"
        else:
            cmd = f"paplay {wav}{out}"

        print(f"Executing: '{cmd}'")
        os.system(cmd)
