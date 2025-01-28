# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2025, The University of Memphis,
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
from mininet.log import setLogLevel, info
from minindn.wifi.minindnwifi import MinindnAdhoc
from minindn.util import MiniNDNWifiCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.gpsd import Gpsd
# This experiment uses the topology defined in adhoc-topology.conf and
# is intended to test whether app Gpsd can work with Mini-NDN.
def runExperiment():
    setLogLevel('info')

    info("Starting network\n")
    ndnwifi = MinindnAdhoc()
    a = ndnwifi.net["sta1"]
    b = ndnwifi.net["sta2"]

    ndnwifi.start()

    info("Starting gpsd\n")

    AppManager(ndnwifi, ndnwifi.net.stations, Gpsd, lat=35.11908, lon=-89.93778, altitude=200, update_interval=0.2)

    info("Starting NFD\n")
    AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    sleep(1)

    # run cgps in the Xterm terminal to check gps info
    for node in [a,b]:
        node.cmd(f"xterm -T '{node.name}' -e 'cgps' &")

    # Start the CLI
    MiniNDNWifiCLI(ndnwifi.net)

    # Stop the network and clean up
    ndnwifi.stop()
    ndnwifi.cleanUp()

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnAdhoc.handleException()
