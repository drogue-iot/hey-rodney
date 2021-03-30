### Vosk & Kaldi

Run server:

~~~shell script
podman run -ti --rm -p 2700:2700 docker.io/alphacep/kaldi-en:latest
~~~

Then run client:

~~~shell script
./test_microphone.py
~~~

Pros:

  * No direct wake-word functionality
  * Ready to run container with Websocket integration

Cons:

  * Need to filter out "wake word" variants ( "he wrote me" -> "hey rodney" )
  * Accuracy is poor
