#!/usr/bin/python

import time
import sys

class Experiment:

    def __init__(self, net, nodes, convergenceTime, nPings, strategy):
        self.net = net
        self.nodes = nodes
        self.convergenceTime = convergenceTime
        self.nPings = nPings
        self.strategy = strategy

    def start(self):
        self.setup()
        self.run()

    def setup(self):
        for host in self.net.hosts:
            # Set strategy
            host.nfd.setStrategy("/ndn/edu", self.strategy)

            # Start ping server
            host.cmd("ndnpingserver /ndn/edu/" + str(host) + " > ping-server &")

            # Create folder to store ping data
            host.cmd("mkdir ping-data")

        # Wait for convergence time period
        print "Waiting " + str(self.convergenceTime) + " seconds for convergence..."
        time.sleep(self.convergenceTime)
        print "...done"

        # To check whether all the nodes of NLSR have converged
        didNlsrConverge = True

        # Checking for convergence
        for host in self.net.hosts:
            statusRouter = host.cmd("nfd-status -b | grep /ndn/edu/%C1.Router/cs/")
            statusPrefix = host.cmd("nfd-status -b | grep /ndn/edu/")
            didNodeConverge = True
            for node in self.nodes.split(","):
                    if ("/ndn/edu/%C1.Router/cs/" + node) not in statusRouter:
                        didNodeConverge = False
                        didNlsrConverge = False
                    if str(host) != node and ("/ndn/edu/" + node) not in statusPrefix:
                        didNodeConverge = False
                        didNlsrConverge = False

            host.cmd("echo " + str(didNodeConverge) + " > convergence-result &")

        if didNlsrConverge:
            print("NLSR has successfully converged.")
        else:
            print("NLSR has not converged. Exiting...")
            for host in self.net.hosts:
                host.nfd.stop()
            sys.exit(1)

    def ping(self, source, dest, nPings):
        # Use "&" to run in background and perform parallel pings
        print "Scheduling ping(s) from %s to %s" % (source.name, dest.name)
        source.cmd("ndnping -t -c "+ str(nPings) + " /ndn/edu/" + dest.name + " >> ping-data/" + dest.name + ".txt &")
        time.sleep(0.2)

    def startPings(self):
        for host in self.net.hosts:
            for other in self.net.hosts:
                # Do not ping self
                if host.name != other.name:
                    self.ping(host, other, self.nPings)

