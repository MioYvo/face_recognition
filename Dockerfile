# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.6-slim-stretch

COPY . /root/face_recognition

RUN apt-get -y update && \
    apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

# RUN cd /root/face_recognition && \
#     pip3 install -r requirements.txt && \
#     # install dlib
#     cd /root/face_recognition/dlib && \
#     python3 setup.py install --yes USE_AVX_INSTRUCTIONS && \
#     # install face_recognition
#     cd /root/face_recognition && \
#     python3 setup.py install

RUN pip3 install -r /root/face_recognition/requirements.txt && \
    cd /root/face_recognition/dlib && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS && \
    cd /root/face_recognition && \
    python3 setup.py install

# The rest of this file just runs an example script.

# If you wanted to use this Dockerfile to run your own app instead, maybe you would do this:
# COPY . /root/your_app_or_whatever
# RUN cd /root/your_app_or_whatever && \
#     pip3 install -r requirements.txt
# RUN whatever_command_you_run_to_start_your_app

CMD cd /root/face_recognition/examples && \
    python3 recognize_faces_in_pictures.py
