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

import time
from ndn.ndn_application import NdnApplication

class Nfd(NdnApplication):
    STRATEGY_BEST_ROUTE = "best-route"
    STRATEGY_NCC = "ncc"

    def __init__(self, node):
        NdnApplication.__init__(self, node)

        self.logLevel = node.params["params"].get("nfd-log-level", "NONE")

        self.confFile = "%s/%s.conf" % (node.homeFolder, node.name)
        self.logFile = "%s/%s.log" % (node.homeFolder, node.name)
        self.sockFile = "/var/run/%s.sock" % node.name
        self.ndnFolder = "%s/.ndn" % node.homeFolder
        self.clientConf = "%s/client.conf" % self.ndnFolder

        # Copy nfd.conf file from /usr/local/etc/mini-ndn to the node's home
        node.cmd("sudo cp /usr/local/etc/mini-ndn/nfd.conf %s" % self.confFile)

        # Set log level
        node.cmd("sudo sed -i \'s|$LOG_LEVEL|%s|g\' %s" % (self.logLevel, self.confFile))

        # Open the conf file and change socket file name
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.confFile))

        # Make NDN folder
        node.cmd("sudo mkdir %s" % self.ndnFolder)

        # Copy the client.conf file and change the unix socket
        node.cmd("sudo cp /usr/local/etc/mini-ndn/client.conf.sample %s" % self.clientConf)
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.clientConf))

        # Change home folder
        node.cmd("export HOME=%s" % node.homeFolder)

    def start(self):
        NdnApplication.start(self, "setsid nfd --config %s >> %s 2>&1 &" % (self.confFile, self.logFile))
        time.sleep(2)

    def setStrategy(self, name, strategy):
        self.node.cmd("nfdc set-strategy %s ndn:/localhost/nfd/strategy/%s" % (name, strategy))
        time.sleep(0.5)
