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

import argparse
import sys
import time
import os
import configparser
from subprocess import call, Popen, PIPE
import shutil
import glob
from traceback import format_exc

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Switch
from mininet.util import ipStr, ipParse
from mininet.log import info, debug, error

class Minindn(object):
    """
    This class provides the following features to the user:
        1) Wrapper around Mininet object with option to pass topology directly
           1.1) Users can pass custom argument parser to extend the default on here
        2) Parses the topology file given via command line if user does not pass a topology object
        3) Provides way to stop Mini-NDN via stop
           3.1) Applications register their clean up function with this class
        4) Sets IPs on neighbors for connectivity required in a switch-less topology
        5) Some other utility functions
    """
    ndnSecurityDisabled = False
    workDir = '/tmp/minindn'
    resultDir = None

    def __init__(self, parser=argparse.ArgumentParser(), topo=None, topoFile=None, noTopo=False,
                 link=TCLink, workDir=None, **mininetParams):
        """
        Create MiniNDN object
        :param parser: Parent parser of Mini-NDN parser
        :param topo: Mininet topo object (optional)
        :param topoFile: Mininet topology file location (optional)
        :param noTopo: Allows specification of topology after network object is
          initialized (optional)
        :param link: Allows specification of default Mininet link type for connections between
          nodes (optional)
        :param mininetParams: Any params to pass to Mininet
        """
        self.parser = Minindn.parseArgs(parser)
        self.args = self.parser.parse_args()

        if not workDir:
            Minindn.workDir = os.path.abspath(self.args.workDir)
        else:
            Minindn.workDir = os.path.abspath(workDir)

        Minindn.resultDir = self.args.resultDir

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
            self.net = Mininet(topo=self.topo, link=link, **mininetParams)
        else:
            self.net = Mininet(link=link, **mininetParams)

        self.initParams(self.net.hosts)

        self.cleanups = []

        if not self.net.switches:
            self.ethernetPairConnectivity()

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

    @staticmethod
    def parseArgs(parent):
        parser = argparse.ArgumentParser(prog='minindn', parents=[parent], add_help=False)

        # nargs='?' required here since optional argument
        parser.add_argument('topoFile', nargs='?', default='/usr/local/etc/mini-ndn/default-topology.conf',
                            help='If no template_file is given, topologies/default-topology.conf \
                            will be used.')

        parser.add_argument('--work-dir', action='store', dest='workDir', default='/tmp/minindn',
                            help='Specify the working directory; default is /tmp/minindn')

        parser.add_argument('--result-dir', action='store', dest='resultDir', default=None,
                            help='Specify the full path destination folder where experiment \
                            results will be moved')

        return parser

    def ethernetPairConnectivity(self):
        ndnNetBase = '10.0.0.0'
        interfaces = []
        for host in self.net.hosts:
            for intf in host.intfList():
                link = intf.link
                node1, node2 = link.intf1.node, link.intf2.node

                if isinstance(node1, Switch) or isinstance(node2, Switch):
                    continue

                if link.intf1 not in interfaces and link.intf2 not in interfaces:
                    interfaces.append(link.intf1)
                    interfaces.append(link.intf2)
                    node1.setIP(ipStr(ipParse(ndnNetBase) + 1) + '/30', intf=link.intf1)
                    node2.setIP(ipStr(ipParse(ndnNetBase) + 2) + '/30', intf=link.intf2)
                    ndnNetBase = ipStr(ipParse(ndnNetBase) + 4)

    @staticmethod
    def processTopo(topoFile):
        config = configparser.ConfigParser(delimiters=' ', allow_no_value=True)
        config.read(topoFile)
        topo = Topo()

        items = config.items('nodes')
        coordinates = []

        for item in items:
            name = item[0].split(':')[0]
            params = {}
            if item[1]:
                if all (x in item[1] for x in ['radius', 'angle']) and item[1] in coordinates:
                    error("FATAL: Duplicate Coordinate, \'{}\' used by multiple nodes\n" \
                        .format(item[1]))
                    sys.exit(1)
                coordinates.append(item[1])

                for param in item[1].split(' '):
                    if param == '_':
                        continue
                    params[param.split('=')[0]] = param.split('=')[1]

            topo.addHost(name, params=params)

        try:
            items = config.items('switches')
            for item in items:
                name = item[0].split(':')[0]
                topo.addSwitch(name)
        except configparser.NoSectionError:
            # Switches are optional
            pass

        items = config.items('links')
        for item in items:
            link = item[0].split(':')

            params = {}
            for param in item[1].split(' '):
                key = param.split('=')[0]
                value = param.split('=')[1]
                if key in ['jitter', 'max_queue_size']:
                    value = int(value)
                if key == 'loss' or key == 'bw':
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

        return topo

    def start(self):
        self.net.start()
        time.sleep(3)

    def stop(self):
        for cleanup in self.cleanups:
            cleanup()
        self.net.stop()

        if Minindn.resultDir is not None:
            info("Moving results to \'{}\'\n".format(Minindn.resultDir))
            os.system("mkdir -p {}".format(Minindn.resultDir))
            for file in glob.glob('{}/*'.format(Minindn.workDir)):
                shutil.move(file, Minindn.resultDir)

    @staticmethod
    def cleanUp():
        devnull = open(os.devnull, 'w')
        call('nfd-stop', stdout=devnull, stderr=devnull)
        call('mn --clean'.split(), stdout=devnull, stderr=devnull)

    @staticmethod
    def verifyDependencies():
        """Prevent MiniNDN from running without necessary dependencies"""
        dependencies = ['nfd', 'nlsr', 'infoedit', 'ndnping', 'ndnpingserver']
        devnull = open(os.devnull, 'w')
        # Checks that each program is in the system path
        for program in dependencies:
            if call(['which', program], stdout=devnull):
                error('{} is missing from the system path! Exiting...\n'.format(program))
                sys.exit(1)
        devnull.close()

    @staticmethod
    def sleep(seconds):
        # sleep is not required if ndn-cxx is using in-memory keychain
        if not Minindn.ndnSecurityDisabled:
            time.sleep(seconds)

    @staticmethod
    def handleException():
        """Utility method to perform cleanup steps and exit after catching exception"""
        Minindn.cleanUp()
        info(format_exc())
        exit(1)

    def getInterfaceDelay(self, node, interface):
        tc_output = node.cmd("tc qdisc show dev {}".format(interface))
        for line in tc_output.splitlines():
            if "qdisc netem 10:" in line:
                split_line = line.split(" ")
                for index in range(0, len(split_line)):
                    if split_line[index] == "delay":
                        return float(split_line[index + 1][:-2])
        return 0.0

    def initParams(self, nodes):
        """Initialize Mini-NDN parameters for array of nodes"""
        for host in nodes:
            if 'params' not in host.params:
                host.params['params'] = {}
            host.params['params']['workDir'] = Minindn.workDir
            homeDir = '{}/{}'.format(Minindn.workDir, host.name)
            host.params['params']['homeDir'] = homeDir
            host.cmd('mkdir -p {}'.format(homeDir))
            host.cmd('export HOME={} && cd ~'.format(homeDir))

    def nfdcBatchProcessing(self, station, faces):
        # Input format: [IP, protocol, isPermanent]
        batch_file = open("{}/{}/nfdc.batch".format(Minindn.workDir, station.name), "w")
        lines = []
        for face in faces:
            ip = face[0]
            protocol = face[1]
            if face[2]:
                face_type = "permanent"
            else:
                face_type = "persistent"
            nfdc_command = "face create {}://{} {}\n".format(protocol, ip, face_type)
            lines.append(nfdc_command)
        batch_file.writelines(lines)
        batch_file.close()
        debug(station.cmd("nfdc -f {}/{}/nfdc.batch".format(Minindn.workDir, station.name)))

    def setupFaces(self, faces_to_create=None):
        """ Method to create unicast faces between connected nodes;
            Returns dict- {node: (other node name, other node IP, other node's delay as int)}. 
            This is intended to pass to the NLSR helper via the faceDict param """
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
                    # Node delay will be symmetrical for connected nodes
                    nodeDelay = int(self.getInterfaceDelay(nodeA, best_interface[0]))
                    #nodeBDelay = int(self.getInterfaceDelay(nodeB, best_interface[1]))
                else:
                    # If no direct wired connections exist (ie when using a switch),
                    # assume the default interface
                    faceAIP = nodeA.IP()
                    faceBIP = nodeB.IP()
                    nodeADelay = int(self.getInterfaceDelay(nodeA, nodeA.defaultIntf()))
                    nodeBDelay = int(self.getInterfaceDelay(nodeB, nodeB.defaultIntf()))
                    nodeDelay = nodeADelay + nodeBDelay

                if not faceCost == -1:
                    nodeALink = (nodeA.name, faceAIP, faceCost)
                    nodeBLink = (nodeB.name, faceBIP, faceCost)
                else:
                    nodeALink = (nodeA.name, faceAIP, nodeDelay)
                    nodeBLink = (nodeB.name, faceBIP, nodeDelay)

                # Importing this before initialization causes issues
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