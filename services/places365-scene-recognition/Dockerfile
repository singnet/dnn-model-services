FROM pytorch/pytorch:0.4.1-cuda9-cudnn7-runtime

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"
ARG snetd_version="v0.1.7"

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/services
ENV SERVICE_NAME=places365-scene-recognition

RUN mkdir -p ${SINGNET_REPOS}

# Updating and installing common and project dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 && \
    pip install cython && \
    pip install --upgrade pip

# Installing SNET Daemon
RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/${snetd_version}/snet-daemon-${snetd_version}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${snetd_version}-linux-amd64.tar.gz && \
    mv snet-daemon-${snetd_version}-linux-amd64/snetd /usr/bin/snetd

# Cloning service repository, downloading models
RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} --single-branch https://github.com/${git_owner}/${DNN_REPO_NAME}.git &&\
    cd ${DNN_REPO_NAME}/utils && \
    ./get_places365_models.sh

# Building protobuf messages
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}