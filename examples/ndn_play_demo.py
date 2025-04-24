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

from minindn.minindn import Minindn
from minindn.apps.nfd import Nfd
from minindn.apps.tshark import Tshark
from minindn.apps.app_manager import AppManager
from minindn.minindn_play.server import PlayServer
from minindn.minindn_play.monitor import LogMonitor

if __name__ == '__main__':
    setLogLevel('info')

    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn()

    ndn.start()

    info('Starting NFD on nodes\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")

    info('Starting TShark on nodes\n')
    sharks = AppManager(ndn, ndn.net.hosts, Tshark, singleLogFile=True)

    ndn.initParams(ndn.net.hosts)

    # Set the color of a node
    ndn.net.hosts[0].params['params']['color'] = "orange"

    # Starts the MiniNDN NDN-Play server
    # This should print a URL you can open to connect to NDN-Play
    # Port 8765 must be forwarded from the host running MiniNDN
    # to the machine running the browser
    server = PlayServer(ndn.net)

    # This method will track updates to the nfd.log file on each node,
    # changing the color briefly to indicate updates. This can be used
    # for a variety of purposes to visualize activity, and is not restricted
    # to just the NFD log file.
    server.add_monitor(LogMonitor(ndn.net.hosts, "log/nfd.log", interval=0.2, regex_filter=""))

    server.start()

    ndn.stop()
