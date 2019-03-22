#!/usr/bin/python

"""Sample file for SUMO

***Requirements***:

sumo
sumo-gui"""

import os
import sys
from subprocess import call

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import UserAP
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd, adhoc, mesh
from mn_wifi.wmediumdConnector import interference

from ndn.ndn_host import NdnHost
from ndn.nfd import Nfd
from ndn.apps.nfdc import Nfdc
from ndnwifi_host import NdnStation, NdnCar
from ndnwifi.wifiutil import MiniNdnWifiCLI

def build_sumo_vndn(vndnTopo, ssid, channel, mode, wmediumd, interference,cluster, placement, servers, tunnelType, ctime, nPings, pctTraffic, experimentName, nlsrSecurity):

    "Create a network."
    net = Mininet_wifi(host=NdnHost, station=NdnStation, car=NdnCar, controller=Controller, accessPoint=UserAP, link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")

    for carName in vndnTopo.hosts():
	if 'car' in str(carName):
		net.addCar(carName, wlans=1, **vndnTopo.nodeInfo(carName))
		#net.addCar(carName, **vndnTopo.nodeInfo(carName))

    e1 = net.addAccessPoint('e1', ssid='vanet-ssid', mac='00:00:00:11:00:01',
                            mode='g', channel='1', passwd='123456789a',
                            encrypt='wpa2', position='3279.02,3736.27,0')
    e2 = net.addAccessPoint('e2', ssid='vanet-ssid', mac='00:00:00:11:00:02',
                            mode='g', channel='6', passwd='123456789a',
                            encrypt='wpa2', position='2320.82,3565.75,0')
    
    c1 = net.addController('c1')

    info("*** Setting bgscan\n")
    net.setBgscan(signal=-45, s_inverval=5, l_interval=10)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.addLink(e1, e2)
    
    for car in net.cars:
        #net.addLink(car, intf=car.params['wlan'][1],
        #            cls=mesh, ssid='mesh-ssid', channel=5)
	net.addLink(car, cls=adhoc, ssid='mesh-ssid', mode = 'g', channel=5)

    net.useExternalProgram(program=sumo, port=8813,
                           config_file='map.sumocfg')

    info("*** Starting network\n")
    net.build()
    c1.start()
    e1.start([c1])
    e2.start([c1])
    
    '''i = 1
    for car in net.cars:
        car.setIP('192.168.0.%s/24' % str(i),
                  intf='%s-wlan0' % car)
        car.setIP('192.168.1.%s/24' % str(i),
                  intf='%s-mp1' % car)
	i+=1	
    '''
    for car in net.cars:
	car.nfd = Nfd(car, 65536)
	car.nfd.start()
	#Nfdc.setStrategy(car, "/vanet", "vanet")
	#cmd = "nfdc strategy set /vanet ndn:/localhost/nfd/strategy/vanet/"

    info("*** Running CLI\n")
    MiniNdnWifiCLI(net)

    info("*** Stopping network\n")
    net.stop()

    info('Cleaning up...')
    call(["nfd-stop"])
    call(["sudo", "mn", "--clean"])
    call(["sudo", "pkill", "sumo"])
    sys.exit(1)
