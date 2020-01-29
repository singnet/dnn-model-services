FROM nvidia/cuda:9.0-cudnn7-runtime

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/services
ENV SERVICE_NAME=zeta36-chess-alpha-zero

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    libgomp1 \
    git \
    wget \
    nano \
    curl

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.6 python3.6-dev python3.6-venv

RUN cd ${SINGNET_REPOS} && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.6 get-pip.py && \
    rm -f get-pip.py

RUN SNETD_VERSION=`curl -s https://api.github.com/repos/singnet/snet-daemon/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")'` && \
    cd /tmp && \
    wget https://github.com/singnet/snet-daemon/releases/download/${SNETD_VERSION}/snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    mv snet-daemon-${SNETD_VERSION}-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    python3.6 -m pip install -U pip && \
    python3.6 -m pip install -r requirements.txt && \
    sh buildproto.sh

# chess-alpha-zero
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    git clone https://github.com/Zeta36/chess-alpha-zero.git

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
