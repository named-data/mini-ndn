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

import time
import sys
from itertools import cycle

from mininet.log import info

from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnping import NDNPing
from minindn.util import getSafeName

class Experiment(object):
    @staticmethod
    def checkConvergence(ndn, hosts, convergenceTime, quit=False, returnConvergenceInfo=False):
        # Wait for convergence time period
        info('Waiting {} seconds for convergence...\n'.format(convergenceTime))
        time.sleep(convergenceTime)
        info('...done\n')

        didNlsrConverge = True
        convergeInfo = {}

        for host in hosts:
            convergeInfo[host.name] = {}
            statusRouter = host.cmd('nfdc fib list | grep site/%C1.Router/cs/')
            statusPrefix = host.cmd('nfdc fib list | grep ndn | grep site | grep -v Router')
            for node in hosts:
                # Node has its own router name in the fib list, but not name prefix
                routerPrefix = ('/ndn/{}-site/%C1.Router/cs/{}'.format(node.name, node.name))
                namePrefix = ('/ndn/{}-site/{}'.format(node.name, node.name))

                statusRouterCheck = routerPrefix not in statusRouter
                statusPrefixCheck = host.name != node.name and namePrefix not in statusPrefix

                if statusRouterCheck or statusPrefixCheck:
                    didNlsrConverge = False
                    host.cmd('echo {} > convergence-result &'.format(False))

                    if returnConvergenceInfo:
                        convergeInfo[host.name][node.name] = []
                        if statusRouterCheck:
                            convergeInfo[host.name][node.name].append(routerPrefix)

                        if statusPrefixCheck:
                            convergeInfo[host.name][node.name].append(namePrefix)
                else:
                    host.cmd('echo {} > convergence-result &'.format(True))

        if didNlsrConverge:
            if quit:
                info('NLSR has converged successfully. Exiting...\n')
                ndn.stop()
                sys.exit(0)
            else:
                info('NLSR has converged successfully.\n')
        else:
            if quit:
                info('NLSR has not converged. Exiting...\n')
                ndn.stop()
                sys.exit(1)
            else:
                info('NLSR has not converged.\n')

        if returnConvergenceInfo:
            return didNlsrConverge, convergeInfo
        else:
            return didNlsrConverge

    @staticmethod
    def setupPing(hosts, strategy):
        for host in hosts:
            host.cmd('mkdir -p ping-data')
            Nfdc.setStrategy(host, '/ndn/', strategy)
            prefix = getSafeName('/ndn/{}-site/{}'.format(host.name, host.name))
            NDNPing.startPingServer(host, prefix)

    @staticmethod
    def startPctPings(net, nPings, pctTraffic=1.0):
        nNodesToPing = int(round(len(net.hosts) * pctTraffic))
        info('Each node will ping {} node(s)\n'.format(nNodesToPing))
        # Temporarily store all the nodes being pinged by a particular node
        nodesPingedList = []
        pingedDict = {}

        for host in net.hosts:
            # Create a circular list
            pool = cycle(net.hosts)

            # Move iterator to current node
            next(x for x in pool if host.name == x.name)

            # Track number of nodes to ping scheduled for this node
            nNodesScheduled = 0

            while nNodesScheduled < nNodesToPing:
                other = next(pool)

                # Do not ping self
                if host.name != other.name:
                    destPrefix = getSafeName('/ndn/{}-site/{}'.format(other.name, other.name))
                    NDNPing.ping(host, destPrefix, other.name, nPings)
                    nodesPingedList.append(other)

                # Always increment because in 100% case a node should not ping itself
                nNodesScheduled = nNodesScheduled + 1

            pingedDict[host] = nodesPingedList
            nodesPingedList = []

        return pingedDict
