FROM bvlc/caffe:gpu

ARG git_owner
ARG git_repo
ARG git_branch

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=s2vt-video-captioning

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    git \
    wget \
    nano \
    python-tk

# Caffe dependencies
RUN apt-get install -y libsm6 libxext6 libxrender-dev

RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/v0.1.5/snet-daemon-v0.1.5-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-v0.1.5-linux-amd64.tar.gz && \
    mv snet-daemon-v0.1.5-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git && \
    cd dnn-model-services/Services/gRPC/s2vt-video-captioning && \
    cd service/utils && \
    ./get_s2vt.sh

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
