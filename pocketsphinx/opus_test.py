#!/usr/bin/env python3

import time
import pyogg
import io

now = time.perf_counter_ns()

encoder = pyogg.OpusBufferedEncoder()
encoder.set_application("voip")
encoder.set_sampling_frequency(16000)
encoder.set_channels(1)
encoder.set_frame_size(20) # ms

with io.BytesIO() as f:
    ogg = pyogg.OggOpusWriter(f, encoder)
    ogg.write(bytearray(100))
    ogg.close()

    dur = (time.perf_counter_ns() - now) / 1000
    print(f"Encoding time: {dur} ms")
