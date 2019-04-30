FROM nvidia/cuda:8.0-devel-ubuntu16.04 as torch_builder

RUN apt update && \
    apt install -y \
        autoconf \
        automake \
        build-essential \
        cmake \
        curl \
        g++ \
        gcc \
        git \
        libprotobuf-dev \
        libprotobuf9v5 \
        libreadline-dev \
        libtool \
        libzmq-dev \
        pkg-config \
        protobuf-compiler \
        unzip \
        nano \
        wget

# Fetch Intel MKL.
RUN mkdir /root/mkl && \
    wget https://anaconda.org/intel/mkl/2018.0.1/download/linux-64/mkl-2018.0.1-intel_4.tar.bz2 && \
    tar -xf mkl-2018.0.1-intel_4.tar.bz2 -C /root/mkl && \
    rm mkl-2018.0.1-intel_4.tar.bz2
ENV MKL_ROOT=/root/mkl
RUN rm -f $MKL_ROOT/lib/*vml* \
          $MKL_ROOT/lib/*ilp64* \
          $MKL_ROOT/lib/*blacs* \
          $MKL_ROOT/lib/*scalapack* \
          $MKL_ROOT/lib/*cdft* \
          $MKL_ROOT/lib/libmkl_tbb_thread.so \
          $MKL_ROOT/lib/libmkl_ao_worker.so

# Compile Torch.
ARG CUDA_ARCH
ENV CUDA_ARCH=${CUDA_ARCH:-Common}
RUN git clone https://github.com/torch/distro.git /root/torch-distro --recursive && \
    cd /root/torch-distro && \
    mkdir /root/torch && \
    CMAKE_LIBRARY_PATH=$CMAKE_LIBRARY_PATH:$MKL_ROOT/lib \
    TORCH_CUDA_ARCH_LIST=${CUDA_ARCH} TORCH_NVCC_FLAGS="-Xfatbin -compress-all" \
    PREFIX=/root/torch ./install.sh
RUN cp -r $MKL_ROOT/lib/* /root/torch/lib
RUN /root/torch/bin/luarocks install tds && \
    /root/torch/bin/luarocks install dkjson && \
    /root/torch/bin/luarocks install restserver-xavante && \
    /root/torch/bin/luarocks install yaml && \
    /root/torch/bin/luarocks install bit32 && \
    /root/torch/bin/luarocks install luacheck && \
    /root/torch/bin/luarocks install luacov && \
    /root/torch/bin/luarocks install lua-zmq \
        ZEROMQ_LIBDIR=/usr/lib/x86_64-linux-gnu/ ZEROMQ_INCDIR=/usr/include

FROM nvidia/cuda:8.0-runtime-ubuntu16.04

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

COPY --from=torch_builder /root/torch ${TORCH_DIR}

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
    pip3 install -r requirements.txt && \
    sh buildproto.sh

WORKDIR ${SERVICES_FOLDER}/${SERVICE_NAME}