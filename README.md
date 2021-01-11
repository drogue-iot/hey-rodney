# "Hey Rodney, …"

[![Matrix](https://img.shields.io/matrix/drogue-iot:matrix.org)](https://matrix.to/#/#drogue-iot:matrix.org)

The overall idea is to have a voice assistant for Kubernetes. Re-using the components that we build in
[Drogue IoT](https://github.com/drogue-iot).

In a nutshell:

* A container runs on the edge
    * Listen for the wake word "Hey Rodney"
    * Record the audio, following the wake word, for up to X seconds
    * Send the audio to the cloud backend for processing
* On the cloud side
    * Receive the audio samples
    * Run them through the speech-to-text API (audio -> json)
    * Evaluate the outcome of the request (audio response, command execution)
    * Process outcome

## Words of caution!

* This is a demo. Don't expect too much ;-)
* The accuracy of wake word and speech recognition is highly dependency on the microphone you use. Really, I mean it!
  
  If you feel that it is bad, double check the quality of your recordings.

## Installation

### On device

Check out the installation here: [pocketsphinx/](pocketsphinx/).

**Note:** This installation is based on *Pocketsphinx* for the moment. See below for evaluations of the different
options of wake word detection. Feel free to propose additional options.

### Cloud

Deploy the `deploy/` folder using:

~~~shell
kubectl apply -k deploy/
~~~

Deploying the setup will create a "rules" files inside the `ConfigMap` named `hey-rodney-config`. You can use this
to configure additional rules beside the one provided.

The "matcher" is a regular expression, which can also have groups and named groups. These groups can be re-used in
the command section:

~~~yaml
rules:
  - matcher: say hello to (.*)
    commands:
      - execute: [ "echo", "Hello to: ${1}" ]
~~~

The commands that you execute are executed as part of the request handling, inside the container. This isn't optimal!
Then again, this is just a demo! `kubectl` is part of the container. If you need other commands, you need to build
your own image, or raise a PR.

## Testing

If a Raspberry Pi setup is not feasible for your, or you are frustrated with wake word detection, you can also record
an audio sample in a WAV file and manually submit it:

~~~bash
cat restart-console-pods.wav | http -v -a device:password POST https://http-endpoint-drogue-iot.my.cluster/publish/device/voice "Content-Type:audio/wav"
~~~

## Errors and happy little accidents

### Lagging in recording

Sometimes recording seems to lag. You hear the *bing*, but it didn't detect anything.

Check the CPU load of your Raspberry Pi, if it shows a `python3` process consuming ~99% of your CPU, then you simply
need more compute power. Or you need to accept the fact that it lags a bit.

### It doesn't wake up

Check your microphone! The quality of the microphone and surrounding noises can make a huge difference. A headset
gives some good results, although it definitely isn't as cool as a desk microphone.

After you fiddled a bit with an audio setup like this, you suddenly have much more respect for your average voice
assistant at home.

### Typos

I am pretty sure there are some typos in this repository. However, some of them are intentionally.

For example, the phase for waking up Rodney should be "Hey Rodney", turns out that setting the keyphrase to "hay rodney"
works a bit better.

When defining rules for processing, it may be necessary to take into account several alternatives for some words.
For example "restart console pods" most often gets transcribed as "restart console pots" and sometimes as
"restart console parts". So the matcher (being a regular expression) should be "restart console (pods|parts|pots)".

### `413` when submitting voice sample

If you get an error `413`, you might need to increase the maximum payload size:

~~~
kn service update http-endpoint -e MAX_PAYLOAD_SIZE=4194304 # 4MiB
~~~

## Evaluation of wake word detection solutions

### Mycroft Precise

Build:

~~~shell script
podman build . -t quay.io/ctrontesting/mycroft-precise:latest
~~~

Run (`fish`):
~~~shell script
sudo podman run --rm -v (pwd)/asound.conf:/etc/asound.conf:z --device /dev/snd -ti quay.io/ctrontesting/mycroft-precise:latest
~~~

Pros:

  * No false positives 

Cons:

  * Rarely triggers
  * Hard to set up
  * No silence detection

### Pocketsphinx

Build:

~~~shell script
podman build . -f Dockerfile -t quay.io/ctrontesting/pocketsphinx:latest
~~~

Run (`fish`): 

~~~shell script
podman run --rm -ti -v /run/user/(id -u)/:/run/user/(id -u)/ -e DEVICE_ID=rodney1 -e ENDPOINT=https://http-endpoint-drogue-iot.apps.wonderful.iot-playground.org -e XDG_RUNTIME_DIR=/run/user/(id -u) -e PULSE_SERVER=/run/user/(id -u)/pulse/native --security-opt label=disable quay.io/ctrontesting/pocketsphinx:latest
~~~

Pros:

  * Easy to configure
  * Provides silence detection

Cons:

  * Either triggers to often, or not often enough

### Vosk & Kaldi

Run server:

~~~shell script
podman run -ti --rm -p 2700:2700 docker.io/alphacep/kaldi-en:latest
~~~

Then run client:

~~~shell script
./vosk/test_microphone.py
~~~

Pros:

  * No direct wake-word functionality
  * Ready to run container with Websocket integration

Cons:

  * Need to filter out "wake word" variants ( "he wrote me" -> "hey rodney" )
  * Accuracy is poor

## Speech to text

This is currently handled by: https://github.com/drogue-iot/watson-speech-to-text-converter
