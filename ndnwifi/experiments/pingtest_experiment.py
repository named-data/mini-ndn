#!/usr/bin/python

from ndnwifi.experiments.wifiexperiment import wifiExperiment

class TestExperiment(wifiExperiment):
    def __init__(self, args):
        wifiExperiment.__init__(self, args)
    def setup(self):
        if self.isWiFi:
            for sta in self.net.stations:
                print "pingtest_experiment.py----------------------------", sta
                sta.cmd("ndnpingserver sta.name &")
        else:
            for host in self.net.hosts:
                print "pingtest_experiment.py----------------------------", host
                host.cmd("ndnpingserver host.name &")
    def run(self):
        if self.isWiFi:
            for sta in self.net.stations:
                sta.cmd("ndnping sta.name -c3 > status.txt")
        else:
            for host in self.net.hosts:
                host.cmd("ndnping host.name -c3 > status.txt")

wifiExperiment.register("test", TestExperiment)

