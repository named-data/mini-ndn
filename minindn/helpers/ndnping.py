# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2021, The University of Memphis,
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

import time

# Todo: convert to app

class NDNPing(object):
    @staticmethod
    def ping(source, prefix, pingDataFile="output-client", nPings=1, interval=None, timeout=None,
             starting_seq_num=None, identifier=None, allow_stale_data=False, print_timestamp=True,
             sleepTime=0.2):
        print('Scheduling ping(s) from {} for {}'.format(source.name, prefix))
        # Use '&' to run in background and perform parallel pings
        source.cmd("mkdir -p ping-data")
        source.cmd('ndnping{1}{2}{3}{4}{5}{6}{7} {0} >> ping-data/{8}.txt &'
        .format(
            prefix,
            ' -c {}'.format(nPings),
            ' -i {}'.format(interval) if interval else '',
            ' -o {}'.format(timeout) if timeout  else '',
            ' -n {}'.format(starting_seq_num) if starting_seq_num else '',
            ' -p {}'.format(identifier) if identifier else '',
            ' -a' if allow_stale_data else '',
            ' -t' if print_timestamp else '',
            pingDataFile
        ))
        time.sleep(sleepTime)

    @staticmethod
    def startPingServer(source, prefix, pingDataFile="output-server", freshness=None, satisfy=None,
                        size=None, timestamp=False, quiet=False):
        """
        Start a pingserver
         :param string preifx: prefix to start pingserver on
         :param int freshness: FreshnessPeriod of the ping response, in milliseconds
         :param int satisfy: maximum number of pings to satisfy
         :param int size: size of response payload
         :param boolean timestamp: prepend a timestamp to each log message
         :param boolean quite: do not print a log message each time a ping packet is received
        """
        print('Staring ping server on prefix {}'.format(prefix))
        source.cmd("mkdir -p ping-data")
        cmd = 'ndnpingserver {1}{2}{3}{4}{5} {0}>> ping-data/{6}.txt &'.format(
            prefix,
            '-f {}'.format(freshness) if freshness else '',
            '-p {}'.format(satisfy) if satisfy else '',
            '-s {}'.format(size) if size else '',
            '{}'.format('-t') if timestamp else '',
            '{}'.format('-q') if quiet else '',
            pingDataFile
        )
        source.cmd(cmd)