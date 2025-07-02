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

import os
from shlex import quote
import shutil
import sys
from typing import Dict, List, Optional, Tuple, Union

from mininet.clean import sh
from mininet.examples.cluster import RemoteMixin
from mininet.log import debug, warn
from mininet.node import Node, Switch

from minindn.apps.application import Application
from minindn.util import scp, copyExistentFile, MACToEther
from minindn.helpers.nfdc import Nfdc
from minindn.minindn import Minindn

class Nlsr(Application):
    ROUTING_LINK_STATE = 'link-state'
    ROUTING_HYPERBOLIC = 'hr'
    ROUTING_DRY_RUN = 'dry'
    SYNC_PSYNC = 'psync'

    def __init__(self, node: Node, logLevel: str ='NONE', security: bool = False, sync: str = SYNC_PSYNC,
                 faceType: str = Nfdc.PROTOCOL_UDP, nFaces: int = 3, routingType: str = ROUTING_LINK_STATE,
                 faceDict: Optional[Dict[Node, List[Tuple[str, str, str]]]] = None,
                 infoeditChanges: Optional[List[Union[Tuple[str, str], Tuple[str, str, str]]]] = None):
        """
        Set NLSR NFD application through wrapper on node. Most arguments are directly from nlsr.conf,
        so please reference that documentation for more information.

        :param node: Mininet or Mininet-Wifi node object
        :param logLevel: NLSR log level set as default (default  "NONE")
        :param security: Whether or not to set up signing and packet validation.
               NDN security features are typically disabled in Mini-NDN for performance (default false)
        :param sync: What sync to use with NLSR. PSync is the only one tested, but ndn-svs or chronosync
               may be specified manually (default "psync")
        :param faceType: What protocol to use to create for faces to neighbors during setup.
               UDP faces are typically used in Mini-NDN (default "udp")
        :param nFaces: Number of faces to maintain for each prefix after routing calculations (default 3)
        :param routingType: Whether to use link state or hyperbolic routing. The latter requires additional setup and
               is not recommended for novice users.
        :param faceDict: If not creating faces via the included helper, this contains information on faces
               to use as neighbors. This is helpful for running NLSR in any case where direct links between NDN routers
               are not present in the topology (adhoc or infrastructure wifi, networks using IP switches or routers, etc).
        :param infoeditChanges: Commands passed to infoedit other than the most commonly used arguments.
               These either expect (key, value) (using the `section` command) or otherwise
               (key, value, put|section|delete).
        """
        Application.__init__(self, node)
        try:
            from mn_wifi.node import Node_wifi
            if isinstance(node, Node_wifi) and faceDict == None:
                warn("Wifi nodes need to have faces configured manually. Please see \
                      documentation on provided helper methods.\r\n")
                sys.exit(1)
        except ImportError:
            pass

        self.network = '/ndn/'
        self.node = node
        self.parameters = self.node.params['params']

        if self.parameters.get('nlsr-log-level', None) != None:
            logLevel = self.parameters.get('nlsr-log-level')

        if logLevel in ['NONE', 'WARN', 'INFO', 'DEBUG', 'TRACE']:
            self.envDict = {'NDN_LOG': 'nlsr.*={}'.format(logLevel)}
        else:
            self.envDict = {'NDN_LOG': logLevel}

        self.logFile = 'nlsr.log'
        self.routerName = '/{}C1.Router/cs/{}'.format('%', node.name)
        self.confFile = '{}/nlsr.conf'.format(self.homeDir)
        self.security = security
        self.sync = sync
        self.faceType = faceType
        self.infocmd = 'infoedit -f nlsr.conf'
        # Expected format- node : tuple (node name, IP, cost)
        self.faceDict = faceDict
        self.infoeditManualChanges = infoeditChanges

        self.parameters = self.node.params['params']

        self.nFaces = nFaces
        if routingType == Nlsr.ROUTING_HYPERBOLIC:
            self.hyperbolicState = 'on'
        elif routingType == Nlsr.ROUTING_DRY_RUN:
            self.hyperbolicState = 'dry-run'
        else:
            self.hyperbolicState = 'off'
        self.hyperRadius = self.parameters.get('radius', 0.0)
        self.hyperAngle = self.parameters.get('angle', 0.0)

        if ((self.hyperbolicState == 'on' or self.hyperbolicState == 'dry-run') and
            (self.hyperRadius == 0.0 or self.hyperAngle == 0.0)):
            warn('Hyperbolic coordinates in topology file are either missing or misconfigured.')
            warn('Check that each node has one radius value and one or two angle value(s).')
            sys.exit(1)

        self.neighborLocations = []
        self.interfaceForNeighbor = dict()
        possibleConfPaths = ['/usr/local/etc/ndn/nlsr.conf.sample', '/etc/ndn/nlsr.conf.sample']
        copyExistentFile(node, possibleConfPaths, '{}/nlsr.conf'.format(self.homeDir))

        self.createConfigFile()

        if security and not Minindn.ndnSecurityDisabled:
            self.createKeysAndCertificates()

    def start(self):
        self.createFaces()
        Application.start(self, 'nlsr -f {}'.format(self.confFile), self.logFile, self.envDict)
        Minindn.sleep(1)

    def createFaces(self):
        for location in self.neighborLocations:
            if self.faceType == Nfdc.PROTOCOL_ETHER:
                localIntf = self.interfaceForNeighbor[location]
                Nfdc.createFace(self.node, location, self.faceType, localInterface=localIntf, isPermanent=True)
            else:
                Nfdc.createFace(self.node, location, self.faceType, isPermanent=True)

    @staticmethod
    def createKey(host: Node, name: str, outputFile: Union[str, bytes, os.PathLike]):
        host.cmd('ndnsec-key-gen {} > {}'.format(name, outputFile))

    @staticmethod
    def createCertificate(host: Node, signer: str, keyFile: str, outputFile: Union[str, bytes, os.PathLike] ):
        host.cmd('ndnsec-cert-gen -s {} -r {} > {}'.format(signer, keyFile, outputFile))

    def createKeysAndCertificates(self):
        securityDir = '{}/security'.format(Minindn.workDir)

        if not os.path.exists(securityDir):
            os.mkdir(securityDir)

        rootName = self.network
        rootCertFile = '{}/root.cert'.format(securityDir)
        if not os.path.isfile(rootCertFile):
            # Create root certificate
            sh('ndnsec-key-gen {}'.format(rootName)) # Installs a self-signed cert into the system
            sh('ndnsec-cert-dump -i {} > {}'.format(rootName, rootCertFile))

        # Create necessary certificates for each site
        nodeSecurityFolder = '{}/security'.format(self.homeDir)

        self.node.cmd('mkdir -p {}'.format(nodeSecurityFolder))

        # Create temp folders for remote nodes on this machine (localhost) to store site.key file
        # from RemoteNodes
        if not os.path.exists(nodeSecurityFolder) and \
            isinstance(self.node, RemoteMixin) and self.node.isRemote:
            os.makedirs(nodeSecurityFolder)

        shutil.copyfile('{}/root.cert'.format(securityDir),
                        '{}/root.cert'.format(nodeSecurityFolder))

        # Create site certificate
        siteName = '{}{}-site'.format(self.network, self.node.name)
        siteKeyFile = '{}/site.keys'.format(nodeSecurityFolder)
        siteCertFile = '{}/site.cert'.format(nodeSecurityFolder)
        Nlsr.createKey(self.node, siteName, siteKeyFile)

        # Copy siteKeyFile from remote for ndnsec-cert-gen
        if isinstance(self.node, RemoteMixin) and self.node.isRemote:
            login = 'mininet@{}'.format(self.node.server)
            src = '{}:{}'.format(login, siteKeyFile)
            dst = siteKeyFile
            scp(src, dst)

        # Root key is in root namespace, must sign site key and then install on host
        sh('ndnsec-cert-gen -s {} -r {} > {}'.format(rootName, siteKeyFile, siteCertFile))

        # Copy root.cert and site.cert from localhost to remote host
        if isinstance(self.node, RemoteMixin) and self.node.isRemote:
            login = 'mininet@{}'.format(self.node.server)
            src = '{}/site.cert'.format(nodeSecurityFolder)
            src2 = '{}/root.cert'.format(nodeSecurityFolder)
            dst = '{}:/tmp/'.format(login)
            scp(src, src2, dst)
            self.node.cmd('mv /tmp/*.cert {}'.format(nodeSecurityFolder))

        self.node.cmd('ndnsec-cert-install -f {}'.format(siteCertFile))

        # Create and install operator certificate
        opName = '{}/%C1.Operator/op'.format(siteName)
        opKeyFile = '{}/op.keys'.format(nodeSecurityFolder)
        opCertFile = '{}/op.cert'.format(nodeSecurityFolder)
        Nlsr.createKey(self.node, opName, opKeyFile)
        Nlsr.createCertificate(self.node, siteName, opKeyFile, opCertFile)
        self.node.cmd('ndnsec-cert-install -f {}'.format(opCertFile))

        # Create and install router certificate
        routerName = '{}/%C1.Router/cs/{}'.format(siteName, self.node.name)
        routerKeyFile = '{}/router.keys'.format(nodeSecurityFolder)
        routerCertFile = '{}/router.cert'.format(nodeSecurityFolder)
        Nlsr.createKey(self.node, routerName, routerKeyFile)
        Nlsr.createCertificate(self.node, opName, routerKeyFile, routerCertFile)
        self.node.cmd('ndnsec-cert-install -f {}'.format(routerCertFile))

    def createConfigFile(self):

        self.__editGeneralSection()
        if self.faceDict:
            self.__editNeighborsSectionManual()
        else:
            self.__editNeighborsSection()
        self.__editHyperbolicSection()
        self.__editFibSection()
        self.__editAdvertisingSection()
        self.__editSecuritySection()
        if self.infoeditManualChanges:
            self.__editCustom()

    def __editGeneralSection(self):

        self.node.cmd('{} -s general.network -v {}'.format(self.infocmd, self.network))
        self.node.cmd('{} -s general.site -v /{}-site'.format(self.infocmd, self.node.name))
        self.node.cmd('{} -s general.router -v /%C1.Router/cs/{}'.format(self.infocmd, self.node.name))
        self.node.cmd('{} -s general.state-dir -v {}/log'.format(self.infocmd, self.homeDir))
        self.node.cmd('{} -s general.sync-protocol -v {}'.format(self.infocmd, self.sync))

    def __editNeighborsSection(self):

        self.node.cmd('{} -d neighbors.neighbor'.format(self.infocmd))
        for intf in self.node.intfList():
            link = intf.link
            if not link:
                continue

            node1, node2 = link.intf1.node, link.intf2.node

            # Todo: add some switch support
            if isinstance(node1, Switch) or isinstance(node2, Switch):
                continue

            if node1 == self.node:
                other = node2
                if self.faceType == Nfdc.PROTOCOL_ETHER:
                    location = MACToEther(link.intf2.MAC())
                else:
                    location = link.intf2.IP()
            else:
                other = node1
                if self.faceType == Nfdc.PROTOCOL_ETHER:
                    location = MACToEther(link.intf1.MAC())
                else:
                    location = link.intf1.IP()

            linkCost = intf.params.get('delay', '10ms').replace('ms', '')

            self.neighborLocations.append(location)
            if self.faceType == Nfdc.PROTOCOL_ETHER:
                self.interfaceForNeighbor[location] = intf

            self.node.cmd('{} -a neighbors.neighbor \
                          <<<\'name {}{}-site/%C1.Router/cs/{} face-uri {}://{}\n link-cost {}\''
                          .format(self.infocmd, self.network, other.name, other.name,
                                  self.faceType, location, linkCost))

    def __editNeighborsSectionManual(self):

        self.node.cmd('{} -d neighbors.neighbor'.format(self.infocmd))
        if self.node not in self.faceDict:
            return
        for link in self.faceDict[self.node]:
            nodeName = link[0]
            nodeIP = link[1]
            linkCost = link[2]

            self.node.cmd('{} -a neighbors.neighbor \
                          <<<\'name {}{}-site/%C1.Router/cs/{} face-uri {}://{}\n link-cost {}\''
                          .format(self.infocmd, self.network, nodeName, nodeName,
                                  self.faceType, nodeIP, linkCost))


    def __editHyperbolicSection(self):

        self.node.cmd('{} -s hyperbolic.state -v {}'.format(self.infocmd, self.hyperbolicState))
        self.node.cmd('{} -s hyperbolic.radius -v {}'.format(self.infocmd, self.hyperRadius))
        self.node.cmd('{} -s hyperbolic.angle -v {}'.format(self.infocmd, self.hyperAngle))

    def __editFibSection(self):

        self.node.cmd('{} -s fib.max-faces-per-prefix  -v {}'.format(self.infocmd, self.nFaces))

    def __editAdvertisingSection(self):

        self.node.cmd('{} -d advertising'.format(self.infocmd))
        self.node.cmd('{} -s advertising.{}{}-site/{} -v 0'
                      .format(self.infocmd, self.network, self.node.name, self.node.name))

    def __editSecuritySection(self):

        self.node.cmd('{} -d security.cert-to-publish'.format(self.infocmd))
        if not self.security:
            self.node.cmd('{} -s security.validator.trust-anchor.type -v any'.format(self.infocmd))
            self.node.cmd('{} -d security.validator.trust-anchor.file-name'.format(self.infocmd))
            self.node.cmd('{} -s security.prefix-update-validator.trust-anchor.type -v any'.format(self.infocmd))
            self.node.cmd('{} -d security.prefix-update-validator.trust-anchor.file-name'.format(self.infocmd))
        else:
            self.node.cmd('{} -s security.validator.trust-anchor.file-name -v security/root.cert'.format(self.infocmd))
            self.node.cmd('{} -s security.prefix-update-validator.trust-anchor.file-name -v security/site.cert'.format(self.infocmd))
            self.node.cmd('{} -p security.cert-to-publish -v security/site.cert'.format(self.infocmd))
            self.node.cmd('{} -p security.cert-to-publish -v security/op.cert'.format(self.infocmd))
            self.node.cmd('{} -p security.cert-to-publish -v security/router.cert'.format(self.infocmd))

    def __editCustom(self):
        # EXPECTED FORMAT: [<section>, <key>] OR [<section>, <key>, <operation>]
        # Default behavior will replace all values for section with key
        # Deletion only works for unique keys
        INFOEDIT_COMMANDS = {"put": "-p", "delete": "-d", "section": "-s"}
        for infoeditChange in self.infoeditManualChanges:
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
