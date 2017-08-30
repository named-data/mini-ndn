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
    sta1 = net.addStation('sta1')
    sta2 = net.addStation('sta2')
    sta3 = net.addStation('sta3')
    sta4 = net.addStation('sta4')
    sta5 = net.addStation('sta5')
    print "*** Configuring wifi nodes"
#    net.propagationModel('friisPropagationLossModel', sL=2)
    net.propagationModel("logDistancePropagationLossModel", exp=5)
    net.configureWifiNodes()

    print "*** Creating links"
    net.addMesh(sta1, ssid='meshNet', mode='g')
    net.addMesh(sta2, ssid='meshNet', mode='g')
    net.addMesh(sta3, ssid='meshNet', mode='g')
    net.addMesh(sta4, ssid='meshNet', mode='g')
    net.addMesh(sta5, ssid='meshNet', mode='g')

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

