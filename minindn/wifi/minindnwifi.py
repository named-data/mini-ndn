# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2021, The University of Memphis,
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

import os
import argparse
import sys
import configparser
from subprocess import Popen, PIPE

from mininet.log import info, debug

from mn_wifi.topo import Topo as Topo_WiFi
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import WirelessLink

from minindn.minindn import Minindn
from minindn.helpers.nfdc import Nfdc

class MinindnWifi(Minindn):
    """ Class for handling default args, Mininet-wifi object and home directories """
    def __init__(self, parser=argparse.ArgumentParser(), topo=None, topoFile=None, noTopo=False,
                 link=WirelessLink, workDir=None, **mininetParams):
        """
        Create Mini-NDN-Wifi object
        parser: Parent parser of Mini-NDN-Wifi parser (use to specify experiment arguments)
        topo: Mininet topo object (optional)
        topoFile: topology file location (optional)
        noTopo: Allows specification of topology after network object is initialized (optional)
        link: Allows specification of default Mininet/Mininet-Wifi link type for
        connections between nodes (optional)mininetParams: Any params to pass to Mininet-WiFi
        """
        self.parser = self.parseArgs(parser)
        self.args = self.parser.parse_args()

        if not workDir:
            Minindn.workDir = os.path.abspath(self.args.workDir)
        else:
            Minindn.workDir = os.path.abspath(workDir)

        Minindn.resultDir = self.args.resultDir

        self.topoFile = None
        if not topoFile:
            # Args has default topology if none specified
            self.topoFile = self.args.topoFile
        else:
            self.topoFile = topoFile

        self.faces_to_create = {}
        if topo is None and not noTopo:
            try:
                info('Using topology file {}\n'.format(self.topoFile))
                self.topo, self.faces_to_create = self.processTopo(self.topoFile)
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
                Minindn.ndnSecurityDisabled = '/dummy/KEY/-%9C%28r%B8%AA%3B%60' in output.decode("utf-8")
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

        faces = {}
        try:
            items = config.items('faces')
            debug("Faces")
            for item in items:
                face_a, face_b = item[0].split(':')
                debug(item)
                cost = -1
                for param in item[1].split(' '):
                    if param.split("=")[0] == 'cost':
                        cost = param.split("=")[1]
                face_info = (face_b, int(cost))
                if face_a not in faces:
                    faces[face_a] = [face_info]
                else:
                    faces[face_a].append(face_info)
        except configparser.NoSectionError:
            debug("Faces section is optional")
            pass

        return (topo, faces)

    def startMobility(self, max_x=1000, max_y=1000, **kwargs):
        """ Method to run a basic mobility setup on your net"""
        self.net.plotGraph(max_x=max_x, max_y=max_y)
        self.net.startMobility(**kwargs)

    def startMobilityModel(self, max_x=1000, max_y=1000, **kwargs):
        """ Method to run a mobility model on your net until exited"""
        self.net.plotGraph(max_x=max_x, max_y=max_y)
        self.net.setMobilityModel(**kwargs)

    def getWifiInterfaceDelay(self, node, interface=None):
        """Method to return the configured tc delay of a wifi node's interface as a float"""
        if not interface:
            wifi_interface = "{}-wlan0".format(node.name)
        else:
            wifi_interface = interface
        tc_output = node.cmd("tc qdisc show dev {}".format(wifi_interface))
        for line in tc_output.splitlines():
            if "qdisc netem 10:" in line:
                split_line = line.split(" ")
                for index in range(0, len(split_line)):
                    if split_line[index] == "delay":
                        return float(split_line[index + 1][:-2])
        return 0.0

    def setupFaces(self, faces_to_create=None):
        """
        Method to create unicast faces between nodes connected by an AP based on name or faces
        between connected nodes; Returns dict- {node: (other node name, other node IP, other
        node's delay as int)}. This is intended to pass to the NLSR helper via the faceDict param
        """
        if not faces_to_create:
            faces_to_create = self.faces_to_create
        # (nodeName, IP, delay as int)
        # list of tuples
        created_faces = dict()
        batch_faces = dict()
        for nodeAname in faces_to_create.keys():
            if not nodeAname in batch_faces.keys():
                batch_faces[nodeAname] = []
            for nodeBname, faceCost in faces_to_create[nodeAname]:
                if not nodeBname in batch_faces.keys():
                    batch_faces[nodeBname] = []
                nodeA = self.net[nodeAname]
                nodeB = self.net[nodeBname]
                if nodeA.connectionsTo(nodeB):
                    best_interface = None
                    delay = None
                    for interface in nodeA.connectionsTo(nodeB):
                        interface_delay = self.getInterfaceDelay(nodeA, interface[0])
                        if not delay or int(interface_delay) < delay:
                            best_interface = interface
                    faceAIP = best_interface[0].IP()
                    faceBIP = best_interface[1].IP()
                    # Node delay should be symmetrical
                    nodeDelay = int(self.getInterfaceDelay(nodeA, best_interface[0]))
                else:
                    # Default IP will be the primary wireless interface, unclear if multiple wireless
                    # interfaces should be handled
                    faceAIP = nodeA.IP()
                    faceBIP = nodeB.IP()
                    nodeADelay = self.getWifiInterfaceDelay(nodeA)
                    nodeBDelay = self.getWifiInterfaceDelay(nodeB)
                    nodeDelay = nodeADelay + nodeBDelay

                if not faceCost == -1:
                    nodeALink = (nodeA.name, faceAIP, faceCost)
                    nodeBLink = (nodeB.name, faceBIP, faceCost)
                else:
                    nodeALink = (nodeA.name, faceAIP, nodeDelay)
                    nodeBLink = (nodeB.name, faceBIP, nodeDelay)

                batch_faces[nodeAname].append([faceBIP, "udp", True])
                batch_faces[nodeBname].append([faceAIP, "udp", True])

                if nodeA not in created_faces:
                    created_faces[nodeA] = [nodeBLink]
                else:
                    created_faces[nodeA].append(nodeBLink)
                if nodeB not in created_faces:
                    created_faces[nodeB] = [nodeALink]
                else:
                    created_faces[nodeB].append(nodeALink)
        for station_name in batch_faces.keys():
            self.nfdcBatchProcessing(self.net[station_name], batch_faces[station_name])
        return created_faces