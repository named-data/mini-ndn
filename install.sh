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
#
# This file incorporates work covered by the following copyright and
# permission notice:
#
#   Mininet 2.3.0d1 License
#
#   Copyright (c) 2013-2016 Open Networking Laboratory
#   Copyright (c) 2009-2012 Bob Lantz and The Board of Trustees of
#   The Leland Stanford Junior University
#
#   Original authors: Bob Lantz and Brandon Heller
#
#   We are making Mininet available for public use and benefit with the
#   expectation that others will use, modify and enhance the Software and
#   contribute those enhancements back to the community. However, since we
#   would like to make the Software available for broadest use, with as few
#   restrictions as possible permission is hereby granted, free of charge, to
#   any person obtaining a copy of this Software to deal in the Software
#   under the copyrights without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#   The name and trademarks of copyright holder(s) may NOT be used in
#   advertising or publicity pertaining to the Software or any derivatives
#   without specific, written prior permission.

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
CHRONOSYNC_VERSION="master"
NLSR_VERSION="master"
NDN_TOOLS_VERSION="master"

if [ $SUDO_USER ]; then
    REAL_USER=$SUDO_USER
else
    REAL_USER=$(whoami)
fi

function patchDummy {
    git -C $NDN_SRC/ndn-cxx apply $(pwd)/patches/ndn-cxx-dummy-keychain-from-ndnsim.patch
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
        $install git libsqlite3-dev libboost-all-dev make g++ libssl-dev libpcap-dev pkg-config python-pip
    fi

    if [[ $DIST == Fedora ]]; then
        $install gcc-c++ sqlite-devel boost-devel openssl-devel libpcap-devel python-pip
    fi

    ndn_install ndn-cxx $NDN_CXX_VERSION
    ndn_install NFD $NFD_VERSION --without-websocket
    ndn_install PSync $PSYNC_VERSION --with-examples
    ndn_install ChronoSync $CHRONOSYNC_VERSION
    ndn_install NLSR $NLSR_VERSION
    ndn_install ndn-tools $NDN_TOOLS_VERSION
    infoedit
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
    sudo ./util/install.sh -nv
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
    sudo python setup.py develop
}

function ndn_cpp {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git build-essential libssl-dev libsqlite3-dev libboost-all-dev libprotobuf-dev protobuf-compiler
    fi

    if [[ $DIST == Fedora ]]; then
        printf '\nNDN-CPP does not support Fedora yet.\n'
        return
    fi

    git clone --depth 1 $NDN_GITHUB/ndn-cpp $NDN_SRC/ndn-cpp
    pushd $NDN_SRC/ndn-cpp
    ./configure
    proc=$(nproc)
    make -j$proc
    sudo make install
    sudo ldconfig
    popd
}

function pyNDN {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git build-essential libssl-dev libffi-dev python-dev python-pip
    fi

    if [[ $DIST == Fedora ]]; then
        printf '\nPyNDN does not support Fedora yet.\n'
        return
    fi

    sudo pip install cryptography trollius protobuf pytest mock
    git clone --depth 1 $NDN_GITHUB/PyNDN2 $NDN_SRC/PyNDN2
    pushd $NDN_SRC/PyNDN2
    # Update the user's PYTHONPATH.
    echo "export PYTHONPATH=\$PYTHONPATH:`pwd`/python" >> ~/.bashrc
    # Also update root's PYTHONPATH in case of running under sudo.
    echo "export PYTHONPATH=\$PYTHONPATH:`pwd`/python" | sudo tee -a /root/.bashrc > /dev/null
    popd
}

function ndn_js {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git nodejs npm
    fi

    if [[ $DIST == Fedora ]]; then
        printf '\nNDN-JS does not support Fedora yet.\n'
        return
    fi

    sudo ln -fs /usr/bin/nodejs /usr/bin/node
    sudo npm install -g mocha
    sudo npm install rsa-keygen sqlite3
    git clone --depth 1 $NDN_GITHUB/ndn-js $NDN_SRC/ndn-js
}

function jNDN {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git openjdk-8-jdk maven
    fi

    if [[ $DIST == Fedora ]]; then
        printf '\nNDN-JS does not support Fedora yet.\n'
        return
    fi

    git clone --depth 1 $NDN_GITHUB/jndn $NDN_SRC/jndn
    pushd $NDN_SRC/jndn
    mvn install
    popd
}

function commonClientLibraries {
    ndn_cpp
    pyNDN
    ndn_js
    jNDN
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
    printf -- ' -c: install Common Client Libraries\n' >&2
    printf -- ' -d: build documentation\n' >&2
    printf -- ' -h: print this (H)elp message\n' >&2
    printf -- ' -i: install mini-ndn\n' >&2
    printf -- ' -m: install mininet and dependencies\n' >&2
    printf -- ' -n: install NDN dependencies of mini-ndn including infoedit\n' >&2
    printf -- ' -p: patch ndn-cxx with dummy key chain\n' >&2
    printf -- ' -q: quiet install (must be specified first)\n' >&2
    exit 2
}

if [[ $# -eq 0 ]]; then
    usage
else
    while getopts 'acdhimnpq' OPTION
    do
        case $OPTION in
        a)
        ndn
        mininet
        minindn
        commonClientLibraries
        break
        ;;
        c)    commonClientLibraries;;
        d)    buildDocumentation;;
        h)    usage;;
        i)    minindn;;
        m)    mininet;;
        n)    ndn;;
        p)    patchDummy;;
        q)    quiet_install;;
        ?)    usage;;
        esac
    done
    shift $(($OPTIND - 1))
fi
