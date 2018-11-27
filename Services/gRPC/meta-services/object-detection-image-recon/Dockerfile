FROM ubuntu:18.04

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=dnn-model-services
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC/Meta_Services
ENV SERVICE_NAME=object-detection-image-recon
ENV SNETD_PORT=7009
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

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/singnet/snet-cli && \
    cd snet-cli && \
    ./scripts/blockchain install && \
    pip3 install -e .

RUN snet identity create META_ID key --private-key ${PRIVATE_KEY}

RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/v0.1.2/snetd-0.1.2.tar.gz && \
    tar -xvf snetd-0.1.2.tar.gz && \
    cp snetd-0.1.2/snetd-linux-amd64 /usr/local/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/arturgontijo/${DNN_REPO_NAME}.git

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
