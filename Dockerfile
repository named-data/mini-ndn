# Setup container with Ubuntu 20.04 image
FROM ubuntu:20.04

# Set the working directory to /
WORKDIR /

# expose ports for openvswitch-switch
EXPOSE 6633 6653 6640

# Update container image
RUN apt-get update -y && \
    apt-get autoremove -y && \
    apt-get install --no-install-recommends -y \
        lsb-release sudo \
        zip unzip wget git ca-certificates \
        curl iproute2 iputils-ping net-tools \
        tcpdump vim x11-xserver-utils xterm && \
        update-ca-certificates && \
    alias python=python3

RUN git clone --depth 1 https://github.com/mininet/mininet.git && \
    cd mininet && ./util/install.sh && cd /

COPY . /mini-ndn

RUN cd mini-ndn && \
    pip3 install -r requirements.txt && \
    ./install.sh -y --ppa && cd /

RUN rm -rf /var/lib/apt/lists/*

COPY docker/ENTRYPOINT.sh /
RUN chmod +x ENTRYPOINT.sh

# Change the working directory to /mini-ndn
WORKDIR /mini-ndn

ENTRYPOINT ["/ENTRYPOINT.sh"]
