#!/usr/bin/python

from ndn.experiments.experiment import Experiment
from ndn.nlsr import Nlsr

import time

class MultipleFailureExperiment(Experiment):

    def __init__(self, args):

        self.PING_COLLECTION_TIME_BEFORE_FAILURE = 60

        self.FAILURE_INTERVAL = 60
        self.RECOVERY_INTERVAL = 60

        # This is the number of pings required to make it through the full experiment
        nInitialPings = self.PING_COLLECTION_TIME_BEFORE_FAILURE + len(args["net"].hosts)*(self.FAILURE_INTERVAL + self.RECOVERY_INTERVAL)
        print("Scheduling with %s initial pings" % nInitialPings)

        args["nPings"] = nInitialPings

        Experiment.__init__(self, args)

    def failNode(self, host):
        print("Bringing %s down" % host.name)
        host.nfd.stop()

    def recoverNode(self, host):
        print("Bringing %s up" % host.name)
        host.nfd.start()
        host.nlsr.start()
        host.nfd.setStrategy("/ndn/edu", self.strategy)
        host.cmd("ndnpingserver /ndn/edu/" + str(host) + " > ping-server &")

    def run(self):
        self.startPings()

        # After the pings are scheduled, collect pings for 1 minute
        time.sleep(self.PING_COLLECTION_TIME_BEFORE_FAILURE)

        nNodesRemainingToFail = len(self.net.hosts)

        # Fail and recover each node
        for host in self.net.hosts:
            # Fail the node
            self.failNode(host)

            # Stay in failure state for FAILURE_INTERVAL
            time.sleep(self.FAILURE_INTERVAL)

            # Bring the node back up
            self.recoverNode(host)

            # Number of pings required to reach the end of the test
            nPings = self.RECOVERY_INTERVAL + nNodesRemainingToFail*(self.FAILURE_INTERVAL + self.RECOVERY_INTERVAL)
            nNodesRemainingToFail = nNodesRemainingToFail - 1

            # Wait for NFD and NLSR to fully recover
            time.sleep(1)
            print("Scheduling with %s remaining pings" % nPings)

            # Restart pings
            for other in self.net.hosts:
                # Do not ping self
                if host.name != other.name:
                    self.ping(host, other, nPings)

            time.sleep(self.RECOVERY_INTERVAL)

Experiment.register("multiple-failure", MultipleFailureExperiment)
