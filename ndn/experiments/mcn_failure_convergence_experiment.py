# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017 The University of Memphis,
#                         Arizona Board of Regents,
#                         Regents of the University of California.
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
from ndn.experiments.mcn_failure_experiment import MCNFailureExperiment

import time

class MCNFailureConvergenceExperiment(MCNFailureExperiment):

    def __init__(self, args):
        MCNFailureExperiment.__init__(self, args)

    def run(self):
        mostConnectedNode = self.getMostConnectedNode()

        # After the pings are scheduled, collect pings for 1 minute
        time.sleep(self.PING_COLLECTION_TIME_BEFORE_FAILURE)

        # Bring down MCN
        self.failNode(mostConnectedNode)

        # MCN is down for 2 minutes
        time.sleep(120)

        # Bring MCN back up
        self.recoverNode(mostConnectedNode)

        self.checkConvergence()

Experiment.register("mcn-failure-convergence", MCNFailureConvergenceExperiment)
