# syntax=docker/dockerfile:1

FROM ubuntu:22.04

# Install dependencies
RUN <<EOF
    set -eux
    apt-get update -y
    apt-get install --no-install-recommends -y \
        lsb-release sudo \
        zip unzip wget git ca-certificates \
        curl iproute2 iputils-ping net-tools \
        python3 python3-pip python-is-python3 \
        tcpdump vim x11-xserver-utils xterm
    rm -rf /var/lib/apt/lists/*
    update-ca-certificates
EOF

COPY . /mini-ndn
WORKDIR /mini-ndn

RUN <<EOF
    set -eux
    pip3 install -r requirements.txt
    ./install.sh -y --source
    make -C dl/mininet install
    make -C dl/mininet-wifi install
    rm -rf dl /var/lib/apt/lists/*
EOF

# Expose ports for openvswitch-switch
EXPOSE 6633 6653 6640

ENTRYPOINT ["docker/entrypoint.sh"]
