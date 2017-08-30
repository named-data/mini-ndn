#!/usr/bin/python

"""This example shows how to emulate a MANET (mobile ad hoc network)"""

import random
from mininet.node import Controller
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

def topology():
    "Create a network."
    net = Mininet(controller=Controller, enable_wmediumd=True, enable_interference=True)
    print "*** Creating nodes"
    sta1 = net.addStation('sta1', mac='02:00:00:00:00:01')
    sta2 = net.addStation('sta2', mac='02:00:00:00:00:02')
    sta3 = net.addStation('sta3', mac='02:00:00:00:00:03')
    sta4 = net.addStation('sta4', mac='02:00:00:00:00:04')
    sta5 = net.addStation('sta5', mac='02:00:00:00:00:05')
    print "*** Configuring wifi nodes"
#    net.propagationModel('friisPropagationLossModel', sL=2)
    net.propagationModel("logDistancePropagationLossModel", exp=5)
    net.configureWifiNodes()

    print "*** Creating links"
    net.addHoc(sta1, ssid='adhocNet', mode='g')
    net.addHoc(sta2, ssid='adhocNet', mode='g')
    net.addHoc(sta3, ssid='adhocNet', mode='g')
    net.addHoc(sta4, ssid='adhocNet', mode='g')
    net.addHoc(sta5, ssid='adhocNet', mode='g')

    print "*** Starting network"
    net.build()
    net.plotGraph(max_x=100, max_y=100)
    net.seed(random.randint(0, 100))
    net.startMobility(startTime=0, model='RandomWayPoint', max_x=100, max_y=100, min_v=0.5, max_v=0.8)

    print "*** Running CLI"
    CLI(net)

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()

