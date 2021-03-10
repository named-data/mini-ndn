# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2020, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import time
import os
import configparser
from subprocess import call, check_output, Popen
from sys import exit

from mininet.link import TCLink
from mininet.node import Switch
from mininet.util import ipStr, ipParse
from mininet.log import info, debug

from mn_wifi.topo import Topo as Topo_WiFi
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import WirelessLink

from minindn.minindn import Minindn

class MinindnWifi(Minindn):
    """ Class for handling default args, Mininet-wifi object and home directories """
    def __init__(self, parser=argparse.ArgumentParser(), topo=None, topoFile=None, noTopo=False, link=WirelessLink, **mininetParams):
        """Create Mini-NDN-Wifi object
        parser: Parent parser of Mini-NDN-Wifi parser (use to specify experiment arguments)
        topo: Mininet topo object (optional)
        topoFile: topology file location (optional)
        noTopo: Allows specification of topology after network object is initialized (optional)
        link: Allows specification of default Mininet/Mininet-Wifi link type for connections between nodes (optional)
        mininetParams: Any params to pass to Mininet-WiFi
        """
        self.parser = self.parseArgs(parser)
        self.args = self.parser.parse_args()

        Minindn.workDir = self.args.workDir
        Minindn.resultDir = self.args.resultDir

        self.topoFile = None
        if not topoFile:
            # Args has default topology if none specified
            self.topoFile = self.args.topoFile
        else:
            self.topoFile = topoFile

        if topo is None and not noTopo:
            try:
                info('Using topology file {}\n'.format(self.topoFile))
                self.topo = self.processTopo(self.topoFile)
            except configparser.NoSectionError as e:
                info('Error reading config file: {}\n'.format(e))
                sys.exit(1)
        else:
            self.topo = topo

        if not noTopo:
            self.net = Mininet_wifi(topo=self.topo, ifb=self.args.ifb, link=link, **mininetParams)
        else:
            self.net = Mininet_wifi(ifb=self.args.ifb, link=link, **mininetParams)

        # Prevents crashes running mixed topos
        nodes = self.net.stations + self.net.hosts + self.net.cars
        self.initParams(nodes)

        try:
            process = Popen(['ndnsec-get-default', '-k'], stdout=PIPE, stderr=PIPE)
            output, error = process.communicate()
            if process.returncode == 0:
                Minindn.ndnSecurityDisabled = '/dummy/KEY/-%9C%28r%B8%AA%3B%60' in output
                info('Dummy key chain patch is installed in ndn-cxx. Security will be disabled.\n')
            else:
                debug(error)
        except:
            pass

        self.cleanups = []

    @staticmethod
    def parseArgs(parent):
        parser = argparse.ArgumentParser(prog='minindn-wifi', parents=[parent], add_help=False)

        # nargs='?' required here since optional argument
        parser.add_argument('topoFile', nargs='?', default='/usr/local/etc/mini-ndn/singleap-topology.conf',
                            help='If no template_file is given, topologies/wifi/singleap-topology.conf will be used.')

        parser.add_argument('--work-dir', action='store', dest='workDir', default='/tmp/minindn',
                            help='Specify the working directory; default is /tmp/minindn')

        parser.add_argument('--result-dir', action='store', dest='resultDir', default=None,
                            help='Specify the full path destination folder where experiment results will be moved')

        parser.add_argument('--mobility',action='store_true',dest='mobility',default=False,
                            help='Enable custom mobility for topology (defined in topology file)')

        parser.add_argument('--model-mob',action='store_true',dest='modelMob',default=False,
                            help='Enable model mobility for topology (defined in topology file)')

        parser.add_argument('--ifb',action='store_true',dest='ifb',default=False,
                            help='Simulate delay on receiver-side by use of virtual IFB devices (see docs)')

        return parser

    @staticmethod
    def processTopo(topoFile):
        config = configparser.ConfigParser(delimiters=' ')
        config.read(topoFile)
        topo = Topo_WiFi()

        items = config.items('stations')
        debug("Stations")
        for item in items:
            debug(item[0].split(':'))
            name = item[0].split(':')[0]
            params = {}
            for param in item[1].split(' '):
                    if param == "_":
                        continue
                    key = param.split('=')[0]
                    value = param.split('=')[1]
                    if key in ['range']:
                        value = int(value)
                    params[key] = value

            topo.addStation(name, **params)

        try:
            debug("Switches")
            items = config.items('switches')
            for item in items:
                debug(item[0].split(':'))
                name = item[0].split(':')[0]
                topo.addSwitch(name)
        except configparser.NoSectionError:
            debug("Switches are optional")
            pass

        try:
            debug("APs")
            items = config.items('accessPoints')
            for item in items:
                debug(item[0].split(':'))
                name = item[0].split(':')[0]
                ap_params = {}
                for param in item[1].split(' '):
                    if param == "_":
                        continue
                    key = param.split('=')[0]
                    value = param.split('=')[1]
                    if key in ['range']:
                        value = int(value)
                    ap_params[key] = value
                topo.addAccessPoint(name, **ap_params)
        except configparser.NoSectionError:
            debug("APs are optional")
            pass

        items = config.items('links')
        debug("Links")
        for item in items:
            link = item[0].split(':')
            debug(link)
            params = {}
            for param in item[1].split(' '):
                if param == "_":
                    continue
                key = param.split('=')[0]
                value = param.split('=')[1]
                if key in ['bw', 'jitter', 'max_queue_size']:
                    value = int(value)
                if key == 'loss':
                    value = float(value)
                params[key] = value

            topo.addLink(link[0], link[1], **params)

        return topo

    def startMobility(self, max_x=1000, max_y=1000, **kwargs):
        """ Method to run a basic mobility setup on your net"""
        self.net.plotGraph(max_x=max_x, max_y=max_y)
        self.net.startMobility(**kwargs)

    def startMobilityModel(self, max_x=1000, max_y=1000, **kwargs):
        """ Method to run a mobility model on your net until exited"""
        self.net.plotGraph(max_x=max_x, max_y=max_y)
        self.net.setMobilityModel(**kwargs)