# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
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
from ndn.nlsr import Nlsr

import time

class MultipleFailureExperiment(Experiment):

    def __init__(self, args):

        self.PING_COLLECTION_TIME_BEFORE_FAILURE = 60

        self.FAILURE_INTERVAL = 60
        self.RECOVERY_INTERVAL = 60

        # This is the number of pings required to make it through the full experiment
        nInitialPings = (self.PING_COLLECTION_TIME_BEFORE_FAILURE +
                         len(args["net"].hosts)*(self.FAILURE_INTERVAL + self.RECOVERY_INTERVAL))
        print("Scheduling with %s initial pings" % nInitialPings)

        args["nPings"] = nInitialPings

        Experiment.__init__(self, args)

    def run(self):
        self.startPctPings()

        # After the pings are scheduled, collect pings for 1 minute
        time.sleep(self.PING_COLLECTION_TIME_BEFORE_FAILURE)

        nNodesRemainingToFail = len(self.net.hosts)

        # Fail and recover each node
        for host in self.net.hosts:
            # Fail the node
            self.failNode(host)

            # Stay in failure state for FAILURE_INTERVAL seconds
            time.sleep(self.FAILURE_INTERVAL)

            # Bring the node back up
            start_time = time.time()
            self.recoverNode(host)
            recovery_time = int(time.time() - start_time)

            # Number of pings required to reach the end of the test
            nNodesRemainingToFail -= 1
            nPings = ((self.RECOVERY_INTERVAL - recovery_time) +
                      nNodesRemainingToFail*(self.FAILURE_INTERVAL + self.RECOVERY_INTERVAL))

            print("Scheduling with %s remaining pings" % nPings)

            # Restart pings
            for nodeToPing in self.pingedDict[host]:
                self.ping(host, nodeToPing, nPings)

            time.sleep(self.RECOVERY_INTERVAL - recovery_time)

Experiment.register("multiple-failure", MultipleFailureExperiment)
