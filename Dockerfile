FROM ubuntu:20.04

# Set environment variable to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages including ZLIB and OpenTracing
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    git \
    wget \
    libcurl4-openssl-dev \
    libssl-dev \
    pkg-config \
    jq \
    libmicrohttpd-dev \
    zlib1g-dev \
    tzdata

# Install MessagePack (pinned version for compatibility)
RUN git clone --branch cpp-3.3.0 https://github.com/msgpack/msgpack-c.git /opt/msgpack-c \
    && cd /opt/msgpack-c \
    && cmake . \
    && make \
    && make install

# Install OpenTracing (v1.6.0)
RUN git clone --branch v1.6.0 https://github.com/opentracing/opentracing-cpp.git /opt/opentracing-cpp \
    && cd /opt/opentracing-cpp \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install

# Install Datadog APM dependencies (v1.3.7)
RUN wget https://github.com/DataDog/dd-opentracing-cpp/archive/refs/tags/v1.3.7.tar.gz -O dd-opentracing-cpp.tar.gz \
    && mkdir -p /opt/dd-opentracing-cpp \
    && tar zxvf dd-opentracing-cpp.tar.gz -C /opt/dd-opentracing-cpp --strip-components=1 \
    && cd /opt/dd-opentracing-cpp \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install

# Copy your project files
COPY . /usr/src/myapp
WORKDIR /usr/src/myapp

# Build your project
RUN cmake . && make

# Command to run your application
CMD ["./server"]
