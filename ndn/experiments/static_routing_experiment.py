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
from ndn.apps.ndn_global_routing_helper import GlobalRoutingHelper

from mininet.log import info

class RoutingHelperExp(Experiment):

    def __init__(self, args):
        Experiment.__init__(self, args)

    def start(self):
        """
        Compute and add routes to NFD
        """
        info('Adding static routes to NFD\n')
        grh = GlobalRoutingHelper(self.net, self.options.faceType, self.options.routingType)
        # For all host, pass self.net.hosts or a list, [self.net['a'], ..] or [self.net.hosts[0],.]
        grh.addOrigin([self.net['a']], ["/abc"])
        grh.calculateNPossibleRoutes()

        '''
        Experiment run with default topology, test cases won't work with other topologies
                              # With calculateNPossibleRoutes,
                10            # routing = hr, N = All, from A, 3 routes needs to added to NFD.
            A +++++++ B       # A - B  -- cost 10
            +         +       # A - C  -- cost 10
         10 +         + 10    # A - D  -- cost 20
            +         +       # Same goes for B being a source.
            C         D       #

         prefix "/abc" is advertise from node A, it should be reachable from all other nodes.

        '''
        if self.options.routingType == "link-state":
            # This test only for link-state. Similar test can be done for hyperbolic routing.
            routesFromA = self.net['a'].cmd("nfdc route | grep -v '/localhost/nfd'")
            if '/ndn/b-site/b' not in routesFromA or \
               '/ndn/c-site/c' not in routesFromA or \
               '/ndn/d-site/d' not in routesFromA:
                info("Route addition failed\n")
                exit(-1)

            routesToPrefix = self.net['b'].cmd("nfdc fib | grep '/abc'")
            if '/abc' not in routesToPrefix:
                info("Missing route to advertised prefix, Route addition failed\n")
                exit(-1)

        info('Route addition to NFD completed\n')

Experiment.register("centralize-routing", RoutingHelperExp)