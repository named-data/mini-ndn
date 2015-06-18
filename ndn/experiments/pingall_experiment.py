#!/usr/bin/python

from ndn.experiments.experiment import Experiment

import time

class PingallExperiment(Experiment):

    def __init__(self, args):

        Experiment.__init__(self, args)
        self.COLLECTION_PERIOD_BUFFER = 10


    def run(self):
        self.startPings()

        # For pingall experiment sleep for the number of pings + some offset
        time.sleep(self.nPings + self.COLLECTION_PERIOD_BUFFER)

Experiment.register("pingall", PingallExperiment)
