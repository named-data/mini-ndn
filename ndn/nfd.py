#!/usr/bin/env python

import time

class Nfd:
    STRATEGY_BEST_ROUTE_V3 = "best-route/%FD%03"
    STRATEGY_NCC = "ncc"

    def __init__(self, node):
        self.node = node
        self.isRunning = False

        # Create home directory for a node
        node.cmd("cd /tmp && mkdir %s" % node.name)
        node.cmd("cd %s" % node.name)

        self.homeFolder = "/tmp/%s" % node.name
        self.confFile = "%s/%s.conf" % (self.homeFolder, node.name)
        self.logFile = "%s/%s.log" % (self.homeFolder, node.name)
        self.sockFile = "/var/run/%s.sock" % node.name
        self.ndnFolder = "%s/.ndn" % self.homeFolder
        self.clientConf = "%s/client.conf" % self.ndnFolder

        # Copy nfd.conf file from /usr/local/etc/mini-ndn to the node's home
        node.cmd("sudo cp /usr/local/etc/mini-ndn/nfd.conf %s" % self.confFile)

        # Open the conf file and change socket file name
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.confFile))

        # Make NDN folder
        node.cmd("sudo mkdir %s" % self.ndnFolder)

        # Copy the client.conf file and change the unix socket
        node.cmd("sudo cp /usr/local/etc/mini-ndn/client.conf.sample %s" % self.clientConf)
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.clientConf))

        # Change home folder
        node.cmd("export HOME=%s" % self.homeFolder)

    def start(self):
        if self.isRunning is True:
            try:
                os.kill(int(self.processId), 0)
            except OSError:
                self.isRunning = False

        if self.isRunning is False:
            self.node.cmd("sudo nfd --config %s 2>> %s &" % (self.confFile, self.logFile))
            self.processId = self.node.cmd("echo $!")[:-1]

            time.sleep(2)

            self.isRunning = True

    def stop(self):
        if self.isRunning is True:
            self.node.cmd("sudo kill %s" % self.processId)

            self.isRunning = False

    def setStrategy(self, name, strategy):
        self.node.cmd("nfdc set-strategy %s ndn:/localhost/nfd/strategy/%s" % (name, strategy))
        time.sleep(0.5)
