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
from ndn.apps.nlsr import Nlsr, NlsrConfigGenerator

from mininet.log import info

import time, sys

class AdvertiseDelayedStartExperiment(Experiment):
    '''Tests Name LSA data segmentation'''

    def __init__(self, args):
        Experiment.__init__(self, args)

    def setup(self):
        pass

    def run(self):
        pass

    def startNlsr(self, checkConvergence = True):
        # NLSR Security
        if self.options.nlsrSecurity is True:
            Nlsr.createKeysAndCertificates(self.net, self.options.workDir)

        host1 = self.net.hosts[0]
        host1.nlsr = Nlsr(host1, self.options)
        host1.nlsr.start()

        expectedTotalCount = 500
        for i in range(0, expectedTotalCount):
            host1.cmd("nlsrc advertise /long/name/to/exceed/max/packet/size/host1/{}".format(i))

        time.sleep(60)

        host2 = self.net.hosts[1]
        host2.nlsr = Nlsr(host2, self.options)
        host2.nlsr.start()

        time.sleep(60)

        advertiseCount = int(host2.cmd("nfdc fib | grep host1 | wc -l"))
        info(advertiseCount)
        if advertiseCount == expectedTotalCount:
            info('\nSuccessfully advertised {} prefixes\n'.format(expectedTotalCount))
        else:
            info('\nAdvertising {} prefixes failed. Exiting...\n'.format(expectedTotalCount))
            self.net.stop()
            sys.exit(1)

Experiment.register("advertise-delayed-start", AdvertiseDelayedStartExperiment)
