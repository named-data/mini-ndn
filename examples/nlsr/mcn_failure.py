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

def mcnFailure(ndn, nfds, nlsrs, args):
    Experiment.checkConvergence(ndn, ndn.net.hosts, args.ctime, quit=True)
    if args.nPings != 0:
        Experiment.setupPing(ndn.net.hosts, Nfdc.STRATEGY_BEST_ROUTE)
        pingedDict = Experiment.startPctPings(ndn.net, args.nPings, args.pctTraffic)

    PING_COLLECTION_TIME_BEFORE_FAILURE = 60
    PING_COLLECTION_TIME_AFTER_RECOVERY = 120

    time.sleep(PING_COLLECTION_TIME_BEFORE_FAILURE)

    mcn = max(ndn.net.hosts, key=lambda host: len(host.intfNames()))

    info('Bringing down node {}\n'.format(mcn.name))
    nlsrs[mcn.name].stop()
    nfds[mcn.name].stop()

    time.sleep(args.ctime)

    info('Bringing up node {}\n'.format(mcn.name))
    nfds[mcn.name].start()
    nlsrs[mcn.name].start()

    # Restart pings
    if args.nPings != 0:
        Experiment.setupPing([mcn], Nfdc.STRATEGY_BEST_ROUTE)
        for nodeToPing in pingedDict[mcn]:
            NDNPingClient.ping(mcn, nodeToPing, PING_COLLECTION_TIME_AFTER_RECOVERY)

        time.sleep(PING_COLLECTION_TIME_AFTER_RECOVERY)

    Experiment.checkConvergence(ndn, ndn.net.hosts, args.ctime, quit=True)

if __name__ == '__main__':
    setLogLevel('info')

    ndn = Minindn(parser=getParser())
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, sync=args.sync,
                       security=args.security, faceType=args.faceType,
                       nFaces=args.faces, routingType=args.routingType)

    mcnFailure(ndn, nfds, nlsrs, args)

    if args.isCliEnabled:
        MiniNDNCLI(ndn.net)

    ndn.stop()
