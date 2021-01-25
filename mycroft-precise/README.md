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
