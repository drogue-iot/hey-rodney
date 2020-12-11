#!/usr/bin/env python3

#
# Derived from: https://github.com/alphacep/vosk-server/blob/master/websocket/test_microphone.py
#
# SPDX: Apache-2.0
#

import asyncio
import websockets
import sys
from pyaudio import PyAudio, Stream, paInt16
from contextlib import asynccontextmanager, contextmanager, AsyncExitStack
from typing import AsyncGenerator, Generator

import argparse
import json

@contextmanager
def _pyaudio() -> Generator[PyAudio, None, None]:
    p = PyAudio()
    try:
        yield p
    finally:
        print('Terminating PyAudio object')
        p.terminate()


@contextmanager
def _pyaudio_open_stream(p: PyAudio, *args, **kwargs) -> Generator[Stream, None, None]:
    s = p.open(*args, **kwargs)
    try:
        yield s
    finally:
        print('Closing PyAudio Stream')
        s.close()


@asynccontextmanager
async def _polite_websocket(ws: websockets.WebSocketClientProtocol) -> AsyncGenerator[
    websockets.WebSocketClientProtocol, None]:
    try:
        yield ws
    finally:
        print('Terminating connection')
        await ws.send('{"eof" : 1}')
        print(await ws.recv())


async def hello(uri, input, rate):
    async with AsyncExitStack() as stack:
        ws = await stack.enter_async_context(websockets.connect(uri))
        print(f'Connected to {uri}')
        print('Type Ctrl-C to exit')
        ws = await stack.enter_async_context(_polite_websocket(ws))
        p = stack.enter_context(_pyaudio())
        s = stack.enter_context(_pyaudio_open_stream(p,
                                                     input_device_index=input,
                                                     format=paInt16,
                                                     channels=1,
                                                     rate=rate,
                                                     input=True,
                                                     frames_per_buffer=rate))
        while True:
            data = s.read(rate)
            if len(data) == 0:
                break
            await ws.send(data)
            recv = await ws.recv()
            print(recv)
            process(json.loads(recv))


def process(recv):
    if 'result' in recv and 'text' in recv:
        print('Checking trigger')
        words = recv.get('text')
        if is_wake(words):
            wake(words)
        else:
            print(f'Ignored: {words}')


def is_wake(words):
    # variants that we accept as wake word
    return {
        'hey rodney': True,
        'hi rodney': True,
        'hey rocky': True,
        'hi rocky': True,
        'hey rob me': True,
        'hi rob me': True,
        'hey rugby': True,
        'hi rugby': True,
        'i wrote me': True,
    }.get(words, False)


def wake(words):
    print(f'Listening ({words})...')


parser = argparse.ArgumentParser(description='Vosk Agent')
parser.add_argument('-s', '--server', dest='server', default='localhost:2700',
                    help='address of the Vosk API (default: localhost:2700)')
parser.add_argument('-i', '--input', dest='input', type=int, help='audio input device')
parser.add_argument('-r', '--rate', dest='rate', type=int, default='8000', help='sample rate in Hz (default: 8000)')
args = parser.parse_args()

print(f'Connecting to server: {args.server}')
print(f'Input device: {args.input}')

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        hello(f'ws://' + args.server, args.input, args.rate))
except (Exception, KeyboardInterrupt) as e:
    loop.stop()
    loop.run_until_complete(
        loop.shutdown_asyncgens())
    if isinstance(e, KeyboardInterrupt):
        print('Bye')
        exit(0)
    else:
        print(f'Oops! {e}')
        exit(1)
