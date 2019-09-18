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

import argparse

def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ctime', type=int, default=60,
                        help='Specify convergence time for the topology (Default: 60 seconds)')

    parser.add_argument('--faces', type=int, default=3,
                        help='Specify number of max faces per prefix for NLSR 0-60')

    parser.add_argument('--routing', dest='routingType', default='link-state',
                        choices=['link-state', 'hr', 'dry'],
                        help='''Choose routing type, dry = link-state is used
                                but hr is calculated for comparision.''')

    parser.add_argument('--sync', dest='sync', default='psync',
                        choices=['chronosync', 'psync'],
                        help='choose the sync protocol to be used by NLSR.')

    parser.add_argument('--security', action='store_true', dest='security',
                        help='Enables NLSR security')

    parser.add_argument('--face-type', dest='faceType', default='udp', choices=['udp', 'tcp'])

    parser.add_argument('--no-cli', action='store_false', dest='isCliEnabled',
                        help='Run experiments and exit without showing the command line interface')

    parser.add_argument('--pct-traffic', dest='pctTraffic', type=float, default=1.0,
                        help='Specify the percentage of nodes each node should ping')

    parser.add_argument('--nPings', type=int, default=300,
                        help='Number of pings to perform between each node in the experiment')

    return parser
