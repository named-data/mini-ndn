#!/bin/bash
# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
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

    git clone https://github.com/named-data/NFD
    cd NFD
    current=$(git rev-parse HEAD)
    if [[ $current != "f4056d0242536f85b7d7b4de1b5ac50dad65c233" ]]; then
      git checkout f4056d0242536f85b7d7b4de1b5ac50dad65c233
      git checkout -b fix-commit
    fi
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
        $install liblog4cxx10-dev
    fi

    if [[ $DIST == Fedora ]]; then
        $install log4cxx log4cxx-devel openssl-devel
    fi

    git clone --depth 1 https://github.com/named-data/ChronoSync
    cd ChronoSync
    ./waf configure
    ./waf
    sudo ./waf install
    cd ../

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
        $install git libsqlite3-dev libboost-all-dev make g++ libssl-dev libcrypto++-dev
    fi

    if [[ $DIST == Fedora ]]; then
        $install gcc-c++ sqlite-devel boost-devel openssl-devel cryptopp-devel
    fi

    git clone https://github.com/named-data/ndn-cxx
    cd ndn-cxx
    current=$(git rev-parse HEAD)
    if [[ $current != "b555b00c280b9c9ed46f24a1fbebc73b720601af" ]]; then
      git checkout b555b00c280b9c9ed46f24a1fbebc73b720601af
      git checkout -b fix-commit
    fi
    ./waf configure
    ./waf
    sudo ./waf install
    sudo ldconfig
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
    sudo cp ndn_utils/client.conf.sample "$install_dir"
    sudo cp ndn_utils/topologies/default-topology.conf "$install_dir"
    sudo cp ndn_utils/topologies/minindn.caida.conf "$install_dir"
    sudo cp ndn_utils/topologies/minindn.ucla.conf "$install_dir"
    sudo cp ndn_utils/topologies/minindn.testbed.conf "$install_dir"
    sudo cp ndn_utils/topologies/adhoc-topology.conf "$install_dir"
    sudo python setup.py clean --all install
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
