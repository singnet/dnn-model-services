FROM microsoft/cntk:latest

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=dnn-model-services
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=cntk-image-recon
ENV SNETD_PORT=7004
ENV SNETD_CONFIG=snetd.config.json

RUN mkdir -p ${SINGNET_REPOS}

RUN apt-get update && \
    apt-get install -y \
    git \
    wget \
    nano \
    libudev-dev \
    libusb-1.0-0-dev

RUN apt-get install -y python3 python3-pip
RUN apt-get install -y nodejs npm

# Python 3.6.5 for snet-cli ============================================================================================
RUN apt-get install -y \
    build-essential \
    checkinstall \
    zlib1g-dev \
    libreadline-gplv2-dev \
	libncursesw5-dev \
	libssl-dev \
	libsqlite3-dev \
	tk-dev \
	libgdbm-dev \
	libc6-dev \
	libbz2-dev

RUN wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz && \
    tar xvf Python-3.6.5.tar.xz && \
    cd Python-3.6.5 && \
    ./configure && \
    make -j8 && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.6.5 && \
    rm -f Python-3.6.5.tar.xz

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/singnet/snet-cli && \
    cd snet-cli && \
    cat ./scripts/blockchain | sed "s/python3/python3.6/g" > ./scripts/blockchain && \
    ./scripts/blockchain install && \
    pip3.6 install -e .
# ======================================================================================================================

RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/v0.1.2/snetd-0.1.2.tar.gz && \
    tar -xvf snetd-0.1.2.tar.gz && \
    cp snetd-0.1.2/snetd-linux-amd64 /usr/local/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/singnet/${DNN_REPO_NAME}.git && \
    cd ${DNN_REPO_NAME}/utils && \
    ./get_cntk_models.sh

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    sh -c "echo '{ \"PRIVATE_KEY\": \"1000000000000000000000000000000000000000000000000000000000000000\", \
                   \"DAEMON_LISTENING_PORT\": ${SNETD_PORT}, \
                   \"ETHEREUM_JSON_RPC_ENDPOINT\": \"https://kovan.infura.io\", \
                   \"PASSTHROUGH_ENABLED\": true, \
                   \"PASSTHROUGH_ENDPOINT\": \"http://localhost:7003\", \
                   \"REGISTRY_ADDRESS_KEY\": \"0x2e4b2f2b72402b9b2d6a7851e37c856c329afe38\", \
                   \"DAEMON_END_POINT\": \"http://54.203.198.53:${SNETD_PORT}\", \
                   \"IPFS_END_POINT\": \"http://ipfs.singularitynet.io:80\", \
                   \"ORGANIZATION_NAME\": \"snet\", \
                   \"SERVICE_NAME\": \"${SERVICE_NAME}\", \
                   \"LOG\": { \
                   \"LEVEL\": \"debug\", \
                   \"OUTPUT\": { \
                       \"TYPE\": \"stdout\" \
                       } \
                   } \
                }'" > ${SNETD_CONFIG}

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip3 install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}