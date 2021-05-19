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

from mininet.log import setLogLevel, info
from mn_wifi.topo import Topo
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
from time import sleep
# This experiment uses the singleap topology and is intended to be a basic
# test case where we see if two nodes can send interests to each other.
# This topology can be replicated in other wifi experiments using the
# provided singleap-topology.conf. 
def runExperiment():
    setLogLevel('info')

    info("Starting network")
    topo = Topo()
    sta1 = topo.addStation("sta1", range=150, speed=5)
    sta2 = topo.addStation("sta2", range=200)
    ap1 = topo.addAccessPoint("ap1", position="150,150,0", range=150)
    topo.addLink(sta1, ap1, delay="10ms")
    topo.addLink(sta2, ap1, delay="10ms")
    ndnwifi = MinindnWifi(topo=topo)
    a = ndnwifi.net["sta1"]
    b = ndnwifi.net["sta2"]
    # Test for model-based mobility
    if ndnwifi.args.modelMob:
        ndnwifi.startMobilityModel(model='GaussMarkov')
    #Test for replay based mobility
    if ndnwifi.args.mobility:
        info("Running with mobility...")

        p1, p2, p3, p4 = dict(), dict(), dict(), dict()
        p1 = {'position': '150.0,150.0,0.0'}
        p2 = {'position': '140.0,130.0,0.0'}

        p3 = {'position': '250.0,250.0,0.0'}
        p4 = {'position': '301.0,301.0,0.0'}

        ndnwifi.net.mobility(a, 'start', time=1, **p1)
        ndnwifi.net.mobility(a, 'stop', time=12, **p3)
        ndnwifi.net.mobility(b, 'start', time=2, **p2)
        ndnwifi.net.mobility(b, 'stop', time=22, **p4)
        ndnwifi.net.stopMobility(time=23)
        ndnwifi.startMobility(time=0, mob_rep=1, reverse=False)

    ndnwifi.start()
    info("Starting NFD")
    sleep(2)
    nfds = AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    info("Starting pingserver...")
    ping_server_proc = getPopen(b, "ndnpingserver /example")
    Nfdc.createFace(a, b.IP())
    Nfdc.registerRoute(a, "/example", b.IP())

    info("Starting ping...")
    NDNPingClient.ping(a, "/example", 10)

    # Start the CLI
    MiniNDNWifiCLI(ndnwifi.net)
    ndnwifi.net.stop()
    ndnwifi.cleanUp()

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnWifi.handleException()