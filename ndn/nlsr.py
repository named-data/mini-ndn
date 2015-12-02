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

from mininet.clean import sh

from ndn.ndn_application import NdnApplication

import os
import shutil
import textwrap

class Nlsr(NdnApplication):
    def __init__(self, node):
        NdnApplication.__init__(self, node)
        self.routerName = "/%sC1.Router/cs/%s" % ('%', node.name)
        self.confFile = "%s/nlsr.conf" % node.homeFolder

        # Make directory for log file
        self.logDir = "%s/log" % node.homeFolder
        node.cmd("mkdir %s" % self.logDir)

        # Configure basic router information in nlsr.conf based on host name
        node.cmd("sudo sed -i 's|router .*|router %s|g' %s" % (self.routerName, self.confFile))
        node.cmd("sudo sed -i 's|log-dir .*|log-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|seq-dir .*|seq-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|prefix .*netlab|prefix /ndn/edu/%s|g' %s" % (node.name, self.confFile))

    def start(self):
        NdnApplication.start(self, "nlsr -d -f {} &".format(self.confFile))

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
        rootName = "/ndn"
        sh("ndnsec-keygen {} > {}/root.keys".format(rootName, securityDir))
        sh("ndnsec-certgen -N {} -p {} {}/root.keys > {}/root.cert".format(rootName, rootName, securityDir, securityDir))

        # Create necessary certificates for each site
        for host in net.hosts:
            nodeSecurityFolder = "{}/security".format(host.homeFolder)

            if not os.path.exists(nodeSecurityFolder):
                os.mkdir(nodeSecurityFolder)

            shutil.copyfile("{}/root.cert".format(securityDir), "{}/root.cert".format(nodeSecurityFolder))

            # Create site certificate
            siteName = "/ndn/edu"
            siteKeyFile = "{}/site.keys".format(nodeSecurityFolder)
            siteCertFile = "{}/site.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, siteName, siteKeyFile)

            # Root key is in root namespace, must sign site key and then install on host
            sh("ndnsec-certgen -N {} -s {} -p {} {} > {}".format(siteName, rootName, siteName, siteKeyFile, siteCertFile))
            host.cmd("ndnsec-cert-install -f {}".format(siteCertFile))

            # Create operator certificate
            opName = "{}/%C1.Operator/op".format(siteName)
            opKeyFile = "{}/op.keys".format(nodeSecurityFolder)
            opCertFile = "{}/op.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, opName, opKeyFile)
            Nlsr.createCertificate(host, opName, opName, opKeyFile, opCertFile, signer=siteName)

            # Create router certificate
            routerName = "{}/%C1.Router/cs/{}".format(siteName, host.name)
            routerKeyFile = "{}/router.keys".format(nodeSecurityFolder)
            routerCertFile = "{}/router.cert".format(nodeSecurityFolder)
            Nlsr.createKey(host, routerName, routerKeyFile)
            Nlsr.createCertificate(host, routerName, routerName, routerKeyFile, routerCertFile, signer=opName)

class NlsrConfigGenerator:

    ROUTING_LINK_STATE = "ls"
    ROUTING_HYPERBOLIC = "hr"

    def __init__(self, node, isSecurityEnabled):
        node.cmd("sudo cp /usr/local/etc/mini-ndn/nlsr.conf nlsr.conf")
        self.node = node
        self.isSecurityEnabled = isSecurityEnabled

        parameters = node.nlsrParameters

        self.nFaces = parameters.get("max-faces-per-prefix", 3)
        self.hyperbolicState = parameters.get("hyperbolic-state", "off")
        self.hyperRadius = parameters.get("radius", 0.0)
        self.hyperAngle = parameters.get("angle", 0.0)
        self.logLevel = parameters.get("nlsr-log-level", "DEBUG")

    def createConfigFile(self):

        filePath = "%s/nlsr.conf" % self.node.homeFolder

        configFile = open(filePath, 'r')
        oldContent = configFile.read()
        configFile.close()

        newContent = oldContent.replace("$GENERAL_SECTION", self.__getGeneralSection())
        newContent = newContent.replace("$NEIGHBORS_SECTION", self.__getNeighborsSection())
        newContent = newContent.replace("$HYPERBOLIC_SECTION", self.__getHyperbolicSection())
        newContent = newContent.replace("$FIB_SECTION", self.__getFibSection())
        newContent = newContent.replace("$ADVERTISING_SECTION", self.__getAdvertisingSection())
        newContent = newContent.replace("$SECURITY_SECTION", self.__getSecuritySection())

        configFile = open(filePath, 'w')
        configFile.write(newContent)
        configFile.close()

    def __getConfig(self):

        config =  self.__getGeneralSection()
        config += self.__getNeighborsSection()
        config += self.__getHyperbolicSection()
        config += self.__getFibSection()
        config += self.__getAdvertisingSection()
        config += self.__getSecuritySection()

        return config

    def __getGeneralSection(self):

        general =  "general\n"
        general += "{\n"
        general += "  network /ndn/\n"
        general += "  site /edu\n"
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
                neighbors += "  name /ndn/edu/%C1.Router/cs/" + other.name + "\n"
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
        advertising += "  prefix /ndn/edu/" + self.node.name + "\n"
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
                            p-regex ^([^<NLSR><LSA>]*)<NLSR><LSA>(<>*)<><><><>$
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
