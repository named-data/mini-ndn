#!/usr/bin/env python
import os

class NdnApplication:
    def __init__(self, node):
        self.node = node
        self.isRunning = False

    def start(self, command):
        if self.isRunning is True:
            try:
                os.kill(int(self.processId), 0)
            except OSError:
                self.isRunning = False

        if self.isRunning is False:
            self.node.cmd(command)
            self.processId = self.node.cmd("echo $!")[:-1]

            self.isRunning = True

    def stop(self):
        if self.isRunning:
            self.node.cmd("sudo kill %s" % self.processId)

            self.isRunning = False
