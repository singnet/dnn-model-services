# Using this image because it performs better than nvidia/cuda-cudnn
FROM opennmt/opennmt:latest

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=${git_repo}
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/services
ENV SERVICE_NAME=siggraph-colorization

RUN mkdir -p ${SINGNET_REPOS}

RUN apt update && \
    apt install -y --no-install-recommends \
        libgomp1 \
        libprotobuf9v5 \
        libzmq1 \
        cmake \
        make \
        g++ \
        gcc \
        curl \
        nano \
        wget \
        git \
        libpng-dev \
        libjpeg-dev \
        python3-pip \
        python3 && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

ENV TORCH_DIR=/root/torch

ENV LUA_PATH="${TORCH_DIR}/share/lua/5.1/?.lua;${TORCH_DIR}/share/lua/5.1/?/init.lua;./?.lua"
ENV LUA_CPATH="${TORCH_DIR}/lib/lua/5.1/?.so;./?.so;${TORCH_DIR}/lib/?.so"
ENV PATH=${TORCH_DIR}/bin:${PATH}
ENV LD_LIBRARY_PATH=${TORCH_DIR}/lib:${LD_LIBRARY_PATH}
ENV THC_CACHING_ALLOCATOR=0

RUN mkdir /root/mkl && \
    ln -s /root/torch/lib /root/mkl/ && \
    luarocks install image

RUN SNETD_VERSION=`curl -s https://api.github.com/repos/singnet/snet-daemon/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")'` && \
    cd /tmp && \
    wget https://github.com/singnet/snet-daemon/releases/download/${SNETD_VERSION}/snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    mv snet-daemon-${SNETD_VERSION}-linux-amd64/snetd /usr/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git && \
    cd ${DNN_REPO_NAME}/utils && \
    sh get_colorize_model.sh

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip3 install -U pip && \
    pip3 install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
