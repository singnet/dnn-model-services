FROM ubuntu:18.04

ARG agent_contract
ARG private_key

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=dnn-model-services
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=YOLOv3_ObjectDetection
ENV SNETD_PORT=7005
ENV SNETD_CONFIG=snetd_object_detection_service_config.json
ENV AGENT_CONTRACT=${agent_contract}
ENV PRIVATE_KEY=${private_key}

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

# OpenCV dependencies
RUN apt-get install -y libsm6 libxext6 libxrender-dev

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/singnet/snet-cli && \
    cd snet-cli && \
    ./scripts/blockchain install && \
    pip3 install -e .

RUN cd ${SINGNET_REPOS} && \
    mkdir snet-daemon && \
    cd snet-daemon && \
    wget https://github.com/singnet/snet-daemon/releases/download/v0.1.1/snetd-0.1.1.tar.gz && \
    tar -xvf snetd-0.1.1.tar.gz && \
    cp snetd-linux-amd64 /usr/local/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/arturgontijo/${DNN_REPO_NAME}.git && \
    cd dnn-model-services/utils && \
    ./get_yolov3.sh

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    sh -c "echo '{  \"DAEMON_TYPE\": \"grpc\", \
                    \"DAEMON_LISTENING_PORT\": \"${SNETD_PORT}\", \
                    \"BLOCKCHAIN_ENABLED\": true, \
                    \"ETHEREUM_JSON_RPC_ENDPOINT\": \"https://kovan.infura.io\", \
                    \"AGENT_CONTRACT_ADDRESS\": \"${AGENT_CONTRACT}\", \
                    \"SERVICE_TYPE\": \"grpc\", \
                    \"PASSTHROUGH_ENABLED\": true, \
                    \"PASSTHROUGH_ENDPOINT\": \"http://localhost:7003\", \
                    \"LOG_LEVEL\": 10, \
                    \"PRIVATE_KEY\": \"${PRIVATE_KEY}\"}'" > ${SNETD_CONFIG}

RUN cd ${SERVICES_FOLDER}/${SERVICE_NAME} && \
    pip3 install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
