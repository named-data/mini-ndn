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

from minindn.apps.application import Application
from mininet.log import debug


class Tshark(Application):
    """
    Logging utility to dump network traffic of a node to a PCAP file.

    The app is based on the command line tool tshark and requires tshark to be installed on the system.
    """

    def __init__(self, node, logFolder="./", singleLogFile=False):
        """
        :param logFolder Folder, where PCAP files are stored.
        :param singleLogFile Single PCAP file per node, or individual PCAP for each interface
        """

        Application.__init__(self, node)

        self.logFolder = logFolder
        self.singleLogFile = singleLogFile

        # Create logfile folder in case it does not exist
        node.cmd('mkdir -p {}'.format(self.logFolder))

    def start(self):
        # Start capturing traffic with Tshark.
        debug("[{0}] Starting tshark logging\n".format(self.node.name))

        if self.singleLogFile:
            interfaces = ["-i " + intf for intf in self.node.intfNames()]
            ndnDumpOutputFile = "{}/{}-interfaces.pcap".format(self.logFolder, self.node.name)
            self.node.cmd("tshark {} -w {} -q &".format(" ".join(interfaces), ndnDumpOutputFile))
        else:
            for intf in self.node.intfNames():
                ndnDumpOutputFile = "{}/{}.pcap".format(self.logFolder, intf)
                self.node.cmd("tshark -i {} -w {} -q &".format(intf, ndnDumpOutputFile))
