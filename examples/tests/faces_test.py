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
from time import sleep

from mininet.log import setLogLevel, info, debug
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.experiment import Experiment
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper

PREFIX = "/example"

def printOutput(output):
    _out = output.decode("utf-8").split("\n")
    for _line in _out:
        info(_line + "\n")

def udp_run():
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

    """
    There are multiple ways of setting up routes in Mini-NDN
    refer: https://minindn.memphis.edu/experiment.html#routing-options
    It can also be set manually as follows. The important bit to note here
    is the use of the Nfdc command
    """
    links = {"a":["b", "c"], "b":["c"]}
    nfdc_batches = dict()
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_ip = interface.IP()
            Nfdc.createFace(host1, interface_ip)
            Nfdc.registerRoute(host1, PREFIX, interface_ip, cost=0)
            Nfdc.setStrategy(host1, PREFIX, Nfdc.STRATEGY_ASF)
    sleep(1) 
    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open("{}/c/ndnpingserver.log".format(ndn.workDir), "w")
    getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log,\
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    links = {"a":["b", "c"], "b":["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_ip = interface.IP()
            Nfdc.unregisterRoute(host1, PREFIX, interface_ip)
            Nfdc.destroyFace(host1, interface_ip)
            Nfdc.unsetStrategy(host1, PREFIX)
    sleep(1)
    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    ping2 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping2.wait()
    printOutput(ping2.stdout.read())

    info("\nExperiment Completed!\n")
    # MiniNDNCLI(ndn.net)
    ndn.stop()

def eth_run():
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

    """
    There are multiple ways of setting up routes in Mini-NDN
    refer: https://minindn.memphis.edu/experiment.html#routing-options
    It can also be set manually as follows. The important bit to note here
    is the use of the Nfdc command
    """
    links = {"a":["b", "c"], "b":["c"]}
    nfdc_batches = dict()
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            sender_interface = host1.connectionsTo(host2)[0][0]
            interface = host2.connectionsTo(host1)[0][0]
            interface_addr = interface.MAC()
            Nfdc.createFace(host1, interface_addr, protocol=Nfdc.PROTOCOL_ETHER, localInterface=sender_interface)
            Nfdc.registerRoute(host1, PREFIX, interface_addr, cost=0, protocol=Nfdc.PROTOCOL_ETHER)
            Nfdc.setStrategy(host1, PREFIX, Nfdc.STRATEGY_ASF)
    sleep(1) 
    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open("{}/c/ndnpingserver.log".format(ndn.workDir), "w")
    getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log,\
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    links = {"a":["b", "c"], "b":["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            interface_addr = interface.MAC()
            Nfdc.unregisterRoute(host1, PREFIX, interface_addr, protocol=Nfdc.PROTOCOL_ETHER)
            Nfdc.destroyFace(host1, interface_addr, protocol=Nfdc.PROTOCOL_ETHER)
            Nfdc.unsetStrategy(host1, PREFIX)
    sleep(1)
    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    ping2 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping2.wait()
    printOutput(ping2.stdout.read())

    info("\nExperiment Completed!\n")
    # MiniNDNCLI(ndn.net)
    ndn.stop()

def udp_nlsr_run():
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

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, faceType=Nfdc.PROTOCOL_UDP,
                       logLevel='ndn.*=TRACE:nlsr.*=TRACE')

    Experiment.checkConvergence(ndn, ndn.net.hosts, 60, quit=False)

    Experiment.setupPing(ndn.net.hosts, Nfdc.STRATEGY_BEST_ROUTE)
    Experiment.startPctPings(ndn.net, 60)

    sleep(70)

    ndn.stop()

def eth_nlsr_run():
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

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, faceType=Nfdc.PROTOCOL_ETHER,
                       logLevel='ndn.*=TRACE:nlsr.*=TRACE')

    Experiment.checkConvergence(ndn, ndn.net.hosts, 60, quit=False)

    Experiment.setupPing(ndn.net.hosts, Nfdc.STRATEGY_BEST_ROUTE)
    Experiment.startPctPings(ndn.net, 60)

    sleep(70)

    ndn.stop()

def udp_static_run():
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

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    info('Adding static routes to NFD\n')
    grh = NdnRoutingHelper(ndn.net, Nfdc.PROTOCOL_UDP)
    # For all host, pass ndn.net.hosts or a list, [ndn.net['a'], ..] or [ndn.net.hosts[0],.]
    grh.addOrigin([ndn.net['c']], ["/example"])
    grh.calculateNPossibleRoutes()

    '''
    prefix "/abc" is advertise from node A, it should be reachable from all other nodes.
    '''
    routesFromA = ndn.net['a'].cmd("nfdc route | grep -v '/localhost/nfd'")
    if '/ndn/b-site/b' not in routesFromA or '/ndn/c-site/c' not in routesFromA:
        info("Route addition failed\n")

    routesToPrefix = ndn.net['b'].cmd("nfdc fib | grep '/example'")
    if '/example' not in routesToPrefix:
        info("Missing route to advertised prefix, Route addition failed\n")
        ndn.net.stop()

    info('Route addition to NFD completed succesfully\n')

    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open("{}/c/ndnpingserver.log".format(ndn.workDir), "w")
    getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log,\
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    ndn.stop()

def eth_static_run():
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

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    info('Adding static routes to NFD\n')
    grh = NdnRoutingHelper(ndn.net, Nfdc.PROTOCOL_ETHER)
    # For all host, pass ndn.net.hosts or a list, [ndn.net['a'], ..] or [ndn.net.hosts[0],.]
    grh.addOrigin([ndn.net['c']], ["/example"])
    grh.calculateNPossibleRoutes()

    '''
    prefix "/abc" is advertise from node A, it should be reachable from all other nodes.
    '''
    routesFromA = ndn.net['a'].cmd("nfdc route | grep -v '/localhost/nfd'")
    if '/ndn/b-site/b' not in routesFromA or '/ndn/c-site/c' not in routesFromA:
        info("Route addition failed\n")

    routesToPrefix = ndn.net['b'].cmd("nfdc fib | grep '/example'")
    if '/example' not in routesToPrefix:
        info("Missing route to advertised prefix, Route addition failed\n")
        ndn.net.stop()

    info('Route addition to NFD completed succesfully\n')

    debug(ndn.net["a"].cmd("nfdc face list"))
    debug(ndn.net["a"].cmd("nfdc fib list"))
    debug(ndn.net["a"].cmd("nfdc strategy show /example"))

    # Start ping server
    info("Starting pings...\n")
    pingserver_log = open("{}/c/ndnpingserver.log".format(ndn.workDir), "w")
    getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log,\
             stderr=pingserver_log)

    # start ping client
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    printOutput(ping1.stdout.read())

    ndn.stop()

if __name__ == '__main__':
    setLogLevel("debug")
    udp_run()
    eth_run()
    udp_nlsr_run()
    eth_nlsr_run()
    udp_static_run()
    eth_static_run()