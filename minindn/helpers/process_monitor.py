# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2020, The University of Memphis,
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

from threading import Timer

class ProcessMonitor(object):
    def __init__(self, processId, processName, outputDir, interval=1):
        self._processId = processId.strip()
        self._processName = processName
        self._statFile = '/proc/{}/stat'.format(self._processId)
        self._logFile = '{}/{}-{}-stat.txt'.format(outputDir, self._processName, self._processId)
        self._interval = interval

    def _recordStats(self):
        try:
            with open(self._statFile, 'r') as stat:
                currentTime = int(time.time())
                with open(self._logFile, 'a') as log:
                    for line in stat:
                        log.write('{} {}'.format(currentTime, line))
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
            print('No process with PID={}'.format(self._processId))
            return

        self.start() # Reschedule event

    def start(self):
        self._timer = Timer(self._interval, self._recordStats)
        self._timer.start()
