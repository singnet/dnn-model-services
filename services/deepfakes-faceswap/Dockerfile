FROM nvidia/cuda:9.0-cudnn7-runtime

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/services
ENV SERVICE_NAME=deepfakes-faceswap

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    git \
    wget \
    nano \
    curl

# OpenCV dependencies
RUN apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev

RUN apt-get install -y python3 python3-pip ffmpeg

RUN SNETD_VERSION=`curl -s https://api.github.com/repos/singnet/snet-daemon/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")'` && \
    cd /tmp && \
    wget https://github.com/singnet/snet-daemon/releases/download/${SNETD_VERSION}/snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    mv snet-daemon-${SNETD_VERSION}-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git

# Getting the Deepfakes/faceswap codes
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    git clone https://github.com/deepfakes/faceswap.git

# Getting content-server module
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip3 install git+https://github.com/arturgontijo/content-server.git

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip3 install -U pip && \
    pip3 install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
