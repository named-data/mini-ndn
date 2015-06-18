#!/usr/bin/python

from ndn.experiments.experiment import Experiment
from ndn.nlsr import Nlsr

import time

class FailureExperiment(Experiment):

    def __init__(self, args):
        args["nPings"] = 300
        Experiment.__init__(self, args)

        self.PING_COLLECTION_TIME_BEFORE_FAILURE = 60
        self.PING_COLLECTION_TIME_AFTER_RECOVERY = 90

    def run(self):
        self.startPings()

        # After the pings are scheduled, collect pings for 1 minute
        time.sleep(self.PING_COLLECTION_TIME_BEFORE_FAILURE)

        # Bring down CSU
        for host in self.net.hosts:
            if host.name == "csu":
                print("Bringing CSU down")
                host.nfd.stop()
                break

        # CSU is down for 2 minutes
        time.sleep(120)

        # Bring CSU back up
        for host in self.net.hosts:
            if host.name == "csu":
                print("Bringing CSU up")
                host.nfd.start()
                host.nlsr.start()
                host.nfd.setStrategy("/ndn/edu", self.strategy)
                host.cmd("ndnpingserver /ndn/edu/" + str(host) + " > ping-server &")

        # Collect pings for more seconds after CSU is up
        time.sleep(self.PING_COLLECTION_TIME_AFTER_RECOVERY)

Experiment.register("failure", FailureExperiment)
