#!/bin/bash

test -e /etc/debian_version && DIST="Debian"
grep Ubuntu /etc/lsb-release &> /dev/null && DIST="Ubuntu"

if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
    update='sudo apt-get update'
    install='sudo apt-get -y install'
    remove='sudo apt-get -y remove'
    pkginst='sudo dpkg -i'
    # Prereqs for this script
    if ! which lsb_release &> /dev/null; then
        $install lsb-release
    fi
fi

test -e /etc/fedora-release && DIST="Fedora"
if [[ $DIST == Fedora ]]; then
    update='sudo yum update'
    install='sudo yum -y install'
    remove='sudo yum -y erase'
    pkginst='sudo rpm -ivh'
    # Prereqs for this script
    if ! which lsb_release &> /dev/null; then
        $install redhat-lsb-core
    fi
fi

function forwarder {
    if [[ $cxx != true ]]; then
        ndncxx
        cxx="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install libpcap-dev pkg-config
    fi

    if [[ $DIST == Fedora ]]; then
        $install libpcap-devel
    fi

    git clone --depth 1 https://github.com/named-data/NFD
    cd NFD
    ./waf configure --without-websocket
    ./waf
    sudo ./waf install
    cd ../
}

function routing {
    if [[ $cxx != true ]]; then
        ndncxx
        cxx="true"
    fi

    if [[ $DIST == Ubuntu ]]; then
        $install liblog4cxx10-dev libprotobuf-dev protobuf-compiler
    fi

    if [[ $DIST == Fedora ]]; then
        $install log4cxx log4cxx-devel openssl-devel protobuf-devel
    fi

    git clone --depth 1 https://github.com/named-data/NLSR
    cd NLSR
    ./waf configure
    ./waf
    sudo ./waf install
    cd ../
}

function ndncxx {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git libsqlite3-dev libboost-all-dev make g++
        crypto
    fi

    if [[ $DIST == Fedora ]]; then
        $install gcc-c++ sqlite-devel boost-devel
    fi

    git clone --depth 1 https://github.com/named-data/ndn-cxx
    cd ndn-cxx
    ./waf configure
    ./waf
    sudo ./waf install
    cd ../
}

function crypto {
    mkdir crypto
    cd crypto
    $install unzip
    wget http://www.cryptopp.com/cryptopp562.zip
    unzip cryptopp562.zip
    make
    sudo make install
    cd ../
}

function tools {
    if [[ $cxx != true ]]; then
        ndncxx
        cxx="true"
    fi

    git clone --depth 1 https://github.com/named-data/ndn-tools
    cd ndn-tools
    ./waf configure
    ./waf
    sudo ./waf install
    cd ../
}

function mininet {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $pysetup != true ]]; then
        pysetup="true"
    fi

    git clone --depth 1 https://github.com/mininet/mininet
    cd mininet
    sudo ./util/install.sh -fnv
    cd ../
}

function minindn {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $pysetup != true ]]; then
        $install python-setuptools
        pysetup="true"
    fi
    sudo mkdir -p /usr/local/etc/mini-ndn/
    sudo cp ndn_utils/client.conf.sample /usr/local/etc/mini-ndn/
    sudo cp ndn_utils/nfd.conf /usr/local/etc/mini-ndn/
    sudo cp ndn_utils/nlsr.conf /usr/local/etc/mini-ndn/
    sudo python setup.py install
}


function usage {
    printf '\nUsage: %s [-mfrti]\n\n' $(basename $0) >&2

    printf 'options:\n' >&2
    printf -- ' -f: install NFD\n' >&2
    printf -- ' -i: install mini-ndn\n' >&2
    printf -- ' -m: install mininet and dependencies\n' >&2
    printf -- ' -r: install NLSR\n' >&2
    printf -- ' -t: install tools\n' >&2
    exit 2
}

if [[ $# -eq 0 ]]; then
    usage
else
    while getopts 'mfrti' OPTION
    do
        case $OPTION in
        f)    forwarder;;
        i)    minindn;;
        m)    mininet;;
        r)    routing;;
        t)    tools;;
        ?)    usage;;
        esac
    done
    shift $(($OPTIND - 1))
fi
