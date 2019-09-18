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
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

from nlsr_common import getParser

if __name__ == '__main__':
    setLogLevel('info')

    topo = Topo()
    h1 = topo.addHost('h1')
    h2 = topo.addHost('h2')
    topo.addLink(h1, h2, delay='10ms')

    ndn = Minindn(parser=getParser(), topo=topo)
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, [], Nlsr)

    host1 = ndn.net.hosts[0]
    nlsrs.startOnNode(host1, security=args.security, faceType=args.faceType,
                      nFaces=args.faces, routingType=args.routingType)


    expectedTotalCount = 500
    for i in range(0, expectedTotalCount):
        host1.cmd('nlsrc advertise /long/name/to/exceed/max/packet/size/host1/{}'.format(i))

    time.sleep(60)

    host2 = ndn.net.hosts[1]
    nlsrs.startOnNode(host2, security=args.security, faceType=args.faceType,
                      nFaces=args.faces, routingType=args.routingType)

    time.sleep(60)

    advertiseCount = int(host2.cmd('nfdc fib | grep host1 | wc -l'))
    info(advertiseCount)
    if advertiseCount == expectedTotalCount:
        info('\nSuccessfully advertised {} prefixes\n'.format(expectedTotalCount))
    else:
        info('\nAdvertising {} prefixes failed. Exiting...\n'.format(expectedTotalCount))
        ndn.stop()
        sys.exit(1)

    ndn.stop()
