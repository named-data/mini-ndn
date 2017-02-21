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

from mininet.clean import sh
from mininet.examples.cluster import RemoteMixin

from ndn.ndn_application import NdnApplication
from ndn.util import ssh, scp

import shutil
import os
import textwrap
from subprocess import call

NETWORK="/ndn/"

class Nlsr(NdnApplication):
    def __init__(self, node):
        NdnApplication.__init__(self, node)
        self.routerName = "/%sC1.Router/cs/%s" % ('%', node.name)
        self.confFile = "%s/nlsr.conf" % node.homeFolder

        # Make directory for log file
        self.logDir = "%s/log" % node.homeFolder
        node.cmd("mkdir %s" % self.logDir)

    def start(self):
        # Removed & at the end, was giving key not found error
        # This way NLSR is daemonized fully before continuing
        NdnApplication.start(self, "nlsr -d -f {}".format(self.confFile))

    @staticmethod
    def createKey(host, name, outputFile):
        host.cmd("ndnsec-keygen {} > {}".format(name, outputFile))

    @staticmethod
    def createCertificate(host, name, prefix, keyFile, outputFile, signer=None):
        if signer is None:
            host.cmd("ndnsec-certgen -N {} -p {} {} > {}".format(name, prefix, keyFile, outputFile))
        else:
            host.cmd("ndnsec-certgen -N {} -p {} -s {} {} > {}".format(name, prefix, signer, keyFile, outputFile))

    @staticmethod
    def createKeysAndCertificates(net, workDir):
        securityDir = "{}/security".format(workDir)

        if not os.path.exists(securityDir):
            os.mkdir(securityDir)

        # Create root certificate
        rootName = NETWORK
        sh("ndnsec-keygen {} > {}/root.keys".format(rootName, securityDir))
        sh("ndnsec-certgen -N {} -p {} {}/root.keys > {}/root.cert".format(rootName, rootName, securityDir, securityDir))

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
            sh("ndnsec-certgen -N {} -s {} -p {} {} > {}".format(siteName, rootName, siteName, siteKeyFile, siteCertFile))

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
            Nlsr.createCertificate(host, opName, opName, opKeyFile, opCertFile, signer=siteName)
            host.cmd("ndnsec-cert-install -f {}".format(opCertFile))

            # Create and install router certificate
            routerName = "{}/%C1.Router/cs/{}".format(siteName, host.name)
            routerKeyFile = "{}/router.keys".format(nodeSecurityFolder)
            routerCertFile = "{}/router.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, routerName, routerKeyFile)
            Nlsr.createCertificate(host, routerName, routerName, routerKeyFile, routerCertFile, signer=opName)
            host.cmd("ndnsec-cert-install -f {}".format(routerCertFile))

