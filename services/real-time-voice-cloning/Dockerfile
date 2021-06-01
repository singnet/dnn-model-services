FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime

ARG git_owner="singnet"
ARG git_repo="dnn-model-services"
ARG git_branch="master"
ARG snetd_version

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

# Installing SNET Daemon
RUN SNETD_GIT_VERSION=`curl -s https://api.github.com/repos/singnet/snet-daemon/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")' || echo "v5.0.1"` && \
    SNETD_VERSION=${snetd_version:-${SNETD_GIT_VERSION}} && \
    cd /tmp && \
    wget https://github.com/singnet/snet-daemon/releases/download/${SNETD_VERSION}/snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    tar -xvf snet-daemon-${SNETD_VERSION}-linux-amd64.tar.gz && \
    mv snet-daemon-${SNETD_VERSION}-linux-amd64/snetd /usr/bin/snetd && \
    rm -rf snet-daemon-*

# Git cloning this repository
RUN cd ${SINGNET_REPOS} && \
    git clone -b ${git_branch} https://github.com/${git_owner}/${DNN_REPO_NAME}.git

# Git cloning Real-Time-Voice-Cloning repository to rtvc/
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning.git rtvc/ && \
    cd rtvc/ && \
    git checkout 5425557efe30863267f805851f918124191e0be0

# Putting it in PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:${SERVICES_FOLDER}/${SERVICE_NAME}/rtvc"

# Downloading the pre-trained models
RUN cd ${SINGNET_REPOS}/${DNN_REPO_NAME} && \
    sh utils/get_voice_model.sh

# Installing all the dependencies of the service
RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip install -U pip==21.0.1 && \
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
