# Setup container with Ubuntu 22.04 image
FROM ubuntu:22.04

# Set the working directory to /
WORKDIR /

# expose ports for openvswitch-switch
EXPOSE 6633 6653 6640

# Update container image
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
        lsb-release sudo \
        zip unzip wget git ca-certificates \
        curl iproute2 iputils-ping net-tools \
        python3 python3-pip \
        tcpdump vim x11-xserver-utils xterm && \
        update-ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    alias python=python3

COPY . /mini-ndn

RUN cd mini-ndn && \
    pip3 install -r requirements.txt && \
    ./install.sh -y --source && \
    cd dl/mininet && make install && cd ../.. && \
    cd dl/mininet-wifi && make install && cd ../.. && \
    rm -rf dl && rm -rf /var/lib/apt/lists/* && cd /

COPY docker/ENTRYPOINT.sh /
RUN chmod +x ENTRYPOINT.sh

# Change the working directory to /mini-ndn
WORKDIR /mini-ndn

ENTRYPOINT ["/ENTRYPOINT.sh"]
