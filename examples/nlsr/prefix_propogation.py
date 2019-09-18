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

from nlsr_common import getParser

if __name__ == '__main__':
    setLogLevel('info')

    ndn = Minindn(parser=getParser())
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, sync=args.sync,
                       security=args.security, faceType=args.faceType,
                       nFaces=args.faces, routingType=args.routingType)

    Experiment.checkConvergence(ndn, ndn.net.hosts, args.ctime, quit=True)

    firstNode = ndn.net.hosts[0]

    if args.security:
        firstNode.cmd('ndnsec-set-default /ndn/{}-site/%C1.Operator/op'.format(firstNode.name))

    info('Testing advertise\n')
    firstNode.cmd('nlsrc advertise /testPrefix')
    time.sleep(30)

    for host in ndn.net.hosts:
        if host.name != firstNode.name:
            if (int(host.cmd('nfdc fib | grep testPrefix | wc -l')) != 1 or
               int(host.cmd('nlsrc status | grep testPrefix | wc -l')) != 1):
                info('Advertise test failed\n')
                ndn.stop()
                sys.exit(1)

    info('Testing withdraw\n')
    firstNode.cmd('nlsrc withdraw /testPrefix')
    time.sleep(30)

    for host in ndn.net.hosts:
        if host.name != firstNode.name:
            if (int(host.cmd('nfdc fib | grep testPrefix | wc -l')) != 0 or
               int(host.cmd('nlsrc status | grep testPrefix | wc -l')) != 0):
                info('Withdraw test failed\n')
                ndn.stop()
                sys.exit(1)

    if args.isCliEnabled:
        MiniNDNCLI(ndn.net)

    ndn.stop()
