#!/usr/bin/python

""" This program used to build ad hoc network.
propagation Model function must be call just before
calling of function for configuring wifi node.
So, need to this program. """
import os
import sys
import datetime
import random # This line for graph
from subprocess import call
from mininet.net import Mininet
from mini_ndn.ndn.ndn_host import NdnHost
from mininet.link import TCLink
from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, output, info
from mininet.examples.cluster import MininetCluster, RoundRobinPlacer, ClusterCleanup
from mininet.wifiLink import Association
from ndnwifi.wifiutil import MiniNdnWifiCLI
import matplotlib.pyplot as plt
from ndn.nfd import Nfd
from ndnwifi import WifiExperimentManager


# build_adhocnet function() is usd to replace BuildFromTopo() function in mininet/net.py
def build_sumo_vndn(vndnTopo, ssid, channel, mode, wmediumd, interference,
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
        #sumo_vndn = Mininet(host=CpuLimitedNdnHost, station=CpuLimitedNdnHost, link=TCLink,controller=Controller,
        #                   ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                   enable_interference=interference)
#    elif vndnTopo.isTCLink == True and vndnTopo.isLimited == False:
#        if cluster is not None:
        #    mn = partial(MininetCluster, servers=servers, placement=placement)
        #    sumo_vndn = mn(host=NdnHost, station=NdnHost, link=TCLink,controller=Controller,
        #                  ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                  enable_interference=interference)
#        else:
        #    sumo_vndn = Mininet(host=NdnHost, station=NdnHost, link=TCLink, controller=Controller,
        #                       ssid=ssid, channel=channel, mode=mode, enable_wmediumd=wmediumd,
        #                       enable_interference=interference)

#    elif vndnTopo.isTCLink == False and vndnTopo.isLimited == True:
        #sumo_vndn = Mininet(host=CpuLimitedNdnHost, station=CpuLimitedNdnHost, controller=Controller, ssid=ssid, channel=channel,
        #               mode=mode, enable_wmediumd=wmediumd, enable_interference=interference)

#    else:
    sumo_vndn = Mininet(host=NdnHost, station=NdnHost, car=NdnHost, controller=Controller, switch=OVSKernelSwitch ,ssid=ssid, channel=channel,
                   mode=mode, enable_wmediumd=wmediumd, enable_interference=interference)


    # Possibly we should clean up here and/or validate
    # the topo
    if sumo_vndn.cleanup:
        pass

    info('*** Creating adhoc network\n')
    if not sumo_vndn.controllers and sumo_vndn.controller:
        # Add a default controller
        info('*** Adding controller\n')
        classes = sumo_vndn.controller
        if not isinstance(classes, list):
            classes = [ classes ]
        for i, cls in enumerate(classes):
            # Allow Controller objects because nobody understands partial()
            if isinstance(cls, Controller):
                sumo_vndn.addController(cls)
            else:
                sumo_vndn.addController('c%d' % i, cls, ip='127.0.0.1', port=6633)
            info('c%d' %i)

    info('\n*** Adding hosts and stations:\n')
    x=0
    for carName in vndnTopo.hosts():
        if 'car' in str(carName):
            sumo_vndn.addCar(carName,ip='10.0.0.%s/8'% (x + 1), wlans=1, range=50, **vndnTopo.nodeInfo(carName))
        else:
            sumo_vndn.addHost(carName, **vndnTopo.nodeInfo(carName))
        x=x+1
        info(carName + ' ')

    info('\n*** Adding accessPoints and Road Sides Units:\n')
#    for switchName in vndnTopo.accessPoints():
#        # A bit ugly: add batch parameter if appropriate
#        params = vndnTopo.nodeInfo(switchName)
#        cls = params.get('cls', sumo_vndn.switch)
#        if hasattr(cls, 'batchStartup'):
#            params.setdefault('batch', True)
#        if 'rsu' in str(switchName):
#            sumo_vndn.addAccessPoint(switchName, ssid="vanet-ssid", passwd='123456789a', encrypt='wpa2', **params)
#        else:
#            sumo_vndn.addSwitch(switchName, **params)
#            info(switchName + ' ')

    rsu1 = sumo_vndn.addAccessPoint('rsu1', ssid='vanet-ssid', mac='00:00:00:11:00:01', mode='g', channel='1', passwd='123456789a', 
                               encrypt='wpa2', position='3279.02,3736.27,0',range=100)
    rsu2 = sumo_vndn.addAccessPoint('rsu2', ssid='vanet-ssid', mac='00:00:00:11:00:02', mode='g', channel='6', passwd='123456789a', 
                               encrypt='wpa2', position='2320.82,3565.75,0',range=100)
    rsu3 = sumo_vndn.addAccessPoint('rsu3', ssid='vanet-ssid', mac='00:00:00:11:00:03', mode='g', channel='11', passwd='123456789a',
                               encrypt='wpa2', position='2806.42,3395.22,0', range=100)
    rsu4 = sumo_vndn.addAccessPoint('rsu4', ssid='vanet-ssid', mac='00:00:00:11:00:04', mode='g', channel='1', passwd='123456789a',
                               encrypt='wpa2', position='3332.62,3253.92,0', range=100)

    info('\n*** Configuring propagation model...\n')
    sumo_vndn.propagationModel(model="logDistance", exp=4.5) # An error that tx power is negative if negiexp=2.5

    print "*** Setting bgscan"
    sumo_vndn.setBgscan(signal=-45, s_inverval=5, l_interval=10)

    print "*** Configuring Propagation Model"
    sumo_vndn.propagationModel(model="logDistance", exp=4)


    info('\n*** Configuring wifi nodes...\n')
    sumo_vndn.configureWifiNodes()

    info('\n*** Adding link(s):\n')
    i=0
    while i<len(sumo_vndn.aps)-1:
        sumo_vndn.addLink(sumo_vndn.aps[i], sumo_vndn.aps[i+1])
        i=i+1

    "Available Options: sumo, sumo-gui"
    sumo_vndn.useExternalProgram('sumo-gui', config_file='map.sumocfg')
    print "starting network....."
    sumo_vndn.build()
    sumo_vndn.controllers[0].start()
    for rsu in sumo_vndn.aps:
        rsu.start(sumo_vndn.controllers)

    i = 201
    for sw in sumo_vndn.carsSW:
        sw.start(sumo_vndn.controllers)
        os.system('ip addr add 10.0.0.%s dev %s' % (i, sw))
        i += 1

    i = 1
    j = 2
    k = 1
    for car in sumo_vndn.cars:
        car.setIP('192.168.0.%s/24' % k, intf='%s-wlan0' % car)
        car.setIP('192.168.1.%s/24' % i, intf='%s-eth0' % car)
        car.cmd('ip route add 10.0.0.0/8 via 192.168.1.%s' % j)
        i += 2
        j += 2
        k += 1

    i = 1
    j = 2
    for v in sumo_vndn.carsSTA:
        v.setIP('192.168.1.%s/24' % j, intf='%s-eth0' % v)
        #v.setIP('10.0.0.%s/24' % i, intf='%s-mp0' % v) # This is for v2v communication in mesh mode
        v.setIP('10.0.0.%s/24' % i, intf='%s-wlan0' % v) #This is for v2v communication in ad hoc mode
        v.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        i += 1
        j += 2


    for v1 in sumo_vndn.carsSTA:
        i = 1
        j = 1
        for v2 in sumo_vndn.carsSTA:
            if v1 != v2:
                v1.cmd('route add -host 192.168.1.%s gw 10.0.0.%s' % (j, i))
            i += 1
            j += 2


    # Load experiment

    if experimentName is not None:
        print("Loading experiment: %s" % experimentName)

        experimentArgs = {
            "isWiFi": True,
            "isVndn": False,
            "isSumoVndn": True,
            "net": sumo_vndn,
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
    MiniNdnWifiCLI(sumo_vndn)

    print "*** Stopping network"
    sumo_vndn.stop()

    print('Cleaning up...')
    call(["nfd-stop"])
    call(["sudo", "mn", "--clean"])
    sys.exit(1)

