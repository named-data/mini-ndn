#!/usr/bin/python

""" This program used to build mobile ad hoc network """
import datetime
import random # add this line for graph
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mini_ndn.ndn.ndn_host import NdnHost
from mininet.node import Controller
from mininet.log import setLogLevel, output, info
from mininet.wifiLink import Association
from ndnwifi.wifiutil import MiniNdnWifiCLI
# build_manet function() is usd to replace BuildFromTopo() function in mininet/net.py 
def build_manet(manetTopo, channel):
    """Create a mobile ad hoc network from a topology object
           At the end of this function, everything should be connected
           and up..
    topo:topology object according to network topology configure file;
    channel: channel parames according to user selection. 
    """
    manet = Mininet(host=NdnHost, station=NdnHost, channel=channel, ssid='adhocNet',
                  controller=Controller, enable_wmediumd=True, enable_interference=True)
    t = datetime.datetime.now()
    #topology object manetTopo can't make as  params in Mininet object definination. 
    manet.plotGraph(max_x=100, max_y=100)
    manet.seed(random.randint(0, 100))

    cls = Association
    cls.printCon = False
    # Possibly we should clean up here and/or validate
    # the topo
    if manet.cleanup:
        pass

    info('*** Creating MANET network\n')
    if not manet.controllers and manet.controller:
        # Add a default controller
        info('*** Adding controller\n')
        classes = manet.controller
        if not isinstance(classes, list):
            classes = [ classes ]
        for i, cls in enumerate(classes):
            # Allow Controller objects because nobody understands partial()
            if isinstance(cls, Controller):
                manet.addController(cls)
            else:
                manet.addController('c%d' % i, cls)
            info('c%d' %i)

    info('\n*** Adding hosts and stations:\n')
    for hostName in manetTopo.hosts():
        if 'sta' in str(hostName):
            manet.addStation(hostName, **manetTopo.nodeInfo(hostName))
        else:
            manet.addHost(hostName, **manetTopo.nodeInfo(hostName))
        info(hostName + ' ')

    info('\n*** Configuring wifi nodes...\n')
    # this code line must play here
    manet.propagationModel("logDistancePropagationLossModel", exp=5)
    manet.configureWifiNodes()

    info('\n*** Adding link(s):\n')
    for station in manet.stations:
        manet.addHoc(station, ssid = 'adhocNet', mode = 'g')
    t2 = datetime.datetime.now()
    delta = t2 - t
    info('Setup time: ' + str(delta.seconds) + '\n')

    print "*** Starting network"
    manet.build()
    # this code line must play here
    manet.startMobility(startTime=0, model='RandomWayPoint', max_x=100, max_y=100, min_v=0.5, max_v=0.8)

    """Running CLI....."""
    MiniNdnWifiCLI(manet)
    print "*** Stopping network"
    manet.stop()
