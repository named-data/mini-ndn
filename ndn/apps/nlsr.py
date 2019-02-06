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

from mininet.clean import sh
from mininet.examples.cluster import RemoteMixin
from mininet.log import info

from ndn.ndn_application import NdnApplication
from ndn.util import ssh, scp, copyExistentFile
from ndn.apps.nfdc import Nfdc

import shutil
import os
import textwrap
from subprocess import call
import time

NETWORK="/ndn/"

class Nlsr(NdnApplication):
    def __init__(self, node, options):
        NdnApplication.__init__(self, node)
        self.config = NlsrConfigGenerator(node, options)

        self.node = node
        self.routerName = "/{}C1.Router/cs/{}".format('%', node.name)
        self.confFile = "{}/nlsr.conf".format(node.homeFolder)

        # Make directory for log file
        self.logDir = "{}/log".format(node.homeFolder)
        self.node.cmd("mkdir {}".format(self.logDir))

    def start(self, sleepTime = 1):
        self.node.cmd("export NDN_LOG=nlsr.*={}".format(self.node.params["params"].get("nlsr-log-level", "DEBUG")))
        NdnApplication.start(self, "nlsr -f {} > log/nlsr.log 2>&1 &".format(self.confFile))
        time.sleep(sleepTime)

    def createFaces(self):
        for ip in self.config.neighborIPs:
            Nfdc.createFace(self.node, ip, self.config.faceType, isPermanent=True)

    @staticmethod
    def createKey(host, name, outputFile):
        host.cmd("ndnsec-keygen {} > {}".format(name, outputFile))

    @staticmethod
    def createCertificate(host, signer, keyFile, outputFile):
        host.cmd("ndnsec-certgen -s {} -r {} > {}".format(signer, keyFile, outputFile))

    @staticmethod
    def createKeysAndCertificates(net, workDir):
        securityDir = "{}/security".format(workDir)

        if not os.path.exists(securityDir):
            os.mkdir(securityDir)

        # Create root certificate
        rootName = NETWORK
        sh("ndnsec-keygen {}".format(rootName)) # Installs a self-signed cert into the system
        sh("ndnsec-cert-dump -i {} > {}/root.cert".format(rootName, securityDir))

        # Create necessary certificates for each site
        for host in net.hosts:
            nodeSecurityFolder = "{}/security".format(host.homeFolder)

            host.cmd("mkdir -p %s" % nodeSecurityFolder)

            # Create temp folders for remote nodes on this machine (localhost) to store site.key file
            # from RemoteNodes
            if not os.path.exists(nodeSecurityFolder) and isinstance(host, RemoteMixin) and host.isRemote:
                os.makedirs(nodeSecurityFolder)

            shutil.copyfile("{}/root.cert".format(securityDir), "{}/root.cert".format(nodeSecurityFolder))

            # Create site certificate
            siteName = "{}{}-site".format(NETWORK, host.name)
            siteKeyFile = "{}/site.keys".format(nodeSecurityFolder)
            siteCertFile = "{}/site.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, siteName, siteKeyFile)

            # Copy siteKeyFile from remote for ndnsec-certgen
            if isinstance(host, RemoteMixin) and host.isRemote:
                login = "mininet@{}".format(host.server)
                src = "{}:{}".format(login, siteKeyFile)
                dst = siteKeyFile
                scp(src, dst)

            # Root key is in root namespace, must sign site key and then install on host
            sh("ndnsec-certgen -s {} -r {} > {}".format(rootName, siteKeyFile, siteCertFile))

            # Copy root.cert and site.cert from localhost to remote host
            if isinstance(host, RemoteMixin) and host.isRemote:
                login = "mininet@{}".format(host.server)
                src = "{}/site.cert".format(nodeSecurityFolder)
                src2 = "{}/root.cert".format(nodeSecurityFolder)
                dst = "{}:/tmp/".format(login)
                scp(src, src2, dst)
                host.cmd("mv /tmp/*.cert {}".format(nodeSecurityFolder))

            host.cmd("ndnsec-cert-install -f {}".format(siteCertFile))

            # Create and install operator certificate
            opName = "{}/%C1.Operator/op".format(siteName)
            opKeyFile = "{}/op.keys".format(nodeSecurityFolder)
            opCertFile = "{}/op.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, opName, opKeyFile)
            Nlsr.createCertificate(host, siteName, opKeyFile, opCertFile)
            host.cmd("ndnsec-cert-install -f {}".format(opCertFile))

            # Create and install router certificate
            routerName = "{}/%C1.Router/cs/{}".format(siteName, host.name)
            routerKeyFile = "{}/router.keys".format(nodeSecurityFolder)
            routerCertFile = "{}/router.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, routerName, routerKeyFile)
            Nlsr.createCertificate(host, opName, routerKeyFile, routerCertFile)
            host.cmd("ndnsec-cert-install -f {}".format(routerCertFile))

