 # -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2019, The University of Memphis
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

# IMPORTANT! This feature is in highly experimental phase and may go several changes
# in future

from mininet.log import info
from ndn.apps.nfdc import Nfdc as nfdc
from collections import defaultdict
from ndn.apps.calculate_routing import CalculateRoutes
from mininet.log import warn

class GlobalRoutingHelper():
    """
    This module is a helper class which helps to create face and register routes
    to NFD from a given node to all of its neighbors.

    :param NetObject netObject: Mininet net object
    :param FaceType faceType: UDP, Ethernet etc.
    :param Routing routingType: (optional) Routing algorithm, link-state or hr etc

    """
    def __init__(self, netObject, faceType=nfdc.PROTOCOL_UDP, routingType="link-state"):
        self.net = netObject
        self.faceType = faceType
        self.routingType = routingType
        self.routes = []
        self.namePrefixes = {host_name.name: [] for host_name in self.net.hosts}
        self.routeObject = CalculateRoutes(self.net, self.routingType)

    def globalRoutingHelperHandler(self):
        for host in self.net.hosts:
            neighborIPs = self.getNeighbor(host)
            self.createFaces(host, neighborIPs)
            self.routeAdd(host, neighborIPs)

        info('Processed all the routes to NFD\n')

    def addOrigin(self, nodes, prefix):
        """
        Add prefix/s as origin on node/s

        :param Prefix prefix: Prefix that is originated by node/s (as producer) for this prefix
        :param Nodes nodes: List of nodes from net object
        """
        for node in nodes:
            self.namePrefixes[node.name] = prefix

    def calculateNPossibleRoutes(self, nFaces=0):
        """
        By default, calculates all possible routes i.e. routes via all the faces of a node.
        pass nFaces if want to compute routes via n number of faces. e.g. 2. For larger topology
        the computation might take huge amount of time.

        :param int nFaces: (optional) number of faces to consider while computing routes. Default
          i.e. nFaces = 0 will compute all possible routes

        """
        self.routes = self.routeObject.getRoutes(nFaces)
        if self.routes:
            self.globalRoutingHelperHandler()
        else:
            warn("Route computation failed\n")

    def calculateRoutes(self):
        # Calculate shortest path for every node
        calculateNPossibleRoutes(self, nFaces=1)

    def createFaces(self, node, neighborIPs):
        for ip in neighborIPs.values():
            nfdc.createFace(node, ip, self.faceType)

    def routeAdd(self, node, neighborIPs):
        """
        Add route from a node to its neighbors for each prefix/s  advertised by destination node

        :param Node node: source node (Mininet net.host)
        :param IP neighborIPs: IP addresses of neighbors
        """
        neighbors = self.routes[node.name]
        for route in neighbors:
            destination = route[0]
            cost = int(route[1])
            nextHop = route[2]
            defaultPrefix = "/ndn/{}-site/{}".format(destination, destination)
            prefixes = [defaultPrefix] + self.namePrefixes[destination]
            for prefix in prefixes:
                # Register routes to all the available destination name prefix/s
                nfdc.registerRoute(node, prefix, neighborIPs[nextHop], \
                                   nfdc.PROTOCOL_UDP, cost=cost)
    @staticmethod
    def getNeighbor(node):
        # Nodes to IP mapping
        neighborIPs = defaultdict()
        for intf in node.intfList():
            link = intf.link
            if link:
                node1, node2 = link.intf1.node, link.intf2.node

                if node1 == node:
                    other = node2
                    ip = other.IP(str(link.intf2))
                else:
                    other = node1
                    ip = other.IP(str(link.intf1))

                # Used later to create faces
                neighborIPs[other.name] = ip
        return neighborIPs