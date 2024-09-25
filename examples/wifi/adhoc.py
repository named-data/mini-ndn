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
from minindn.wifi.minindnwifi import MinindnAdhoc
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

    info("Starting network\n")
    ndnwifi = MinindnAdhoc()
    a = ndnwifi.net["sta1"]
    b = ndnwifi.net["sta2"]

    ndnwifi.start()


    info("Starting NFD\n")
    AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    info("Starting pingserver...\n")
    NDNPing.startPingServer(b, "/example")

    # multicast face for wireless communication
    multicastFaceId = Nfdc.getFaceId(a, "[01:00:5e:00:17:aa]", None, "ether", 6363)
    # print(multicastFaceId)
    Nfdc.registerRoute(a, "/example", multicastFaceId, 100)

    info("Starting ping...\n")
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
        MinindnAdhoc.handleException()