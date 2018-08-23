FROM golang:latest
WORKDIR /
RUN apt-get update && apt-get install -y \
    nano \
    wget \
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
    libbz2-dev \
    libusb-1.0-0-dev \
    libudev1 \
    libudev-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sL https://deb.nodesource.com/setup_8.x -o nodesource_setup.sh
RUN chmod 755 nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install -y nodejs
RUN apt-get install -y protobuf-compiler libprotobuf-dev
RUN go get -v -u github.com/golang/dep/cmd/dep
RUN go get -v -u github.com/golang/protobuf/protoc-gen-go
RUN go get -v -u github.com/golang/lint/golint
RUN mkdir -p /go/src/github.com/singnet
WORKDIR /go/src/github.com/singnet
RUN git clone https://github.com/singnet/snet-daemon.git
WORKDIR /go/src/github.com/singnet/snet-daemon
RUN ./scripts/install
RUN ./scripts/build linux amd64
RUN cp ./build/snetd-linux-amd64 /go/bin/snetd
WORKDIR /go/src
RUN wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
RUN tar xvf Python-3.6.5.tar.xz
WORKDIR /go/src/Python-3.6.5/
RUN ./configure
RUN make -j8
RUN make altinstall
WORKDIR /go/src
RUN rm -rf Python-3.6.5/
RUN rm -f Python-3.6.5.tar.xz
RUN pip3.6 install --upgrade pip
RUN pip3.6 install snet_cli
RUN git clone https://github.com/arturgontijo/snet_bh.git
WORKDIR /go/src/snet_bh/Snet_Services/gRPC/Basic_Template
RUN pip3.6 install -r requirements.txt
RUN sh buildproto.sh
EXPOSE 7000-7001
CMD ["python3.6", "run_basic_service.py", "--daemon-conf", "config/"]