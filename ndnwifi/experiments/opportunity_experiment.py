#!/usr/bin/python
import re
import time
import sys
from itertools import cycle
from subprocess import call
import random
from ndnwifi.experiments.wifiexperiment import wifiExperiment

class OpportunityExperiment(wifiExperiment):
    def __init__(self, args):
        wifiExperiment.__init__(self, args)
        self.producerName=" "
        self.consumerName=" "
    def setup(self):
        # create Fib
        self.createFib()

        # Randomly select a producuer
        self.producerName=self.net.stations[random.randrange(1, len(self.net.stations), 1)]

        print "The randomly seleted producer %s is producing a content chunck..." % self.producerName
        self.producerName.cmd("echo 'hello UoM!' | ndnpoke -f /ndnwifi/hello >opportunity-producer.txt &")
        #self.producerName.cmd("ndnpingserver /ndnwifi/sw >opportunity-producer.txt &")

    def run(self):
        # Randomly select a consumer
        wileFlag=True
        while wileFlag:
            self.consumerName=self.net.stations[random.randrange(1, len(self.net.stations), 1)]
            if self.consumerName != self.producerName:
                wileFlag=False
        i=1
        print "The randomly seleted consumer %s will send %s interest packets. waiting ...." % (self.consumerName, str(self.nPings))
        while i<=self.nPings:
            print "%s send the %s interest packet ..." % (self.consumerName, str(i))
            #self.consumerName.cmd("ndnping -t -c1 " + "/ndnwifi/sw" + " >> peek-data/" + str(self.consumerName) + ".txt &")
            self.producerName.cmd("echo 'hello UoM!' | ndnpoke -f /ndnwifi/hello >opportunity-producer.txt &")
            self.consumerName.cmd("ndnpeek -p /ndnwifi/hello" + " >> peek-data/" + str(self.consumerName) + ".txt &")
            time.sleep(3)
            i=i+1

wifiExperiment.register("opportunity", OpportunityExperiment)

