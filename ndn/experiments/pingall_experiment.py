#!/usr/bin/python

from ndn.experiments.experiment import Experiment

import time

class PingallExperiment(Experiment):

    def __init__(self, net, nodes, convergenceTime, nPings, strategy):

        Experiment.__init__(self, net, nodes, convergenceTime, nPings, strategy)
        self.COLLECTION_PERIOD_BUFFER = 10


    def run(self):
        self.startPings()

        # For pingall experiment sleep for the number of pings + some offset
        time.sleep(self.nPings + self.COLLECTION_PERIOD_BUFFER)
