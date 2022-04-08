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

from subprocess import PIPE

from mininet.log import setLogLevel, info
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc

PREFIX = "/example"

def printOutput(output):
    _out = output.decode("utf-8").split("\n")
    for _line in _out:
        info(_line + "\n")

def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    # Topology can be created/modified using Mininet topo object
    topo = Topo()
    info("Setup\n")
    # add hosts
    a = topo.addHost('a')
    b = topo.addHost('b')
    c = topo.addHost('c')

    # add links
    topo.addLink(a, b, delay='10ms', bw=10) # bw = bandwidth
    topo.addLink(b, c, delay='10ms', bw=10)

    ndn = Minindn(topo=topo)
    ndn.start()

    # configure and start nfd on each node
    info("Configuring NFD\n")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")

    """
    There are multiple ways of setting up routes in Mini-NDN
    refer: https://minindn.memphis.edu/experiment.html#routing-options
    It can also be set manually as follows. The important bit to note here
    is the use of the Nfdc command
    """
    links = {"a":["b"], "b":["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_ip = interface.IP()
            Nfdc.createFace(host1, interface_ip)
            Nfdc.registerRoute(host1, PREFIX, interface_ip, cost=0)

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open("{}/c/ndnpingserver.log".format(ndn.workDir), "w")
    getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log,\
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    interface = ndn.net["b"].connectionsTo(ndn.net["a"])[0][0]
    info("Failing link\n") # failing link by setting link loss to 100%
    interface.config(delay="10ms", bw=10, loss=100)
    info ("\n starting ping2 client \n")

    ping2 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping2.wait()
    printOutput(ping2.stdout.read())

    interface.config(delay="10ms", bw=10, loss=0) # bringing back the link

    info("\nExperiment Completed!\n")
    MiniNDNCLI(ndn.net)
    ndn.stop()

if __name__ == '__main__':
    setLogLevel("info")
    run()