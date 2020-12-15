FROM docker.io/ubuntu:20.04

LABEL org.opencontainers.image.source=https://github.com/drogue-iot/hey-rodney

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y vim alsa-utils pulseaudio-utils python3 python3-pip \
 && apt-get install -y python3-dev build-essential swig git libpulse-dev libasound2-dev \
 && pip3 install --upgrade pocketsphinx \
 && pip3 install requests wave \
 && rm -Rf ~/.cache/pip \
 && apt-get -y purge python3-dev build-essential swig git libpulse-dev libasound2-dev \
 && apt-get -y autoremove --purge \
 && apt-get -y autoclean \
 && apt-get -y clean

#RUN python3 -m pip install --upgrade pip setuptools wheel
#RUN pip3 install --upgrade pocketsphinx
#RUN pip3 install requests wave

#WORKDIR pocketsphinx-python
#RUN python3 setup.py install

RUN mkdir hey-rodney
COPY sounds /hey-rodney
COPY *.py /hey-rodney/
COPY main.sh /hey-rodney/

ENTRYPOINT ["/hey-rodney/main.sh"]
