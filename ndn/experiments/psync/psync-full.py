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

from ndn.experiments.experiment import Experiment
from ndn.apps.nfdc import Nfdc

import time
import sys

class PSyncFull(Experiment):

    def __init__(self, args):
        Experiment.__init__(self, args)
        self.syncPrefix = "/sync"
        self.numUserPrefixesPerNode = 2
        self.maxUpdatesPerUserPrefixPerNode = 3

    def registerRouteToAllNeighbors(self, host):
        for node in self.net.hosts:
            for neighbor in node.connectionsTo(host):
                ip = node.IP(neighbor[0])
                Nfdc.createFace(host, ip)
                Nfdc.registerRoute(host, self.syncPrefix, ip)

    def start(self):
        for host in self.net.hosts:
            Nfdc.setStrategy(host, self.syncPrefix, "multicast")
            self.registerRouteToAllNeighbors(host)

        print("Starting psync-full-sync on all the nodes")
        for host in self.net.hosts:
            host.cmd("export NDN_LOG=examples.FullSyncApp=INFO")
            host.cmd("psync-full-sync {} {} {} {} &> psync.logs &"
                     .format(self.syncPrefix, host.name, self.numUserPrefixesPerNode,
                             self.maxUpdatesPerUserPrefixPerNode))

        print("Sleeping 5 minutes for convergence")
        # Estimated time for 4 node default topology
        time.sleep(300)

        totalUpdates = int(host.cmd("grep -r Update {}/*/psync.logs | wc -l"
                                    .format(self.options.workDir)))

        expectedUpdates = (self.maxUpdatesPerUserPrefixPerNode *
                          len(self.net.hosts) * (len(self.net.hosts) - 1) *
                          self.numUserPrefixesPerNode)

        if totalUpdates == expectedUpdates:
            print("PSync full sync has successfully converged.")
        else:
            print("PSync full sync convergence was not successful. Exiting...")
            self.net.stop()
            sys.exit(1)

Experiment.register("psync-full", PSyncFull)
