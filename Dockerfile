FROM lambci/lambda:build-python3.6

# Installing system libraries
RUN \
    yum install -y wget; \
    yum install -y gflags-devel glog-devel gtest-devel openssl-devel; \
    yum clean all; \
    yum autoremove;

# Switch to build directory
WORKDIR /build

# Upgrading CMAKE
RUN \
    mkdir cmake-config; \
    cd cmake-config; \
    yum remove cmake -y; \
    wget https://cmake.org/files/v3.6/cmake-3.6.2.tar.gz; \
    tar -zxvf cmake-3.6.2.tar.gz; \
    cd cmake-3.6.2; \
    ./bootstrap --prefix=/usr/local; \
    make; \
    make install; \
    cd ..; rm -rf cmake-config

# Building Google S2 Library
RUN \
    git clone https://github.com/google/s2geometry.git; \
    cd s2geometry; \
    mkdir build; \
    cd build; \
    cmake ..; \
    make; \
    make install

# Installing cognition-datasources + requirements
COPY requirements.txt ./

RUN \
    pip install -r requirements.txt;


# Copy shell scripts
COPY bin/* /usr/local/bin/

WORKDIR /home/spatial-db