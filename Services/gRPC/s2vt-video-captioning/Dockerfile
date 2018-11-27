FROM bvlc/caffe:gpu

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=dnn-model-services
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=s2vt-video-captioning
ENV SNETD_PORT=7004
ENV SNETD_CONFIG=snetd_video_cap_service_config.json

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
    wget https://github.com/singnet/snet-daemon/releases/download/v0.1.2/snetd-0.1.2.tar.gz && \
    tar -xvf snetd-0.1.2.tar.gz && \
    cp snetd-0.1.2/snetd-linux-amd64 /usr/local/bin/snetd

RUN cd ${SINGNET_REPOS} && \
    git clone https://github.com/arturgontijo/${DNN_REPO_NAME}.git && \
    cd dnn-model-services/Services/gRPC/s2vt-video-captioning && \
    cd service/utils && \
    ./get_s2vt.sh

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
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}
