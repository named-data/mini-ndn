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

import time, sys, os
from ndn.ndn_application import NdnApplication
from ndn.util import copyExistentFile

class Nfd(NdnApplication):

    def __init__(self, node, csSize):
        NdnApplication.__init__(self, node)

        self.logLevel = node.params["params"].get("nfd-log-level", "DEBUG")

        self.confFile = "{}/nfd.conf".format(node.homeFolder)
        self.logFile = "{}/nfd.log".format(node.homeFolder)
        self.sockFile = "/var/run/{}.sock".format(node.name)
        self.ndnFolder = "{}/.ndn".format(node.homeFolder)
        self.clientConf = "{}/client.conf".format(self.ndnFolder)

        # Copy nfd.conf file from /usr/local/etc/ndn or /etc/ndn to the node's home directory
        # Use nfd.conf as default configuration for NFD, else use the sample
        possibleConfPaths = ["/usr/local/etc/ndn/nfd.conf.sample", "/usr/local/etc/ndn/nfd.conf",
                             "/etc/ndn/nfd.conf.sample", "/etc/ndn/nfd.conf"]
        copyExistentFile(node, possibleConfPaths, self.confFile)

        # Set log level
        node.cmd("infoedit -f {} -s log.default_level -v {}".format(self.confFile, self.logLevel))
        # Open the conf file and change socket file name
        node.cmd("infoedit -f {} -s face_system.unix.path -v /var/run/{}.sock".format(self.confFile, node.name))

        # Set CS size
        node.cmd("infoedit -f {} -s tables.cs_max_packets -v {}".format(self.confFile, csSize))

        # Make NDN folder
        node.cmd("sudo mkdir {}".format(self.ndnFolder))

        # Copy client configuration to host
        possibleClientConfPaths = ["/usr/local/etc/ndn/client.conf.sample", "/etc/ndn/client.conf.sample"]
        copyExistentFile(node, possibleClientConfPaths, self.clientConf)

        # Change the unix socket
        node.cmd("sudo sed -i 's|nfd.sock|{}.sock|g' {}".format(node.name, self.clientConf))

        # Change home folder
        node.cmd("export HOME={}".format(node.homeFolder))
        node.cmd("ndnsec-keygen /localhost/operator | ndnsec-install-cert -")

    def start(self):
        NdnApplication.start(self, "setsid nfd --config {} > {} 2>&1 &".format(self.confFile, self.logFile))
        time.sleep(2)
