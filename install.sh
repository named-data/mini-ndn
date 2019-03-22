#!/bin/bash
# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2018, The University of Memphis,
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

    git clone --depth 1 https://github.com/named-data/NFD
    cd NFD
    ./waf configure --without-websocket
    ./waf
    sudo ./waf install
    cd ../
    sudo rm -rf NFD
}

function routing {
    if [[ $cxx != true ]]; then
        ndncxx
        cxx="true"
    fi

    git clone --depth 1 https://github.com/named-data/PSync
    cd PSync
    ./waf configure
    ./waf
    sudo ./waf install
    sudo ldconfig
    cd ../

    git clone --depth 1 https://github.com/named-data/ChronoSync
    cd ChronoSync
    current=$(git rev-parse HEAD)
    if [[ $current != "097bb448f46b8bd9a5c1f431e824f8f6a169b650" ]]; then
      git checkout 097bb448f46b8bd9a5c1f431e824f8f6a169b650
      git checkout -b fix-commit
    fi
    ./waf configure
    ./waf
    sudo ./waf install
    sudo ldconfig
    cd ../
    sudo rm -rf ChronoSync

    git clone --depth 1 https://github.com/named-data/NLSR
    cd NLSR
    ./waf configure
    ./waf
    sudo ./waf install
    cd ../
    sudo rm -rf NLSR
}

function ndncxx {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $DIST == Ubuntu || $DIST == Debian ]]; then
        $install git libsqlite3-dev libboost-all-dev make g++ libssl-dev
    fi

    if [[ $DIST == Fedora ]]; then
        $install gcc-c++ sqlite-devel boost-devel openssl-devel
    fi

    git clone --depth 1 https://github.com/named-data/ndn-cxx
    cd ndn-cxx
    ./waf configure
    ./waf
    sudo ./waf install
    sudo ldconfig
    cd ../
    sudo rm -rf ndn-cxx
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
    sudo rm -rf ndn-tools
}


# mininetwifi function for install mininetwifi moudul
function mininetwifi {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $pysetup != true ]]; then
        pysetup="true"
    fi

    git clone --depth 1 https://github.com/intrig-unicamp/mininet-wifi
    cd mininet-wifi
    sudo ./util/install.sh -Wnfvl
    cd ../
    sudo rm -rf mininet-wifi
}

function infoedit {
    git clone --depth 1 https://github.com/NDN-Routing/infoedit.git
    cd infoedit
    sudo make install
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
    git clone --depth 1 https://github.com/named-data/mini-ndn
    sudo mv mini-ndn mini_ndn # name mini-ndn is not allowed in python 
    cd mini_ndn
    sudo cp ../ndnwifi/experiments/__init__.py ./ #inorder to import module in the subdirecorty mini_ndn
    sudo ./install.sh -i
    cd ../
    #sudo rm -rf mini_ndn
}

function minindnwifi {
    if [[ updated != true ]]; then
        $update
        updated="true"
    fi

    if [[ $pysetup != true ]]; then
        pysetup="true"
    fi
    install_dir="/usr/local/etc/mini-ndn/wifi/"
    sudo mkdir -p "$install_dir"
    sudo cp ndnwifi_utils/topologies/adhoc-topology.conf "$install_dir"
    sudo cp ndnwifi_utils/topologies/singleap-topology.conf "$install_dir"
    sudo cp ndnwifi_utils/topologies/multiap-topology.conf "$install_dir"
    sudo cp ndnwifi_utils/topologies/vndn-topology.conf "$install_dir"
    sudo cp topologies/default-topology.conf "$install_dir"
    sudo cp topologies/minindn.caida.conf "$install_dir"
    sudo cp topologies/minindn.ucla.conf "$install_dir"
    sudo cp topologies/minindn.testbed.conf "$install_dir"
    sudo cp topologies/current-testbed.conf "$install_dir"
    sudo python setup.py clean --all install
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

    git clone --depth 1 https://github.com/named-data/ndn-cpp
    cd ndn-cpp
    ./configure
    proc=$(nproc)
    make -j$proc
    sudo make install
    sudo ldconfig
    cd ..
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
    git clone --depth 1 https://github.com/named-data/PyNDN2
    cd PyNDN2
    # Update the user's PYTHONPATH.
    echo "export PYTHONPATH=\$PYTHONPATH:`pwd`/python" >> ~/.bashrc
    # Also update root's PYTHONPATH in case of running under sudo.
    echo "export PYTHONPATH=\$PYTHONPATH:`pwd`/python" | sudo tee -a /root/.bashrc > /dev/null
    cd ..
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
    git clone --depth 1 https://github.com/named-data/ndn-js
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

    git clone --depth 1 https://github.com/named-data/jndn
    cd jndn
    mvn install
    cd ..
}

function argcomplete {
    if [[ $SHELL == "/bin/bash" ]]; then
        $install bash-completion
        $install python-argcomplete
        if ! grep -q 'eval "$(register-python-argcomplete minindn)"' ~/.bashrc; then
            echo 'eval "$(register-python-argcomplete minindn)"' >> ~/.bashrc
        fi
        source ~/.bashrc
    elif [[ $SHELL == "/bin/zsh" ]] || [[ $SHELL == "/usr/bin/zsh" ]]; then
        $install bash-completion
        $install python-argcomplete
        if ! grep -z -q 'autoload bashcompinit\sbashcompinit\seval "$(register-python-argcomplete minindn)"' ~/.zshrc; then
            echo -e 'autoload bashcompinit\nbashcompinit\neval "$(register-python-argcomplete minindn)"' >> ~/.zshrc
        fi
        source ~/.zshrc
    else
        echo "Skipping argomplete install..."
    fi
}

function commonClientLibraries {
    ndn_cpp
    pyNDN
    ndn_js
    jNDN
}

function usage {
    printf '\nUsage: %s [-a]\n\n' $(basename $0) >&2

    printf 'options:\n' >&2
    printf -- ' -a: install all the required dependencies\n' >&2
    printf -- ' -b: install autocomplete for Bash and Zsh users\n' >&2
    printf -- ' -e: install infoedit\n' >&2
    printf -- ' -f: install NFD\n' >&2
    printf -- ' -i: install mini-ndn\n' >&2
    printf -- ' -m: install mininet and dependencies\n' >&2
    printf -- ' -r: install NLSR\n' >&2
    printf -- ' -t: install tools\n' >&2
    printf -- ' -c: install Common Client Libraries\n' >&2
    printf -- ' -w: install minindn-wifi' >&2
    exit 2
}

if [[ $# -eq 0 ]]; then
    usage
else
    while getopts 'abemfrticw' OPTION
    do
        case $OPTION in
        a)
        forwarder
        mininet-wifi
        routing
        tools
        infoedit
        argcomplete
        commonClientLibraries
        minindnwifi
        break
        ;;
        b)    argcomplete;;
        e)    infoedit;;
        f)    forwarder;;
        i)    minindn;;
        m)    mininet-wifi;;
        r)    routing;;
        t)    tools;;
        c)    commonClientLibraries;;
        w)    minindnwifi;;
        ?)    usage;;
        esac
    done
    shift $(($OPTIND - 1))
fi
