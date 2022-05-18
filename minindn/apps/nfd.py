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

from minindn.apps.application import Application
from minindn.util import copyExistentFile
from minindn.minindn import Minindn

class Nfd(Application):

    def __init__(self, node, logLevel='NONE', csSize=65536,
                 csPolicy='lru', csUnsolicitedPolicy='drop-all'):
        Application.__init__(self, node)

        self.logLevel = node.params['params'].get('nfd-log-level', logLevel)

        self.confFile = '{}/nfd.conf'.format(self.homeDir)
        self.logFile = 'nfd.log'
        self.sockFile = '/run/{}.sock'.format(node.name)
        self.ndnFolder = '{}/.ndn'.format(self.homeDir)
        self.clientConf = '{}/client.conf'.format(self.ndnFolder)

        # Copy nfd.conf file from /usr/local/etc/ndn or /etc/ndn to the node's home directory
        # Use nfd.conf as default configuration for NFD, else use the sample
        possibleConfPaths = ['/usr/local/etc/ndn/nfd.conf.sample', '/usr/local/etc/ndn/nfd.conf',
                             '/etc/ndn/nfd.conf.sample', '/etc/ndn/nfd.conf']
        copyExistentFile(node, possibleConfPaths, self.confFile)

        # Set log level
        node.cmd('infoedit -f {} -s log.default_level -v {}'.format(self.confFile, self.logLevel))
        # Open the conf file and change socket file name
        node.cmd('infoedit -f {} -s face_system.unix.path -v {}'.format(self.confFile, self.sockFile))

        # Set CS parameters
        node.cmd('infoedit -f {} -s tables.cs_max_packets -v {}'.format(self.confFile, csSize))
        node.cmd('infoedit -f {} -s tables.cs_policy -v {}'.format(self.confFile, csPolicy))
        node.cmd('infoedit -f {} -s tables.cs_unsolicited_policy -v {}'.format(self.confFile, csUnsolicitedPolicy))

        # Make NDN folder
        node.cmd('mkdir -p {}'.format(self.ndnFolder))

        # Copy client configuration to host
        possibleClientConfPaths = ['/usr/local/etc/ndn/client.conf.sample', '/etc/ndn/client.conf.sample']
        copyExistentFile(node, possibleClientConfPaths, self.clientConf)

        # Change the unix socket
        node.cmd('sudo sed -i "s|;transport|transport|g" {}'.format(self.clientConf))
        node.cmd('sudo sed -i "s|nfd.sock|{}.sock|g" {}'.format(node.name, self.clientConf))

        if not Minindn.ndnSecurityDisabled:
            # Generate key and install cert for /localhost/operator to be used by NFD
            node.cmd('ndnsec-keygen /localhost/operator | ndnsec-install-cert -')

    def start(self):
        Application.start(self, 'nfd --config {}'.format(self.confFile), logfile=self.logFile)
        Minindn.sleep(0.5)
