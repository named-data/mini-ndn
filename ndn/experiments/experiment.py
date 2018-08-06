# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2018, The University of Memphis,
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

from ndn import ExperimentManager
from ndn.apps.nfdc import Nfdc

from ndn.apps.nlsr import Nlsr, NlsrConfigGenerator
from ndn.apps.ndn_ping_client import NDNPingClient

class Experiment:

    def __init__(self, args):
        self.net = args["net"]
        self.options = args["options"]

        # Used to restart pings on the recovered node if any
        self.pingedDict = {}

    def afterNfdStart(self):
        pass

    def start(self):
        self.afterNfdStart()
        if self.options.isNlsrEnabled is True:
            self.startNlsr()
        self.setup()
        self.run()

    def setup(self):
        for host in self.net.hosts:
            # Set strategy
            Nfdc.setStrategy(host, "/ndn/", self.options.strategy)

            # Start ping server
            host.cmd("ndnpingserver /ndn/{}-site/{} > ping-server &".format(host.name, host.name))

            # Create folder to store ping data
            host.cmd("mkdir ping-data")

    def startNlsr(self, checkConvergence = True):
        # NLSR Security
        if self.options.nlsrSecurity is True:
            Nlsr.createKeysAndCertificates(self.net, self.options.workDir)

        # NLSR initialization
        info('Starting NLSR on nodes\n')
        for host in self.net.hosts:
            host.nlsr = Nlsr(host, self.options)
            host.nlsr.start()

        for host in self.net.hosts:
            nlsrStatus = host.cmd("ps -g | grep 'nlsr -f {}/[n]lsr.conf'".format(host.homeFolder))
            if not host.nlsr.isRunning or not nlsrStatus:
                print("NLSR on host {} is not running. Printing log file and exiting...".format(host.name))
                print(host.cmd("tail {}/log/nlsr.log".format(host.homeFolder)))
                self.net.stop()
                sys.exit(1)

        if checkConvergence:
            self.checkConvergence()

    def checkConvergence(self, convergenceTime = None):
        if convergenceTime is None:
            convergenceTime = self.options.ctime

        # Wait for convergence time period
        print "Waiting " + str(convergenceTime) + " seconds for convergence..."
        time.sleep(convergenceTime)
        print "...done"

        # To check whether all the nodes of NLSR have converged
        didNlsrConverge = True

        # Checking for convergence
        for host in self.net.hosts:
            statusRouter = host.cmd("nfdc fib list | grep site/%C1.Router/cs/")
            statusPrefix = host.cmd("nfdc fib list | grep ndn | grep site | grep -v Router")
            didNodeConverge = True
            for node in self.net.hosts:
                # Node has its own router name in the fib list, but not name prefix
                if ( ("/ndn/{}-site/%C1.Router/cs/{}".format(node.name, node.name)) not in statusRouter or
                      host.name != node.name and ("/ndn/{}-site/{}".format(node.name, node.name)) not in statusPrefix ):
                    didNodeConverge = False
                    didNlsrConverge = False

            host.cmd("echo " + str(didNodeConverge) + " > convergence-result &")

        if didNlsrConverge:
            print("NLSR has successfully converged.")
        else:
            print("NLSR has not converged. Exiting...")
            self.net.stop()
            sys.exit(1)

    def startPings(self):
        for host in self.net.hosts:
            for other in self.net.hosts:
                # Do not ping self
                if host.name != other.name:
                    NDNPingClient.ping(host, other, self.options.nPings)

    def failNode(self, host):
        print("Bringing {} down".format(host.name))
        host.nfd.stop()

    def recoverNode(self, host):
        print("Bringing {} up".format(host.name))
        host.nfd.start()
        host.nlsr.createFaces()
        host.nlsr.start()
        Nfdc.setStrategy(host, "/ndn/", self.options.strategy)
        host.cmd("ndnpingserver /ndn/{}-site/{} > ping-server &".format(host.name, host.name))

    def startPctPings(self):
        nNodesToPing = int(round(len(self.net.hosts) * self.options.pctTraffic))
        print "Each node will ping {} node(s)".format(nNodesToPing)
        # Temporarily store all the nodes being pinged by a particular node
        nodesPingedList = []

        for host in self.net.hosts:
            # Create a circular list
            pool = cycle(self.net.hosts)

            # Move iterator to current node
            next(x for x in pool if host.name == x.name)

            # Track number of nodes to ping scheduled for this node
            nNodesScheduled = 0

            while nNodesScheduled < nNodesToPing:
                other = pool.next()

                # Do not ping self
                if host.name != other.name:
                    NDNPingClient.ping(host, other, self.options.nPings)
                    nodesPingedList.append(other)

                # Always increment because in 100% case a node should not ping itself
                nNodesScheduled = nNodesScheduled + 1

            self.pingedDict[host] = nodesPingedList
            nodesPingedList = []

    @staticmethod
    def register(name, experimentClass):
        ExperimentManager.register(name, experimentClass)
