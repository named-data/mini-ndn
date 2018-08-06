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

import time

class NlsrDelayedStartExperiment(Experiment):

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

        i = 1
        # NLSR initialization
        info('Starting NLSR on nodes\n')
        for host in self.net.hosts:
            host.nlsr = Nlsr(host, self.options)
            host.nlsr.start()

            # Wait 1/2 minute between starting NLSRs
            # Wait 1 hour before starting last NLSR
            if i == len(self.net.hosts) - 1:
                info('Sleeping 1 hour before starting last NLSR')
                time.sleep(3600)
            else:
                time.sleep(30)
            i += 1

        if checkConvergence:
            self.checkConvergence()

Experiment.register("nlsr-delayed-start", NlsrDelayedStartExperiment)
