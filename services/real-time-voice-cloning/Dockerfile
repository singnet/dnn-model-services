FROM pytorch/pytorch

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/services
ENV SERVICE_NAME=real-time-voice-cloning

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    git \
    wget \
    nano \
    curl \
    unzip

RUN apt-get clean && \
    apt-get update && \
    apt-get install -y ffmpeg libportaudio2 && \
    apt-get -y autoremove

RUN SNETD_VERSION=`curl -s https://api.github.com/repos/singnet/snet-daemon/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")'` && \
    cd /tmp && \
    wget https://github.com/singnet/snet-daemon/releases/download/${SNETD_VERSION}/snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    mv snet-daemon-${SNETD_VERSION}-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git

# Git cloning Real-Time-Voice-Cloning codes to rtvc/ and put it in PYTHONPATH
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning.git rtvc/ && \
    export PYTHONPATH=${PYTHONPATH}:$(pwd)/rtvc

# Downloading the pre-trained models
RUN cd ${DNN_REPO_NAME} && \
    sh utils/get_voice_model.sh

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
