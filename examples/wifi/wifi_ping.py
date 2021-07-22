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

from mininet.log import setLogLevel, info
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnping import NDNPing
from time import sleep
# This experiment uses the singleap topology and is intended to be a basic
# test case where we see if two nodes can send interests to each other.
def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndnwifi = MinindnWifi()
    a = ndnwifi.net["sta1"]
    b = ndnwifi.net["sta2"]
    # Test for model-based mobility
    if ndnwifi.args.modelMob:
        ndnwifi.startMobilityModel(model='GaussMarkov')
    #Test for replay based mobility
    if ndnwifi.args.mobility:
        info("Running with mobility...")

        p1, p2, p3, p4 = dict(), dict(), dict(), dict()
        p1 = {'position': '40.0,30.0,0.0'}
        p2 = {'position': '40.0,40.0,0.0'}
        p3 = {'position': '31.0,10.0,0.0'}
        p4 = {'position': '200.0,200.0,0.0'}

        ndnwifi.net.mobility(a, 'start', time=1, **p1)
        ndnwifi.net.mobility(b, 'start', time=2, **p2)
        ndnwifi.net.mobility(a, 'stop', time=12, **p3)
        ndnwifi.net.mobility(b, 'stop', time=22, **p4)
        ndnwifi.net.stopMobility(time=23)
        ndnwifi.startMobility(time=0, mob_rep=1, reverse=False)

    ndnwifi.start()
    info("Starting NFD")
    sleep(2)
    AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    info("Starting pingserver...")
    NDNPing.startPingServer(b, "/example")
    faceID = Nfdc.createFace(a, b.IP())
    Nfdc.registerRoute(a, "/example", faceID)

    info("Starting ping...")
    NDNPing.ping(a, "/example", nPings=10)

    sleep(10)
    # Start the CLI
    MiniNDNWifiCLI(ndnwifi.net)
    ndnwifi.net.stop()
    ndnwifi.cleanUp()

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnWifi.handleException()