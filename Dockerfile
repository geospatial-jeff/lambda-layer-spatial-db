FROM geospatialjeff/cognition-datasources-db:latest

# Switch to build directory
WORKDIR /build

# Installing lambda-db requirements
COPY requirements.txt ./

RUN \
    pip install -r requirements.txt;

# Copy shell scripts
COPY bin/* /usr/local/bin/

WORKDIR /home/spatial-db