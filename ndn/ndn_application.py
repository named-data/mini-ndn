# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2016, The University of Memphis,
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

import os

class NdnApplication:
    def __init__(self, node):
        self.node = node
        self.isRunning = False
        self.processId = ""

    def start(self, command):
        if self.isRunning is True:
            try:
                os.kill(int(self.processId), 0)
            except OSError:
                self.isRunning = False

        if self.isRunning is False:
            self.node.cmd(command)
            self.processId = self.node.cmd("echo $!")[:-1]

            self.isRunning = True

    def stop(self):
        if self.isRunning:
            self.node.cmd("sudo kill %s" % self.processId)

            self.isRunning = False
