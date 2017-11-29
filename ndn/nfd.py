# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
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


class Nfd(NdnApplication):
    STRATEGY_BEST_ROUTE = "best-route"
    STRATEGY_NCC = "ncc"

    def __init__(self, node):
        NdnApplication.__init__(self, node)

        self.logLevel = node.params["params"].get("nfd-log-level", "NONE")

        self.confFile = "{}/{}.conf".format(node.homeFolder, node.name)
        self.logFile = "{}/{}.log".format(node.homeFolder, node.name)
        self.sockFile = "/var/run/{}.sock".format(node.name)
        self.ndnFolder = "{}/.ndn".format(node.homeFolder)
        self.clientConf = "{}/client.conf".format(self.ndnFolder)

        # Copy nfd.conf file from /usr/local/etc/ndn to the node's home

        # Use nfd.conf as default configuration for NFD, else use the sample
        if os.path.isfile("/usr/local/etc/ndn/nfd.conf") == True:
            node.cmd("sudo cp /usr/local/etc/ndn/nfd.conf {}".format(self.confFile))
        elif os.path.isfile("/usr/local/etc/ndn/nfd.conf.sample") == True:
            node.cmd("sudo cp /usr/local/etc/ndn/nfd.conf.sample {}".format(self.confFile))
        else:
            sys.exit("nfd.conf or nfd.conf.sample cannot be found in the expected directory. Exit.")

        # Set log level
        node.cmd("infoedit -f {} -s log.default_level -v {}".format(self.confFile, self.logLevel))
        # Open the conf file and change socket file name
        node.cmd("infoedit -f {} -s face_system.unix.path -v /var/run/{}.sock".format(self.confFile, node.name))

        # Make NDN folder
        node.cmd("sudo mkdir {}".format(self.ndnFolder))

        # Copy the client.conf file and change the unix socket
        node.cmd("sudo cp /usr/local/etc/ndn/client.conf.sample {}".format(self.clientConf))

        node.cmd("sudo sed -i 's|nfd.sock|{}.sock|g' {}".format(node.name, self.clientConf))

        # Change home folder
        node.cmd("export HOME={}".format(node.homeFolder))

    def start(self):
        NdnApplication.start(self, "setsid nfd --config {} >> {} 2>&1 &".format(self.confFile, self.logFile))
        time.sleep(2)

    def setStrategy(self, name, strategy):
        self.node.cmd("nfdc strategy set {} ndn:/localhost/nfd/strategy/{}".format(name, strategy))
        time.sleep(0.5)
