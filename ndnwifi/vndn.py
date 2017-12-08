#!/usr/bin/python

""" This program used to build ad hoc network.
propagation Model function must be call just before
calling of function for configuring wifi node.
So, need to this program. """
import os
import sys
import datetime
import random
from subprocess import call
from mininet.net import Mininet
from mini_ndn.ndn.ndn_host import NdnHost
from mininet.link import TCLink
from mininet.node import Controller, OVSKernelSwitch, OVSKernelAP
from mininet.log import setLogLevel, output, info
from mininet.examples.cluster import MininetCluster, RoundRobinPlacer, ClusterCleanup
from mininet.wifiLink import Association
from ndnwifi.wifiutil import MiniNdnWifiCLI
import matplotlib.pyplot as plt
from ndn.nfd import Nfd
from ndnwifi import WifiExperimentManager


# build_adhocnet function() is usd to replace BuildFromTopo() function in mininet/net.py
def build_vndn(vndnTopo, ssid, channel, mode, wmediumd, interference,
               cluster, placement, servers, tunnelType, ctime, nPings, pctTraffic, experimentName, nlsrSecurity):
    """Create an ad hoc network from a topology object
       At the end of this function, everything should be connected
       and up..
       adhocTopo:topology object that be builded according to a file of network topology configure;
       isManet: mobile ad hoc network;
       isAdhoc: stationary ad hoc network;
       channel: channel parames;
       ssid: service set identifier;
       wmedimd:param for 802.11 simulation tool;
       interferce:param for 802.11 simulation tool;
       placement:
       servers:
       tunnelType:
       the following paramters are for experiments.
       ctime: specific time that the nentwork covergence;
       nPings: number that perform 
    """
    t = datetime.datetime.now()
    cls = Association
    cls.printCon = False
    #build a wire network or a wirelesswork network.
    #topology object adhocTopo can't make as  params in Mininet object definination.
#    if vndnTopo.isTCLink == True and vndnTopo.isLimited == True:
        #vndn = Mininet(host=CpuLimitedNdnHost, station=CpuLimitedNdnHost, link=TCLink,controller=Controller,
        #                   ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                   enable_interference=interference)
#    elif vndnTopo.isTCLink == True and vndnTopo.isLimited == False:
#        if cluster is not None:
        #    mn = partial(MininetCluster, servers=servers, placement=placement)
        #    vndn = mn(host=NdnHost, station=NdnHost, link=TCLink,controller=Controller,
        #                  ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                  enable_interference=interference)
#        else:
        #    vndn = Mininet(host=NdnHost, station=NdnHost, link=TCLink, controller=Controller,
        #                       ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                       enable_interference=interference)

#    elif vndnTopo.isTCLink == False and vndnTopo.isLimited == True:
        #vndn = Mininet(host=CpuLimitedNdnHost, station=CpuLimitedNdnHost, controller=Controller, ssid=ssid, channel=channel,
        #               mode=mode, enable_wmediumd=wmediumd, enable_interference=interference)

