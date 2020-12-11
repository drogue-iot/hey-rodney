FROM docker.io/ubuntu:20.04 as builder

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y git

RUN apt-get install -y sudo curl
RUN apt-get install -y python3-pip curl libopenblas-dev python3-scipy cython libhdf5-dev python3-h5py portaudio19-dev swig libpulse-dev libatlas-base-dev

RUN git clone https://github.com/mycroftai/mycroft-precise --branch master
WORKDIR mycroft-precise
RUN git remote add matthew https://github.com/MatthewScholefield/mycroft-precise && \
    git fetch matthew && \
    git checkout feature/tf2

# patch tensorflow-cpu
RUN sed -i 's/tensorflow-gpu/tensorflow-cpu/g' setup.py

RUN apt-get install -y python3-venv

RUN apt-get install python3-dev python3-pip python3-wheel -y
RUN pip3 install wheel

#
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#

RUN python3 -m venv .venv
RUN bash -c "source .venv/bin/activate && pip3 install wheel"
RUN bash -c "source .venv/bin/activate && pip3 install \"numpy==1.16.0\""
RUN bash -c "source .venv/bin/activate && pip3 install \"h5py<2.11.0,>=2.10.0\""
RUN bash -c "source .venv/bin/activate && pip3 install \"scipy==1.4.1\""

#RUN ./setup.sh
RUN bash -c "source .venv/bin/activate && pip3 install -e runner"
RUN bash -c "source .venv/bin/activate && pip3 install -e ."

# uninstall 'typing': https://stackoverflow.com/a/58067012
RUN bash -c "source .venv/bin/activate && pip3 uninstall -y typing"
RUN bash -c "source .venv/bin/activate && pip3 install pyinstaller"
RUN ./build.sh
#RUN bash -c "source .venv/bin/activate && pip3 install pyinstaller"

FROM docker.io/ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

#COPY --from=builder /mycroft-precise/dist/precise-all_*.tar.gz /mycroft-precise.tar.gz

#RUN tar xvzf mycroft-precise.tar.gz

RUN apt-get update
RUN apt-get install -y curl python3 libopenblas-dev portaudio19-dev swig libpulse-dev libatlas-base-dev alsa-utils pulseaudio-utils pciutils vim

RUN mkdir /mycroft-precise
COPY --from=builder /mycroft-precise/.venv /mycroft-precise/.venv
COPY --from=builder /mycroft-precise/runner /mycroft-precise/runner
COPY --from=builder /mycroft-precise/precise /mycroft-precise/precise
COPY --from=builder /mycroft-precise/mycroft_precise.egg-info /mycroft-precise/mycroft_precise.egg-info

WORKDIR mycroft-precise

RUN curl -sSL https://github.com/MycroftAI/Precise-Community-Data/raw/master/marvin/models/marvin-en-0.3.0-20190817-jarbas.tar.gz -o marvin-en.tar.gz
RUN curl -sSL https://github.com/MycroftAI/Precise-Community-Data/raw/master/computer/models/computer-en-0.2.0-20190814-eltocino.tar.gz -o computer-en.tar.gz
RUN tar xzf marvin-en.tar.gz
RUN tar xzf computer-en.tar.gz

COPY main.py .

RUN chmod a+x main.py

CMD [ "bash", "--rcfile", ".venv/bin/activate" ]

