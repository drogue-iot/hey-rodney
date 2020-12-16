FROM docker.io/ubuntu:20.04

LABEL org.opencontainers.image.source=https://github.com/drogue-iot/hey-rodney

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y vim alsa-utils pulseaudio-utils python3 python3-pip python3-numpy libopus0 libopusfile0 opus-tools \
 && apt-get install -y python3-dev build-essential swig git libpulse-dev libasound2-dev \
 && pip3 install --upgrade pocketsphinx \
 && pip3 install requests wave \
 && pip3 install git+https://github.com/TeamPyOgg/PyOgg@c78487ef52960d98ab3af5b66a744af8a5efe686 \
 && rm -Rf ~/.cache/pip \
 && apt-get -y purge python3-dev build-essential swig git libpulse-dev libasound2-dev \
 && apt-get -y autoremove --purge \
 && apt-get -y autoclean \
 && apt-get -y clean

RUN mkdir hey-rodney
COPY sounds /hey-rodney
COPY main.sh /hey-rodney/
COPY *.py /hey-rodney/

ENTRYPOINT ["/hey-rodney/main.sh"]
