# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
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

from time import sleep
import subprocess

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

def trafficServer(node, serverConfFile):
    info ("Starting traffic server \n")
    # c = 10, i.e maximum number of Interests to respond
    cmd = 'ndn-traffic-server -c {} {} &> traffic-server.log &'.format(10, serverConfFile)
    node.cmd(cmd)
    sleep(10)

    # The server configuration file uses /example prefix to advertise its service
    #  thus, server needs to advertise this prefix for the client to reach it
    serverPrefix = "/example"
    server.cmd('nlsrc advertise {}'.format(serverPrefix))
    sleep(5) # sleep for routing convergence

def trafficClient(node, clientConfFile):
    info ("Starting ndn traffic client \n")
    # c = 10, total number of Interests to be generated each at 100ms interval
    cmd = 'ndn-traffic-client -c {} -i {} {} &>  traffic-client.log &'.format(10, 200, clientConfFile)
    node.cmd(cmd)

if __name__ == '__main__':
    setLogLevel('info')

    # Traffic generator configuration files. For this example, we are using default conf files.
    # More details on configuration files here: https://github.com/named-data/ndn-traffic-generator
    serverConfFile = "/etc/ndn/ndn-traffic-server.conf.sample"
    clientConfFile = "/etc/ndn/ndn-traffic-client.conf.sample"

    Minindn.cleanUp()
    Minindn.verifyDependencies()
    ndn = Minindn()
    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(90)

    #   Default topology is used in this experiment "/topologies/default-topology.conf"
    #   lets make node "a" as a traffic-server node, and node "c" as a traffic-client node
    server  = ndn.net['a']
    client = ndn.net['c']

    trafficServer(server, serverConfFile)
    trafficClient(client, clientConfFile)
    # default location for the results: /tmp/minindn/

    MiniNDNCLI(ndn.net)
    ndn.stop()