class NlsrConfigGenerator:

    ROUTING_LINK_STATE = "ls"
    ROUTING_HYPERBOLIC = "hr"

    def __init__(self, node, options):
        self.node = node
        self.isSecurityEnabled = options.nlsrSecurity
        self.faceType = options.faceType
        self.infocmd = "infoedit -f nlsr.conf"

        parameters = node.params["params"]

        self.nFaces = options.nFaces
        if options.routingType == "hr":
            self.hyperbolicState = "on"
        elif options.routingType == "dry":
            self.hyperbolicState = "dry-run"
        else:
            self.hyperbolicState = "off"
        self.hyperRadius = parameters.get("radius", 0.0)
        self.hyperAngle = parameters.get("angle", 0.0)

        if ((self.hyperbolicState == "on" or self.hyperbolicState == "dry-run") and
            (self.hyperRadius == 0.0 or self.hyperAngle == 0.0)):
                info('Hyperbolic coordinates in topology file are either missing or misconfigured.')
                info('Check that each node has one radius value and one or two angle value(s).')
                sys.exit(1)

        self.neighborIPs = []
        possibleConfPaths = ["/usr/local/etc/ndn/nlsr.conf.sample", "/etc/ndn/nlsr.conf.sample"]
        copyExistentFile(node, possibleConfPaths, "{}/nlsr.conf".format(self.node.homeFolder))

        self.createConfigFile()

    def createConfigFile(self):

        self.__editGeneralSection()
        self.__editNeighborsSection()
        self.__editHyperbolicSection()
        self.__editFibSection()
        self.__editAdvertisingSection()
        self.__editSecuritySection()

    def __editGeneralSection(self):

        self.node.cmd("{} -s general.network -v {}".format(self.infocmd, NETWORK))
        self.node.cmd("{} -s general.site -v /{}-site".format(self.infocmd, self.node.name))
        self.node.cmd("{} -s general.router -v /%C1.Router/cs/{}".format(self.infocmd, self.node.name))
        self.node.cmd("{} -s general.state-dir -v {}/log".format(self.infocmd, self.node.homeFolder))

    def __editNeighborsSection(self):

        self.node.cmd("{} -d neighbors.neighbor".format(self.infocmd))
        for intf in self.node.intfList():
            link = intf.link
            if link:
                node1, node2 = link.intf1.node, link.intf2.node

                if node1 == self.node:
                    other = node2
                    ip = other.IP(str(link.intf2))
                else:
                    other = node1
                    ip = other.IP(str(link.intf1))

                linkCost = intf.params.get("delay", "10ms").replace("ms", "")

                Nfdc.createFace(self.node, ip, self.faceType, isPermanent=True)
                self.neighborIPs.append(ip)

                self.node.cmd("{} -a neighbors.neighbor \
                              <<<\'name {}{}-site/%C1.Router/cs/{} face-uri {}://{}\n link-cost {}\'"
                              .format(self.infocmd, NETWORK, other.name, other.name, self.faceType, ip, linkCost))

    def __editHyperbolicSection(self):

        self.node.cmd("{} -s hyperbolic.state -v {}".format(self.infocmd, self.hyperbolicState))
        self.node.cmd("{} -s hyperbolic.radius -v {}".format(self.infocmd, self.hyperRadius))
        self.node.cmd("{} -s hyperbolic.angle -v {}".format(self.infocmd, self.hyperAngle))

    def __editFibSection(self):

        self.node.cmd("{} -s fib.max-faces-per-prefix  -v {}".format(self.infocmd, self.nFaces))

    def __editAdvertisingSection(self):

        self.node.cmd("{} -d advertising.prefix".format(self.infocmd))
        self.node.cmd("{} -s advertising.prefix -v {}{}-site/{}"
                      .format(self.infocmd, NETWORK, self.node.name, self.node.name))

    def __editSecuritySection(self):

        self.node.cmd("{} -d security.cert-to-publish".format(self.infocmd))
        if self.isSecurityEnabled is False:
            self.node.cmd("{} -s security.validator.trust-anchor.type -v any".format(self.infocmd))
            self.node.cmd("{} -d security.validator.trust-anchor.file-name".format(self.infocmd))
            self.node.cmd("{} -s security.prefix-update-validator.trust-anchor.type -v any".format(self.infocmd))
            self.node.cmd("{} -d security.prefix-update-validator.trust-anchor.file-name".format(self.infocmd))
        else:
            self.node.cmd("{} -s security.validator.trust-anchor.file-name -v security/root.cert".format(self.infocmd))
            self.node.cmd("{} -s security.prefix-update-validator.trust-anchor.file-name -v security/site.cert".format(self.infocmd))
            self.node.cmd("{} -p security.cert-to-publish -v security/site.cert".format(self.infocmd))
            self.node.cmd("{} -p security.cert-to-publish -v security/op.cert".format(self.infocmd))
            self.node.cmd("{} -p security.cert-to-publish -v security/router.cert".format(self.infocmd))
