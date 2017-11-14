#!/usr/bin/python

""" This program used to build ad hoc network.
propagation Model function must be call just before
calling of function for configuring wifi node.
So, need to this program. """
import sys
import datetime
import random # This line for graph
from subprocess import call
from mininet.net import Mininet
from mini_ndn.ndn.ndn_host import NdnHost
from mininet.link import TCLink
from mininet.node import Controller
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
    vndn = Mininet(host=NdnHost, station=NdnHost, controller=Controller, ssid=ssid, channel=channel,
                   mode=mode, enable_wmediumd=wmediumd, enable_interference=interference)


    # Possibly we should clean up here and/or validate
    # the topo
    if vndn.cleanup:
        pass

    info('*** Creating adhoc network\n')
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
                vndn.addController('c%d' % i, cls, ip='127.0.0.1', port=6633)
            info('c%d' %i)

    info('\n*** Adding hosts and stations:\n')
    x=0
    for hostName in vndnTopo.hosts():
        min = random.randint(1, 10)
        max = random.randint(11, 30)
        if 'car' in str(hostName):
            vndn.addCar(hostName, wlans=1,  min_speed=min, max_speed=max, **vndnTopo.nodeInfo(hostName))
        else:
            vndn.addHost(hostName, **vndnTopo.nodeInfo(hostName))
        x=x+1
        info(hostName + ' ')

    info('\n*** Adding accessPoints and Road Sides Units:\n')
#    for switchName in vndnTopo.accessPoints():
#        # A bit ugly: add batch parameter if appropriate
#        params = vndnTopo.nodeInfo(switchName)
#        cls = params.get('cls', vndn.switch)
#        if hasattr(cls, 'batchStartup'):
#            params.setdefault('batch', True)
#        if 'rsu' in str(switchName):
#            vndn.addAccessPoint(switchName, ssid="vanet-ssid", passwd='123456789a', encrypt='wpa2', **params)
#        else:
#            vndn.addSwitch(switchName, **params)
#            info(switchName + ' ')

    rsu1 = vndn.addAccessPoint('rsu1', ssid='vanet-ssid', mac='00:00:00:11:00:01', mode='g', channel='1', passwd='123456789a', encrypt='wpa2', position='3279.02,3736.27,0')
    rsu2 = vndn.addAccessPoint('rsu2', ssid='vanet-ssid', mac='00:00:00:11:00:02', mode='g', channel='6', passwd='123456789a', encrypt='wpa2', position='2320.82,3565.75,0')
    rsu3 = vndn.addAccessPoint('rsu3', ssid='vanet-ssid', mac='00:00:00:11:00:03', mode='g', channel='11', passwd='123456789a', encrypt='wpa2', position='2806.42,3395.22,0')
    rsu4 = vndn.addAccessPoint('rsu4', ssid='vanet-ssid', mac='00:00:00:11:00:04', mode='g', channel='1', passwd='123456789a', encrypt='wpa2', position='3332.62,3253.92,0')

    info('\n*** Configuring propagation model...\n')
    # this code line must be put here
    vndn.propagationModel("logDistancePropagationLossModel", exp=2.5)
    #Only can use this propagation model

    print "*** Setting bgscan"
    vndn.setBgscan(signal=-45, s_inverval=5, l_interval=10)

    print "*** Configuring Propagation Model"
    vndn.propagationModel("logDistancePropagationLossModel", exp=2)


    info('\n*** Configuring wifi nodes...\n')
    vndn.configureWifiNodes()

    info('\n*** Adding link(s):\n')
    #for station in vndn.stations:
    #    vndn.addHoc(station, ssid = ssid, mode = mode)
    i=0
    while i<len(vndn.accessPoints)-1:
        vndn.addLink(vndn.accessPoints[i], vndn.accessPoints[i+1])
        i=i+1

    "Available Options: sumo, sumo-gui"
    vndn.useExternalProgram('sumo-gui', config_file='map.sumocfg')


    t2 = datetime.datetime.now()
    delta = t2 - t
    info('Setup time: ' + str(delta.seconds) + '\n')

    print "*** Starting network"
    vndn.build()
    #vndn.Controller.start()

    # Load experiment

    if experimentName is not None:
        print("Loading experiment: %s" % experimentName)

        experimentArgs = {
            "isWiFi":True,
            "net": adhocnet,
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

