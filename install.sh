#!/bin/bash
# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2020, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

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

NDN_SRC="ndn-src"

NDN_GITHUB="https://github.com/named-data"

NDN_CXX_VERSION="master"
NFD_VERSION="master"
PSYNC_VERSION="master"
NLSR_VERSION="master"
NDN_TOOLS_VERSION="master"
NDN_TRAFFIC_GENERATOR="master"

if [ $SUDO_USER ]; then
    REAL_USER=$SUDO_USER
else
    REAL_USER=$(whoami)
fi

function patchDummy {
    git -C $NDN_SRC/ndn-cxx apply $(pwd)/util/patches/ndn-cxx-dummy-keychain-from-ndnsim.patch
    if [[ "$?" -ne 0 ]]; then
        echo "Patch might already be applied"
    fi
}

function quiet_install {
    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        update='sudo DEBIAN_FRONTEND=noninteractive apt-get update'
        install='sudo DEBIAN_FRONTEND=noninteractive apt-get -y install'
        remove='sudo DEBIAN_FRONTEND=noninteractive apt-get -y remove'

        echo "wireshark-common wireshark-common/install-setuid boolean false" | sudo debconf-set-selections
    fi
}

function ndn_install {
    mkdir -p $NDN_SRC
    name=$1
    version=$2
    wafOptions=$3

    if [[ $version == "master" ]]; then
        if [[ -d "$NDN_SRC/$name" ]]; then
            pushd $NDN_SRC/$name
            git checkout master
        else
            git clone --depth 1 $NDN_GITHUB/$name $NDN_SRC/$name
            pushd $NDN_SRC/$name
        fi
    else
        if [[ -d $NDN_SRC/$name ]]; then
            pushd $NDN_SRC/$name
            if [[ $(git rev-parse --is-shallow-repository) == "true" ]]; then
                git fetch --unshallow
                git fetch --all
            fi
        else
            git clone $NDN_GITHUB/$name $NDN_SRC/$name
            pushd $NDN_SRC/$name
        fi
        git checkout $version -b version-$version || git checkout version-$version
    fi

    # User must use the same python version as root to use ./waf outside of this script
    sudo -E -u $REAL_USER ./waf configure $wafOptions
    sudo -E -u $REAL_USER ./waf && sudo ./waf install && sudo ldconfig
    popd
}

function ndn {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install libsqlite3-dev libboost-all-dev make g++ libssl-dev libpcap-dev libsystemd-dev pkg-config python3-pip
    fi

    if [[ $DIST == Fedora ]]; then
        $install gcc-c++ sqlite-devel boost-devel openssl-devel libpcap-devel systemd-devel python3-pip
    fi

    ndn_install ndn-cxx $NDN_CXX_VERSION
    ndn_install NFD $NFD_VERSION --without-websocket
    ndn_install PSync $PSYNC_VERSION --with-examples
    ndn_install NLSR $NLSR_VERSION
    ndn_install ndn-tools $NDN_TOOLS_VERSION
    ndn_install ndn-traffic-generator $NDN_TRAFFIC_GENERATOR
    infoedit
}

function ndn-ppa {
    if [[ $DIST == Ubuntu ]]; then
        $update
        $install libsqlite3-dev libboost-all-dev make g++ libssl-dev libpcap-dev libsystemd-dev pkg-config python3-pip

        $install software-properties-common
        sudo add-apt-repository ppa:named-data/ppa
        $update
        $install ndn-cxx nfd libpsync nlsr ndn-tools ndn-traffic-generator
        infoedit
    else
        ndn
    fi
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
    pushd mininet
    sudo PYTHON=python3 ./util/install.sh -nv
    popd
}

function wifi {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $pysetup != true ]]; then
        pysetup="true"
    fi

    git clone --depth 1 https://github.com/intrig-unicamp/mininet-wifi.git
    pushd mininet-wifi
    sudo PYTHON=python3 ./util/install.sh -Wlfnv
    popd
}

function infoedit {
    git clone --depth 1 https://github.com/NDN-Routing/infoedit.git $NDN_SRC/infoedit
    pushd $NDN_SRC/infoedit
    rm infoedit
    sudo make install
    popd
}

function minindn {
    $install libigraph0-dev tshark
    sudo pip install -r requirements.txt

    if [[ updated != true ]]; then
        if [ ! -d "build" ]; then
            $update
            updated="true"
        fi
    fi

    if [[ $pysetup != true ]]; then
        $install python-setuptools
        pysetup="true"
    fi
    install_dir="/usr/local/etc/mini-ndn/"

    sudo mkdir -p "$install_dir"
    sudo cp topologies/default-topology.conf "$install_dir"
    sudo cp topologies/minindn.caida.conf "$install_dir"
    sudo cp topologies/minindn.ucla.conf "$install_dir"
    sudo cp topologies/minindn.testbed.conf "$install_dir"
    sudo cp topologies/current-testbed.conf "$install_dir"
    sudo cp topologies/geo_hyperbolic_test.conf "$install_dir"
    sudo cp topologies/geant.conf "$install_dir"
    sudo cp topologies/wifi/singleap-topology.conf "$install_dir"
    sudo python3 setup.py develop
}

function buildDocumentation {
    sphinxInstalled=$(pip show sphinx | wc -l)
    sphinxRtdInstalled=$(pip show sphinx_rtd_theme | wc -l)
    if [[ $sphinxInstalled -eq "0" ]]; then
        pip install sphinx
    fi

    if [[ $sphinxRtdInstalled -eq "0" ]]; then
        pip install sphinx_rtd_theme
    fi
    cd docs
    make clean
    make html
}

function usage {
    printf '\nUsage: %s [-a]\n\n' $(basename $0) >&2

    printf 'options:\n' >&2
    printf -- ' -a: install all the required dependencies\n' >&2
    printf -- ' -A: install all the required dependencies (wired only)\n' >&2
    printf -- ' -d: build documentation\n' >&2
    printf -- ' -h: print this (H)elp message\n' >&2
    printf -- ' -i: install mini-ndn\n' >&2
    printf -- ' -m: install mininet and dependencies (for wired-only installation)\n' >&2
    printf -- ' -n: install NDN dependencies including infoedit\n' >&2
    printf -- ' -N: install NDN dependencies from PPA including infoedit\n' >&2 
    printf -- ' -p: patch ndn-cxx with dummy key chain\n' >&2
    printf -- ' -q: quiet install (must be specified first)\n' >&2
    printf -- ' -w: install mininet-wifi and dependencies\n' >&2
    exit 2
}

if [[ $# -eq 0 ]]; then
    usage
else
    while getopts 'aAdhimnNpqw' OPTION
    do
        case $OPTION in
        a)
        ndn-ppa
        wifi
        minindn
        break
        ;;
        A)
        ndn-ppa
        mininet
        minindn
        break
        ;;
        d)    buildDocumentation;;
        h)    usage;;
        i)    minindn;;
        m)    mininet;;
        n)    ndn;;
        N)    ndn-ppa;;
        p)    patchDummy;;
        q)    quiet_install;;
        w)    wifi ;;
        ?)    usage;;
        esac
    done
    shift $(($OPTIND - 1))
fi
