# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015 The University of Memphis,
#                    Arizona Board of Regents,
#                    Regents of the University of California.
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

import time

class PingallExperiment(Experiment):

    def __init__(self, args):

        Experiment.__init__(self, args)
        self.COLLECTION_PERIOD_BUFFER = 10
        self.pctTraffic = float(args["pctTraffic"])
        print "Using %f traffic" % self.pctTraffic

    def run(self):
        self.startPctPings()

        # For pingall experiment sleep for the number of pings + some offset
        time.sleep(self.nPings + self.COLLECTION_PERIOD_BUFFER)

Experiment.register("pingall", PingallExperiment)
