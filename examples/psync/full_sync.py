# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2019, The University of Memphis,
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

import time
import sys

from mininet.log import setLogLevel, info

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc

def registerRouteToAllNeighbors(ndn, host, syncPrefix):
    for node in ndn.net.hosts:
        for neighbor in node.connectionsTo(host):
            ip = node.IP(neighbor[0])
            faceID = Nfdc.createFace(host, ip)
            Nfdc.registerRoute(host, syncPrefix, faceID)

if __name__ == '__main__':
    setLogLevel('info')

    ndn = Minindn()
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)

    syncPrefix = "/sync"
    numUserPrefixesPerNode = 2
    maxUpdatesPerUserPrefixPerNode = 3

    for host in ndn.net.hosts:
        Nfdc.setStrategy(host, syncPrefix, Nfdc.STRATEGY_MULTICAST)
        registerRouteToAllNeighbors(ndn, host, syncPrefix)

    info('Starting psync-full-sync on all the nodes\n')
    for host in ndn.net.hosts:
        host.cmd('export NDN_LOG=examples.FullSyncApp=INFO')
        host.cmd('psync-full-sync {} {} {} {} &> psync.logs &'
                 .format(syncPrefix, host.name, numUserPrefixesPerNode,
                         maxUpdatesPerUserPrefixPerNode))

    info('Sleeping 5 minutes for convergence\n')
    # Estimated time for 4 node default topology
    time.sleep(300)

    totalUpdates = int(host.cmd('grep -r Update {}/*/psync.logs | wc -l'
                                .format(ndn.workDir)))

    expectedUpdates = (maxUpdatesPerUserPrefixPerNode *
                      len(ndn.net.hosts) * (len(ndn.net.hosts) - 1) * numUserPrefixesPerNode)

    if totalUpdates == expectedUpdates:
        info('PSync full sync has successfully converged.\n')
    else:
        info('PSync full sync convergence was not successful. Exiting...\n')
        ndn.stop()
        sys.exit(1)
