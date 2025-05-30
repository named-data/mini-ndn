# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2025, The University of Memphis,
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
import json
import os
from shlex import quote
from typing import List, Optional, Tuple, Union

from mininet.clean import sh
from mininet.log import debug
from mininet.node import Node

from minindn.apps.application import Application
from minindn.util import copyExistentFile
from minindn.minindn import Minindn

class Nfd(Application):
    def __init__(self, node: Node, logLevel: str = 'NONE', csSize: int = 65536,
                 csPolicy: str = 'lru', csUnsolicitedPolicy: str = 'drop-all',
                 infoeditChanges: Optional[List[Union[Tuple[str, str], Tuple[str, str, str]]]] = None):
        """
        Set up NFD application through wrapper on node. These arguments are directly from nfd.conf,
        so please reference that documentation for more information.

        :param node: Mininet or Mininet-Wifi node object
        :param logLevel: NFD log level set as default (default  "NONE")
        :param csSize: ContentStore size in packets (default 65536)
        :param csPolicy: ContentStore replacement policy (default "lru")
        :param csUnsolicitedPolicy: Policy for handling unsolicited data (default "drop-all")
        :param infoeditChanges: Commands passed to infoedit other than the most commonly used arguments.
               These either expect (key, value) (using the `section` command) or otherwise
               (key, value, put|section|delete).
        """
        Application.__init__(self, node)
        self.logLevel = node.params['params'].get('nfd-log-level', logLevel)

        self.confFile = '{}/nfd.conf'.format(self.homeDir)
        self.logFile = 'nfd.log'
        self.ndnFolder = '{}/.ndn'.format(self.homeDir)
        self.clientConf = '{}/client.conf'.format(self.ndnFolder)
        # Copy nfd.conf file from /usr/local/etc/ndn or /etc/ndn to the node's home directory
        # Use nfd.conf as default configuration for NFD, else use the sample
        possibleConfPaths = ['/usr/local/etc/ndn/nfd.conf', '/usr/local/etc/ndn/nfd.conf.sample',
                             '/etc/ndn/nfd.conf', '/etc/ndn/nfd.conf.sample']
        copyExistentFile(node, possibleConfPaths, self.confFile)

        # Using infoconv, we convert the local nfd.conf file to JSON and parse it into an object
        conf_file = json.loads(node.cmd("infoconv info2json < {}".format(self.confFile)))

        # Set log level
        conf_file["log"]["default_level"] = self.logLevel

        # Set socket file name and path
        # Retrieve the default socket path from the conf file; this avoids issues from #5316
        default_socket_path = os.path.dirname(conf_file["face_system"]["unix"]["path"])
        self.sockFile = '{}/{}.sock'.format(default_socket_path, node.name)
        # Set socket path in conf file to new socket
        conf_file["face_system"]["unix"]["path"] = self.sockFile
        # Create client configuration for host to ensure socket path is consistent
        # Suppress error if working directory exists from prior run
        os.makedirs(self.ndnFolder, exist_ok=True)
        # This will overwrite any existing client.conf files, which should not be an issue
        with open(self.clientConf, "w") as client_conf_file:
            client_conf_file.write("transport=unix://{}\n".format(self.sockFile))

        # Set CS parameters
        conf_file["tables"]["cs_max_packets"] = csSize
        conf_file["tables"]["cs_policy"] = csPolicy
        conf_file["tables"]["cs_unsolicited_policy"] = csUnsolicitedPolicy

        # To avoid complicated Bash piping, we write the JSON to a temporary file
        with open("{}/temp_nfd_conf.json".format(self.homeDir), "w") as temp_file:
            json.dump(conf_file, temp_file)

        # Convert our modified intermediate file and write to the new conf file
        node.cmd("infoconv json2info < {}/temp_nfd_conf.json > {}".format(self.homeDir, self.confFile))

        # Remove the intermediate JSON file
        os.remove("{}/temp_nfd_conf.json".format(self.homeDir))

        self.infocmd = 'infoedit -f nfd.conf'
        # Apply custom infoedit changes
        # EXPECTED FORMAT: [<section>, <key>] OR [<section>, <key>, <operation>]
        # Default behavior will replace all values for section with key
        # Deletion only works for unique keys
        INFOEDIT_COMMANDS = {"put": "-p", "delete": "-d", "section": "-s"}
        if infoeditChanges:
            for infoeditChange in infoeditChanges:
                command = "-s"
                if len(infoeditChange) > 2:
                    if infoeditChange[2] == "delete":
                        debug(f'{self.infocmd} -d {quote(infoeditChange[0])}\n')
                        debug(self.node.cmd(f'{self.infocmd} -d {quote(infoeditChange[0])}\n'))
                        continue
                    else:
                        command = INFOEDIT_COMMANDS[infoeditChange[2]]
                debug(f'{self.infocmd} {command} {quote(infoeditChange[0])} -v {quote(infoeditChange[1])}\n')
                debug(self.node.cmd(f'{self.infocmd} {command} {quote(infoeditChange[0])} -v {quote(infoeditChange[1])}\n'))

        if not Minindn.ndnSecurityDisabled:
            # Generate key and install cert for /localhost/operator to be used by NFD
            node.cmd('ndnsec-key-gen /localhost/operator | ndnsec-cert-install -')

    def start(self):
        Application.start(self, 'nfd --config {}'.format(self.confFile), logfile=self.logFile)
        Minindn.sleep(0.5)