#    else:
    vndn = Mininet(host=NdnHost, station=NdnHost, car=NdnHost, controller=Controller, switch=OVSKernelSwitch, ssid=ssid, channel=channel,
                    mode=mode, enable_wmediumd=wmediumd, enable_interference=interference)


    # Possibly we should clean up here and/or validate
    # the topo
    if vndn.cleanup:
        pass

    info('*** Creating ndn based vehicle network\n')
    if not vndn.controllers and vndn.controller:
        # Add a default controller
        info('*** Adding controller\n')
        classes = vndn.controller
        if not isinstance(classes, list):
            classes = [ classes ]
        for i, cls in enumerate(classes):
            # Allow Controller objects because nobody understands partial()
            if isinstance(cls, Controller):
                vndn.addController(cls)
            else:
                vndn.addController('c%d' % i, cls)
            info('c%d' %i)

    info('\n*** Adding cars and car stations:\n')
    x=0
    for carName in vndnTopo.hosts():
        min = random.randint(1, 5)
        max = random.randint(5, 15)
        if 'car' in str(carName):
            vndn.addCar(carName, ip='10.0.0.%s/8'% (x + 1), wlans=1, range='100', 
                        min_speed=min, max_speed=max, **vndnTopo.nodeInfo(carName))
        else:
            vndn.addHost(carName, **vndnTopo.nodeInfo(carName))
        x=x+1
        info(carName + ' ')

    info('\n*** Adding Road Sides Units:\n')
    channelValueList = [1, 6, 11]
    i=0
    for accessPointName in vndnTopo.accessPoints():
        # A bit ugly: add batch parameter if appropriate
        i = i+1
        #randomly select a channel value
        channelValue = channelValueList[random.randint(0, len(channelValueList)-1)]
        params = vndnTopo.nodeInfo(accessPointName)
        cls = params.get('cls', vndn.accessPoint)
        if hasattr(cls, 'batchStartup'):
            params.setdefault('batch', True)
        if 'rsu' in str(accessPointName):
            vndn.addAccessPoint(accessPointName, ssid="RSU1%s" %i, range='50', mode='g', channel='%s' %channelValue, **params)
        else:
            vndn.addSwitch(accessPointName, **params)
            info(accessPointName + ' ')
        info(accessPointName + ' ')

    info('\n*** Configuring propagation model...\n')
    # this code line must be put here
    vndn.propagationModel(model="logDistance", exp=4.5)
    #Only can use this propagation model

    info('\n*** Configuring wifi nodes...\n')
    vndn.configureWifiNodes()

    info('\n*** Adding links......\n')
    for srcName, dstName, params in vndnTopo.links(sort=True, withInfo=True):
        vndn.addLink(**params)
        info('(%s, %s) ' % (srcName, dstName))
    info('\n')

    print "*** Starting network"
    vndn.plotGraph(max_x=500, max_y=500)

    """Number of Roads"""
    vndn.roads(10)

    """Start Mobility"""
    # this code line must be put here
    vndn.startMobility(startTime=0)

    print "start network......"
    vndn.build()
    vndn.controllers[0].start()
    for rsu in vndn.aps:
        rsu.start(vndn.controllers)

    i = 201
    for sw in vndn.carsSW:
        sw.start(vndn.controllers)
        os.system('ip addr add 10.0.0.%s dev %s' % (i, sw))
        i += 1

    i = 1
    j = 2
    k = 1
    for car in vndn.cars:
        car.setIP('192.168.0.%s/24' % k, intf='%s-wlan0' % car)
        car.setIP('192.168.1.%s/24' % i, intf='%s-eth0' % car)
        car.cmd('ip route add 10.0.0.0/8 via 192.168.1.%s' % j)
        i += 2
        j += 2
        k += 1

    i = 1
    j = 2
    for v in vndn.carsSTA:
        v.setIP('192.168.1.%s/24' % j, intf='%s-eth0' % v)
        #v.setIP('10.0.0.%s/24' % i, intf='%s-mp0' % v) # This is for v2v communication in mesh mode
        v.setIP('10.0.0.%s/24' % i, intf='%s-wlan0' % v) #This is for v2v communication in ad hoc mode
        v.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        i += 1
        j += 2


    for v1 in vndn.carsSTA:
        i = 1
        j = 1
        for v2 in vndn.carsSTA:
            if v1 != v2:
                v1.cmd('route add -host 192.168.1.%s gw 10.0.0.%s' % (j, i))
            i += 1
            j += 2


    # Load experiment

    if experimentName is not None:
        print("Loading experiment: %s" % experimentName)

        experimentArgs = {
            "isWiFi": True,
            "isVndn": True,
            "isSumoVndn": False,
            "net": vndn,
            "ctime": ctime,
            "nPings": nPings,
            "strategy": Nfd.STRATEGY_BEST_ROUTE,
            "pctTraffic": pctTraffic,
            "nlsrSecurity": nlsrSecurity
        }

        experiment = WifiExperimentManager.create(experimentName, experimentArgs)

        if experiment is not None:
            experiment.start()
        else:
            print("ERROR: Experiment '%s' does not exist" % experimentName)
            return


    """Running CLI....."""
    MiniNdnWifiCLI(vndn)

    print "*** Stopping network"
    vndn.stop()

    print('Cleaning up...')
    call(["nfd-stop"])
    call(["sudo", "mn", "--clean"])
    sys.exit(1)

