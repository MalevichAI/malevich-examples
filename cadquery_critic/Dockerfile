FROM malevichai/app:python11_v0.1 as base

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y

RUN pip install cadquery cadquery-ocp cairosvg

COPY ./apps ./apps