class NlsrConfigGenerator:

    ROUTING_LINK_STATE = "ls"
    ROUTING_HYPERBOLIC = "hr"

    def __init__(self, node, isSecurityEnabled):
        self.node = node
        self.isSecurityEnabled = isSecurityEnabled

        parameters = node.nlsrParameters

        self.nFaces = parameters.get("max-faces-per-prefix", 3)
        self.hyperbolicState = parameters.get("hyperbolic-state", "off")
        self.hyperRadius = parameters.get("radius", 0.0)
        self.hyperAngle = parameters.get("angle", 0.0)
        self.logLevel = parameters.get("nlsr-log-level", "DEBUG")

    def createConfigFile(self):

        tmp_conf = "/tmp/nlsr.conf"

        configFile = open(tmp_conf, 'w')
        configFile.write(self.__getConfig())
        configFile.close()

        # If this node is a remote node scp the nlsr.conf file to its /tmp/nlsr.conf
        if isinstance(self.node, RemoteMixin) and self.node.isRemote:
            login = "mininet@%s" % self.node.server
            src = tmp_conf
            dst = "%s:%s" % (login, tmp_conf)
            scp(src, dst)

        # Copy nlsr.conf to home folder
        self.node.cmd("mv %s nlsr.conf" % tmp_conf)

    def __getConfig(self):

        config  = self.__getGeneralSection() + "\n"
        config += self.__getNeighborsSection() + "\n"
        config += self.__getHyperbolicSection() + "\n"
        config += self.__getFibSection() + "\n"
        config += self.__getAdvertisingSection() + "\n"
        config += self.__getSecuritySection()

        return config

    def __getGeneralSection(self):

        general =  "general\n"
        general += "{\n"
        general += "  network {}\n".format(NETWORK)
        general += "  site /{}-site\n".format(self.node.name)
        general += "  router /%C1.Router/cs/" + self.node.name + "\n"
        general += "  log-level " + self.logLevel + "\n"
        general += "  log-dir " + self.node.homeFolder + "/log\n"
        general += "  seq-dir " + self.node.homeFolder + "/log\n"
        general += "}\n"

        return general

    def __getNeighborsSection(self):

        neighbors =  "neighbors\n"
        neighbors += "{\n"

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

                neighbors += "neighbor\n"
                neighbors += "{\n"
                neighbors += "  name " + NETWORK + other.name + "-site/%C1.Router/cs/" + other.name + "\n"
                neighbors += "  face-uri udp://" + str(ip) + "\n"
                neighbors += "  link-cost " + linkCost + "\n"
                neighbors += "}\n"

        neighbors += "}\n"

        return neighbors

    def __getHyperbolicSection(self):

        hyper =  "hyperbolic\n"
        hyper += "{\n"
        hyper += "state %s\n" % self.hyperbolicState
        hyper += "radius " + str(self.hyperRadius) + "\n"
        hyper += "angle " + str(self.hyperAngle) + "\n"
        hyper += "}\n"

        return hyper

    def __getFibSection(self):

        fib =  "fib\n"
        fib += "{\n"
        fib += "  max-faces-per-prefix " + str(self.nFaces) + "\n"
        fib += "}\n"

        return fib

    def __getAdvertisingSection(self):

        advertising =  "advertising\n"
        advertising += "{\n"
        advertising += "  prefix "+ NETWORK + self.node.name + "-site/" + self.node.name + "\n"
        advertising += "}\n"

        return advertising

    def __getSecuritySection(self):
        if self.isSecurityEnabled is False:
            security = textwrap.dedent("""\
                security
                {
                  validator
                  {
                    trust-anchor
                    {
                      type any
                    }
                  }
                  prefix-update-validator
                  {
                    trust-anchor
                    {
                      type any
                    }
                  }
                }""")
        else:
            security = textwrap.dedent("""\
                security
                {
                  validator
                  {
                    rule
                    {
                      id "NSLR Hello Rule"
                      for data
                      filter
                      {
                        type name
                        regex ^[^<NLSR><INFO>]*<NLSR><INFO><><>$
                      }
                      checker
                      {
                        type customized
                        sig-type rsa-sha256
                        key-locator
                        {
                          type name
                          hyper-relation
                          {
                            k-regex ^([^<KEY><NLSR>]*)<NLSR><KEY><ksk-.*><ID-CERT>$
                            k-expand \\\\1
                            h-relation equal
                            p-regex ^([^<NLSR><INFO>]*)<NLSR><INFO><><>$
                            p-expand \\\\1
                          }
                        }
                      }
                    }

                    rule
                    {
                      id "NSLR LSA Rule"
                      for data
                      filter
                      {
                        type name
                        regex ^[^<NLSR><LSA>]*<NLSR><LSA>
                      }
                      checker
                      {
                        type customized
                        sig-type rsa-sha256
                        key-locator
                        {
                          type name
                          hyper-relation
                          {
                            k-regex ^([^<KEY><NLSR>]*)<NLSR><KEY><ksk-.*><ID-CERT>$
                            k-expand \\\\1
                            h-relation equal
                            p-regex ^<localhop>([^<NLSR><LSA>]*)<NLSR><LSA>(<>*)<><><><>$
                            p-expand \\\\1\\\\2
                          }
                        }
                      }
                    }

                    rule
                    {
                      id "NSLR Hierarchy Exception Rule"
                      for data
                      filter
                      {
                        type name
                        regex ^[^<KEY><%C1.Router>]*<%C1.Router>[^<KEY><NLSR>]*<KEY><ksk-.*><ID-CERT><>$
                      }
                      checker
                      {
                        type customized
                        sig-type rsa-sha256
                        key-locator
                        {
                          type name
                          hyper-relation
                          {
                            k-regex ^([^<KEY><%C1.Operator>]*)<%C1.Operator>[^<KEY>]*<KEY><ksk-.*><ID-CERT>$
                            k-expand \\\\1
                            h-relation equal
                            p-regex ^([^<KEY><%C1.Router>]*)<%C1.Router>[^<KEY>]*<KEY><ksk-.*><ID-CERT><>$
                            p-expand \\\\1
                          }
                        }
                      }
                    }

                    rule
                    {
                      id "NSLR Hierarchical Rule"
                      for data
                      filter
                      {
                        type name
                        regex ^[^<KEY>]*<KEY><ksk-.*><ID-CERT><>$
                      }
                      checker
                      {
                        type hierarchical
                        sig-type rsa-sha256
                      }
                    }

                    trust-anchor
                    {
                      type file
                      file-name "security/root.cert"
                    }
                  }

                  prefix-update-validator
                  {
                    rule
                    {
                      id "NLSR ControlCommand Rule"
                      for interest
                      filter
                      {
                        type name
                        regex ^<localhost><nlsr><prefix-update>[<advertise><withdraw>]<>$
                      }
                      checker
                      {
                        type customized
                        sig-type rsa-sha256
                        key-locator
                        {
                          type name
                          regex ^([^<KEY><%C1.Operator>]*)<%C1.Operator>[^<KEY>]*<KEY><ksk-.*><ID-CERT>$
                        }
                      }
                    }

                    rule
                    {
                      id "NLSR Hierarchy Rule"
                      for data
                      filter
                      {
                        type name
                        regex ^[^<KEY>]*<KEY><ksk-.*><ID-CERT><>$
                      }
                      checker
                      {
                        type hierarchical
                        sig-type rsa-sha256
                      }
                    }

                    trust-anchor
                    {
                      type file
                      file-name "security/site.cert"
                    }
                  }
                  ; cert-to-publish "security/root.cert"  ; optional, a file containing the root certificate
                                                 ; Only the router that is designated to publish the root cert
                                                 ; needs to specify this

                  cert-to-publish "security/site.cert"  ; optional, a file containing the site certificate
                                                 ; Only the router that is designated to publish the site cert
                                                 ; needs to specify this

                  cert-to-publish "security/op.cert" ; optional, a file containing the operator certificate
                                                    ; Only the router that is designated to publish the operator
                                                    ; cert needs to specify this

                  cert-to-publish "security/router.cert"  ; required, a file containing the router certificate.
                }""")

        return security
