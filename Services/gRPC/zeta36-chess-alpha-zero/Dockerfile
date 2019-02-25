FROM nvidia/cuda:8.0-cudnn6-runtime-ubuntu16.04

ARG git_owner
ARG git_repo
ARG git_branch

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=zeta36-chess-alpha-zero

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    libgomp1 \
    git \
    wget \
    nano

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.6 python3.6-dev python3.6-venv

RUN cd ${SINGNET_REPOS} && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.6 get-pip.py && \
    rm -f get-pip.py

RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/0.1.7/snet-daemon-v0.1.7-linux-amd64.tar && \
    tar zxvf snet-daemon-v0.1.7-linux-amd64.tar && \
    mv snet-daemon-v0.1.7-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    python3.6 -m pip install -r requirements.txt && \
    sh buildproto.sh

# chess-alpha-zero
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    git clone https://github.com/Zeta36/chess-alpha-zero.git

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
