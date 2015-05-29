#!/usr/bin/env python
import os

class Nlsr:
    def __init__(self, node):
        self.node = node
        self.routerName = "/%sC1.Router/cs/%s" % ('%', node.name)
        self.confFile = "/tmp/%s/nlsr.conf" % node.name
        self.isRunning = False

        # Make directory for log file
        self.logDir = "/tmp/%s/log" % node.name
        node.cmd("mkdir %s" % self.logDir)

        # Configure basic router information in nlsr.conf based on host name
        node.cmd("sudo sed -i 's|router .*|router %s|g' %s" % (self.routerName, self.confFile))
        node.cmd("sudo sed -i 's|log-dir .*|log-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|seq-dir .*|seq-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|prefix .*netlab|prefix /ndn/edu/%s|g' %s" % (node.name, self.confFile))

    def start(self):
        if self.isRunning is True:
            try:
                os.kill(int(self.processId), 0)
            except OSError:
                self.isRunning = False

        if self.isRunning is False: 
            self.node.cmd("nlsr -d")
            self.processId = self.node.cmd("echo $!")[:-1]

            self.isRunning = True

    def stop(self):
        if self.isRunning:
            self.node.cmd("sudo kill %s" % self.processId)

            self.isRunning = False

class NlsrConfigGenerator:

    ROUTING_LINK_STATE = "ls"
    ROUTING_HYPERBOLIC = "hr"

    def __init__(self, node):
        node.cmd("sudo cp /usr/local/etc/mini-ndn/nlsr.conf nlsr.conf")
        self.node = node

        parameters = node.nlsrParameters

        self.nFaces = parameters.get("max-faces-per-prefix", 3)
        self.hyperbolicState = parameters.get("hyperbolic-state", "off")
        self.hyperRadius = parameters.get("radius", 0.0)
        self.hyperAngle = parameters.get("angle", 0.0)

    def createConfigFile(self):

        filePath = "/tmp/%s/nlsr.conf" % self.node.name

        configFile = open(filePath, 'r')
        oldContent = configFile.read()
        configFile.close()

        newContent = oldContent.replace("$GENERAL_SECTION", self.__getGeneralSection())
        newContent = newContent.replace("$NEIGHBORS_SECTION", self.__getNeighborsSection())
        newContent = newContent.replace("$HYPERBOLIC_SECTION", self.__getHyperbolicSection())
        newContent = newContent.replace("$FIB_SECTION", self.__getFibSection())
        newContent = newContent.replace("$ADVERTISING_SECTION", self.__getAdvertisingSection())

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
        general += "  log-level DEBUG\n"
        general += "  log-dir /tmp/" + self.node.name + "/log\n"
        general += "  seq-dir /tmp/" + self.node.name + "/log\n"
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

        security =  "security\n"
        security += "{\n"
        security += "  validator\n"
        security += "  {\n"
        security += "    trust-anchor\n"
        security += "    {\n"
        security += "      type any\n"
        security += "    }\n"
        security += "  }\n"
        security += "}\n"

        return security
