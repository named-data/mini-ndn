# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2024, The University of Memphis,
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
from time import sleep

from mininet.log import setLogLevel, info, debug
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc, NfdcBatch

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
    topo.addLink(a, c, delay='10ms', bw=10)

    ndn = Minindn(topo=topo)
    ndn.start()

    # configure and start nfd on each node
    info("Configuring NFD\n")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")

    info("Setting up routes and strategies...\n")
    links = {"a": ["b", "c"], "b": ["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_ip = interface.IP()
            # Nfdc.createFace(host1, interface_ip)
            Nfdc.createFace(host1, interface_ip)
            Nfdc.registerRoute(host1, PREFIX, interface_ip, cost=0)
            Nfdc.setStrategy(host1, PREFIX, Nfdc.STRATEGY_ASF)
    info(ndn.net["a"].cmd("nfdc face list"))
    info(ndn.net["a"].cmd("nfdc fib list"))
    info(ndn.net["a"].cmd("nfdc strategy show /example"))

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open(f"{ndn.workDir}/c/ndnpingserver.log", "w")
    getPopen(ndn.net["c"], f"ndnpingserver {PREFIX}", stdout=pingserver_log,
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], f"ndnping {PREFIX} -c 5", stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    info("Bringing down routes and strategies...\n")
    links = {"a": ["b", "c"], "b": ["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_ip = interface.IP()
            Nfdc.unregisterRoute(host1, PREFIX, interface_ip)
            Nfdc.destroyFace(host1, interface_ip)
            Nfdc.unsetStrategy(host1, PREFIX)
    info(ndn.net["a"].cmd("nfdc face list"))
    info(ndn.net["a"].cmd("nfdc fib list"))
    info(ndn.net["a"].cmd("nfdc strategy show /example"))

    ping2 = getPopen(ndn.net["a"], f"ndnping {PREFIX} -c 5", stdout=PIPE, stderr=PIPE)
    ping2.wait()
    printOutput(ping2.stdout.read())

    info("\nExperiment Completed!\n")
    # MiniNDNCLI(ndn.net)
    ndn.stop()

if __name__ == '__main__':
    setLogLevel("info")
    run()