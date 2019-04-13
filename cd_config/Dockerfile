FROM geospatialjeff/cognition-datasources:latest

# Upgrade cmake and install Google S2
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

RUN \
    yum install -y gflags-devel glog-devel gtest-devel openssl-devel; \
    git clone https://github.com/google/s2geometry.git; \
    cd s2geometry; \
    mkdir build; \
    cd build; \
    cmake ..; \
    make; \
    make install

COPY requirements.txt ./

RUN pip install -r requirements.txt

# Add Google S2 to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/lib/python3.6/site-packages/"