FROM pytorch/pytorch:0.4.1-cuda9-cudnn7-runtime

ENV SINGNET_REPOS=/opt/singnet
ENV DNN_REPO_NAME=dnn-model-services
ENV SERVICES_FOLDER=${SINGNET_REPOS}/${DNN_REPO_NAME}/Services/gRPC
ENV SERVICE_NAME=places365-scene-recognition
ENV SERVICE_ROOT=${SERVICES_FOLDER}/${SERVICE_NAME}
ENV SNETD_HOST=http://54.203.198.53
ENV SNETD_PORT=7019
ENV GRPC_HOST=http://localhost
ENV GRPC_PORT=7018
ENV SNETD_CONFIG=snetd.config.json
ENV ACCOUNT=singnet
ENV BRANCH=master

RUN mkdir -p ${SINGNET_REPOS}

# Updating and installing common and project dependencies
RUN apt-get update
RUN apt-get install -y \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6
RUN pip install --upgrade pip

# Installing SNET (snet-cli and snet-daemon + dependencies)
RUN git clone https://github.com/ramongduraes/snet.git &&\
    cd snet/utils &&\
    ./install_snet.sh &&\
    cd ../.. &&\
    rm -rf snet

# Cloning service repository, downloading models
RUN cd ${SINGNET_REPOS} && \
    git clone -b $BRANCH --single-branch https://github.com/${ACCOUNT}/${DNN_REPO_NAME}.git &&\
    cd dnn-model-services/utils && \
    ./get_places365_models.sh

# Writing snetd.config.json
RUN cd ${SERVICE_ROOT} &&\
    sh -c "echo '{ \"ETHEREUM_JSON_RPC_ENDPOINT\": \"https://kovan.infura.io\", \
                   \"PASSTHROUGH_ENABLED\": true, \
                   \"PASSTHROUGH_ENDPOINT\": \"${GRPC_HOST}:${GRPC_PORT}\", \
                   \"REGISTRY_ADDRESS_KEY\": \"0x2e4b2f2b72402b9b2d6a7851e37c856c329afe38\", \
                   \"DAEMON_END_POINT\": \"${SNETD_HOST}:${SNETD_PORT}\", \
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

# Building protobuf messages
RUN cd ${SERVICE_ROOT} && \
    pip install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICE_ROOT}