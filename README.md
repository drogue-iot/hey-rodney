# "Hey Rodney, …"

The overall idea is to have a voice assistant for Kubernetes. Re-using the components that we build in
[Drogue IoT](https://github.com/drogue-iot).

In a nutshell:

* A container runs on the edge
    * Listen for the wake word "Hey Rondey"
    * Record the audio, following the wake word, for up to X seconds
    * Send the audio to the cloud backend for processing
* On the cloud side
    * Receive the audio samples
    * Run them through the speech-to-text API (audio -> json)
    * Evaluate the outcome of the request (audio response, command execution)
    * Process outcome

## Wake word detection

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

Currently handled by: https://github.com/drogue-iot/watson-speech-to-text-converter
