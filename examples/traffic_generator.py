# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2021, The University of Memphis,
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


"""
This example demonstrates the functionality of the Traffic generator. It consists of a traffic
server and client. The server will listen for interest on the prefix specified in the server
configuration file. The client will send a designated number of interests to the server and
get the data back.
More details on traffic generator here: https://github.com/named-data/ndn-traffic-generator
"""

from time import sleep

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.util import copyExistentFile
from examples.nlsr.nlsr_common import getParser

def trafficServer(node, serverConfFile):
    """
    Start traffic server
     :parma mininet.node.Host node: mininet node object
     :param string serverConfFile: server configuration file
    """
    info ("Starting traffic server \n")
    # c = 10, i.e maximum number of Interests to respond
    cmd = 'ndn-traffic-server -c {} {} &> traffic-server.log &'.format(10, serverConfFile)
    node.cmd(cmd)
    sleep(10)

    # The server configuration file uses /example prefix to advertise its service
    # thus, server needs to advertise this prefix for the client to reach it
    serverPrefix = "/example"
    server.cmd('nlsrc advertise {}'.format(serverPrefix))
    sleep(5) # sleep for routing convergence

def trafficClient(node, clientConfFile):
    """
    Start traffic client
     :parma mininet.node.Host node: The expiration period in milliseconds, or None if not specified.
     :param string clientConfFile: client configuration file
    """
    info ("Starting ndn traffic client \n")
    # c = 10, total number of Interests to be generated each at 200ms interval
    cmd = 'ndn-traffic-client -c {} -i {} {} &>  traffic-client.log &'.format(10, 200, clientConfFile)
    node.cmd(cmd)

if __name__ == '__main__':
    setLogLevel('info')

    # Traffic generator configuration files. For this example, we are using default conf files.
    # More details on configuration files here: https://github.com/named-data/ndn-traffic-generator
    possibleServerConfPath = ["/etc/ndn/ndn-traffic-server.conf.sample", "/usr/local/etc/ndn/ndn-traffic-server.conf.sample"]
    possibleClientConfPath = ["/etc/ndn/ndn-traffic-client.conf.sample", "/usr/local/etc/ndn/ndn-traffic-client.conf.sample"]

    Minindn.cleanUp()
    Minindn.verifyDependencies()
    ndn = Minindn(parser=getParser())
    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(90)

    # Default topology is used in this experiment "/topologies/default-topology.conf"
    # lets make node "a" as a traffic-server node, and node "c" as a traffic-client node
    server  = ndn.net['a']
    client = ndn.net['c']
    serverConf = '{}/{}/server-conf'.format(ndn.workDir, server.name)
    clientConf = '{}/{}/client-conf'.format(ndn.workDir, client.name)

    copyExistentFile(server, possibleServerConfPath, serverConf)
    copyExistentFile(server, possibleClientConfPath, clientConf)

    trafficServer(server, serverConf)
    trafficClient(client, clientConf)
    # default location for the results: /tmp/minindn/

    MiniNDNCLI(ndn.net)
    ndn.stop()
