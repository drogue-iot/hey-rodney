FROM docker.io/ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y git vim alsa-utils

RUN apt-get install -y sudo curl python3 python3-pip swig
RUN apt-get install -y python3 python3-dev python3-pip build-essential swig git libpulse-dev libasound2-dev
RUN apt-get install -y pulseaudio-utils
#RUN git clone --depth 1 --shallow-submodules --recursive https://github.com/bambocher/pocketsphinx-python


RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install --upgrade pocketsphinx
RUN pip3 install requests wave

#WORKDIR pocketsphinx-python
#RUN python3 setup.py install

RUN mkdir hey-rodney
COPY sounds /hey-rodney
COPY *.py /hey-rodney/

ENTRYPOINT ["/hey-rodney/main.py"]
