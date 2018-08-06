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

from ndn.experiments.experiment import Experiment
from ndn.apps.ndn_ping_client import NDNPingClient

import time

class FailureExperiment(Experiment):

    def __init__(self, args):
        args["options"].nPings = 300
        Experiment.__init__(self, args)

        self.PING_COLLECTION_TIME_BEFORE_FAILURE = 60
        self.PING_COLLECTION_TIME_AFTER_RECOVERY = 120

    def run(self):
        self.startPctPings()

        # After the pings are scheduled, collect pings for 1 minute
        time.sleep(self.PING_COLLECTION_TIME_BEFORE_FAILURE)

        # Bring down CSU
        for host in self.net.hosts:
            if host.name == "csu":
                self.failNode(host)
                break

        # CSU is down for 2 minutes
        time.sleep(120)

        # Bring CSU back up
        for host in self.net.hosts:
            if host.name == "csu":
                self.recoverNode(host)

                for other in self.net.hosts:
                    if host.name != other.name:
                        NDNPingClient.ping(host, other, self.PING_COLLECTION_TIME_AFTER_RECOVERY)

        # Collect pings for more seconds after CSU is up
        time.sleep(self.PING_COLLECTION_TIME_AFTER_RECOVERY)

Experiment.register("failure", FailureExperiment)
