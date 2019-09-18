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

from mininet.log import setLogLevel, info

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.experiment import Experiment
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient

from nlsr_common import getParser

def multipleFailure(ndn, nfds, nlsrs, args):

    Experiment.checkConvergence(ndn, ndn.net.hosts, args.ctime, quit=True)
    Experiment.setupPing(ndn.net.hosts, Nfdc.STRATEGY_BEST_ROUTE)

    PING_COLLECTION_TIME_BEFORE_FAILURE = 60
    FAILURE_INTERVAL = 60
    RECOVERY_INTERVAL = 60

    # This is the number of pings required to make it through the full experiment
    nInitialPings = (PING_COLLECTION_TIME_BEFORE_FAILURE +
                     len(ndn.net.hosts) * (FAILURE_INTERVAL + RECOVERY_INTERVAL))
    print('Scheduling with {} initial pings'.format(nInitialPings))

    pingedDict = Experiment.startPctPings(ndn.net, nInitialPings, args.pctTraffic)
    time.sleep(PING_COLLECTION_TIME_BEFORE_FAILURE)

    nNodesRemainingToFail = len(ndn.net.hosts)

    for host in ndn.net.hosts:
        # Fail the node
        info('Bringing down node {}\n'.format(host.name))
        nlsrs[host.name].stop()
        nfds[host.name].stop()

        # Stay in failure state for FAILURE_INTERVAL seconds
        time.sleep(FAILURE_INTERVAL)

        # Bring the node back up
        start_time = time.time()
        info('Bringing up node {}\n'.format(host.name))
        nfds[host.name].start()
        nlsrs[host.name].start()
        Experiment.setupPing([host], Nfdc.STRATEGY_BEST_ROUTE)

        recovery_time = int(time.time() - start_time)

        # Number of pings required to reach the end of the test
        nNodesRemainingToFail -= 1
        nPings = ((RECOVERY_INTERVAL - recovery_time) +
                  nNodesRemainingToFail * (FAILURE_INTERVAL + RECOVERY_INTERVAL))

        info('Scheduling with {} remaining pings\n'.format(nPings))

        # Restart pings
        for nodeToPing in pingedDict[host]:
            NDNPingClient.ping(host, nodeToPing, nPings)

        time.sleep(RECOVERY_INTERVAL - recovery_time)

    #Experiment.checkConvergence(ndn, ndn.net.hosts, args.ctime, quit=True)

if __name__ == '__main__':
    setLogLevel('info')

    ndn = Minindn(parser=getParser())
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, sync=args.sync,
                       security=args.security, faceType=args.faceType,
                       nFaces=args.faces, routingType=args.routingType)

    multipleFailure(ndn, nfds, nlsrs, args)

    if args.isCliEnabled:
        MiniNDNCLI(ndn.net)

    ndn.stop()
