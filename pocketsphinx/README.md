### Build:

~~~shell script
podman build . -f Dockerfile -t quay.io/ctrontesting/pocketsphinx:latest
~~~

### Run (`fish`):

~~~shell script
podman run --rm -ti -v /run/user/(id -u)/:/run/user/(id -u)/ -e DEVICE_ID=rodney1 -e ENDPOINT=https://http-endpoint-drogue-iot.apps.wonderful.iot-playground.org -e XDG_RUNTIME_DIR=/run/user/(id -u) -e PULSE_SERVER=/run/user/(id -u)/pulse/native --security-opt label=disable quay.io/ctrontesting/pocketsphinx:latest
~~~

## Installation

## Provision device

We use the following settings here:

* **Device ID:** `foo`
* **Password:** `bar`

Execute the following command to register the device:

~~~bash
http POST https://device-management-service-drogue-iot.my.cluster/api/v1/devices device_id=foo password=bar
~~~

## Container host

The multi-arch image is available for `armv7`, `aarch64`, and `amd64`.

**Note:** Ubuntu 20.10 seems to be broken on the Raspberry Pi 3, I am not able to fire up containers due to some
segfaults. Fedora IoT is not supported for the Raspberry Pi 4.

**Note:** You can of course also run this on your `amd64` desktop/laptop.

### Ubuntu 20.10

You will need to install podman:

~~~bash
sudo apt-get install podman runc
~~~

**Can it run with Docker?** Maybe, I guess. I didn't test. Let me know. If you prefer typing in `docker`, you can
set an alias: `alias docker=podman`.

**Why use `sudo` if you also use `podman`?** We need to pass in the ALSA sound device into the container. This
requires additional privileges. Maybe there is a better way, let me know.

### Fedora IoT

Take a look at the documentation on how to get Fedora IoT on your Raspberry Pi: https://docs.fedoraproject.org/en-US/iot/physical-device-setup/

Podman comes pre-installed with Fedora IoT, so there is no need to install anything in addition.

**Note:** You may need to grow the system partition before you can pull images: https://lists.fedoraproject.org/archives/list/iot@lists.fedoraproject.org/thread/CY2ZB7IB3LNLBYUXL3ZQVD3FW27RTXWI/#WDH64ZCOWV52HDJUJBIDSFR5D7YR37O7

## Audio device

You can use `arecord` from the container to check which sounds cards are available to the container:

~~~bash
sudo podman run --rm -ti --device /dev/snd --entrypoint arecord ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest --list-devices
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
sudo podman run --rm -ti --device /dev/snd --entrypoint arecord ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest --list-pcm
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
`plughw`, because this one supports automatic format and sample conversion if needed.

You might also want to pick an output device. In the case of my headset, this is actually the same device. However,
you can use `aplay` (instead of `arecord`) to list the available output devices, and pick an alternate one instead.

## Running

The following call will run the container in the foreground and patch through the sound devices. This must run as `root`
in order to make the devices available inside the container.

**Note:** Hot-plugging devices does not work, as new devices will appear in the host, but will not get patched through
to the container.

You will also need to register a new device on the cloud side first. The following example assumes you created a
device `rodney1`, with the password `password1`:

~~~bash
ENDPOINT="https://http-endpoint-drogue-iot.my.cluster"
sudo podman run \
  --rm -ti \
  --device /dev/snd \
  -e FORCE_ALSA=true \
  ghcr.io/drogue-iot/hey-rodney-pocketsphinx:latest \
  -d rodney1 -e "$ENDPOINT" \
  -u rodney1 -p password1 \
  -i plughw:CARD=headset,DEV=0 \
  -o plughw:CARD=headset,DEV=0 \

~~~

### Pros:

  * Easy to configure
  * Provides silence detection

### Cons:

  * Either triggers to often, or not often enough
