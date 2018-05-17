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

import sys
import time
from ndn.experiments.experiment import Experiment

class PrefixPropogationExperiment(Experiment):

    def __init__(self, args):
        Experiment.__init__(self, args)

    def setup(self):
        self.checkConvergence()

    def run(self):
        firstNode = self.net.hosts[0]

        if self.nlsrSecurity:
            firstNode.cmd("ndnsec-set-default /ndn/{}-site/%C1.Operator/op".format(firstNode.name))

        print("Testing advertise")
        firstNode.cmd("nlsrc advertise /testPrefix")
        time.sleep(30)

        for host in self.net.hosts:
            if host.name != firstNode.name:
                if (int(host.cmd("nfdc fib | grep testPrefix | wc -l")) != 1 or
                   int(host.cmd("nlsrc status | grep testPrefix | wc -l")) != 1):
                    print("Advertise test failed")
                    self.net.stop()
                    sys.exit(1)

        print("Testing withdraw")
        firstNode.cmd("nlsrc withdraw /testPrefix")
        time.sleep(30)

        for host in self.net.hosts:
            if host.name != firstNode.name:
                if (int(host.cmd("nfdc fib | grep testPrefix | wc -l")) != 0 or
                   int(host.cmd("nlsrc status | grep testPrefix | wc -l")) != 0):
                    print("Withdraw test failed")
                    self.net.stop()
                    sys.exit(1)

Experiment.register("prefix-propogation", PrefixPropogationExperiment)
