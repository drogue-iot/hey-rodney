# Installation

## Provision device

We use the following settings here:

* **Device ID:** `foo`
* **Password:** `bar`

Execute the following command to register the device:

~~~bash
http POST https://device-management-service-drogue-iot.my.cluster/api/v1/devices device_id=foo password=bar
~~~

## Container host

**Note:** Ubuntu 20.10 seems to be broken on the Raspberry Pi 3. Fedora IoT is not supported for the Raspberry Pi 4.

### Ubuntu 20.10

You will need to install podman:

~~~bash
apt-get install podman runc
~~~

### Fedora IoT

Take a look at the documentation on how to get Fedora IoT your Raspberry Pi: https://docs.fedoraproject.org/en-US/iot/physical-device-setup/

Podman comes pre-installed with Fedora IoT.

## Audio device

You can use `aplay` from the container to check which sounds cards are available to the container:

~~~bash
podman run --rm -ti --device --entrypoint arecord /dev/snd ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest --list-devices
~~~

The output should be something like this:

~~~
**** List of CAPTURE Hardware Devices ****
card 1: headset [Sennheiser USB headset], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
~~~

As you can see, I have the Raspberry Pi onboard card (`bcm2835`) and an additional, external USB device (`Sennheiser USB headset`).
However, we need to pass in the device name using ALSA's device name syntax. You can get this list by executing:

~~~
podman run --rm -ti --device --entrypoint arecord /dev/snd ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest --list-pcm
~~~

This list is much longer, so you need to spot your device:

~~~
...
hw:CARD=headset,DEV=0
    Sennheiser USB headset, USB Audio
    Direct hardware device without any conversions
plughw:CARD=headset,DEV=0
    Sennheiser USB headset, USB Audio
    Hardware device with all software conversions
~~~

My headset from before is `plughw:CARD=headset,DEV=0` here. Notice that the same headset shows up multiple times. This
is because there are multiple ways to connect to the hardware. The best approach is to pick the one starting with
`plughw`, because this allows to run automatic format and sample conversion as necessary.

You might also want to pick an output device. In the case of my headset, this is actually the same device. However,
you can use `aplay` (instead of `arecord`) to list the available output devices, and pick an alternate one instead.

## Running

The following call will run the container in the foreground and patch through the sound devices. This must run as `root`
in order to make the devices available inside the container.

**Note:** Hot-plugging devices does not work, as new devices will appear in the host, but will not get patched through
to the container.

~~~bash
podman run \
  --rm -ti \
  --device /dev/snd \
  -e FORCE_ALSA=true \
  ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest \
  -d rodney1 -e https://http-endpoint-drogue-iot.my.cluster \
  -u foo -p bar \
  -i plughw:CARD=M0,DEV=0 \
  -o plughw:CARD=M0,DEV=0 \
  
~~~

