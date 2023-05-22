# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2020, The University of Memphis
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

'''
This module will compute link state, hyperbolic and geohyperbolic
routes and their costs from the given Mini-NDN topology
'''

import sys
import heapq
from math import sin, cos, sinh, cosh, acos, acosh
import json
import operator
from collections import defaultdict
from joblib import Parallel, delayed

from mininet.log import info, debug, error, warn
from minindn.helpers.nfdc import Nfdc as nfdc

UNKNOWN_DISTANCE = -1
HYPERBOLIC_COST_ADJUSTMENT_FACTOR = 1000

def dijkstra(graph, start, end, ignoredNode=None):
    """
    Compute shortest path and cost from a given source to a destination
    using Dijkstra algorithm

    :param Graph graph: given network topology/graph
    :param Start start: source node in a given network graph/topology
    :end End end: destination node in a given network graph/topology
    :param Node ignoredNode: node to ignore computing shortest path from
    """
    queue = [(0, start, [])]
    seen = set()
    while True:
        (cost, v, path) = heapq.heappop(queue)
        if v not in seen:
            path = path + [v]
            seen.add(v)
            if v == end:
                debug("Distance from {} to {} is {}".format(start, end, cost))
                return cost, path
            for (_next, c) in graph[v].items():
                if _next != ignoredNode: # Ignore path going via ignoreNode
                    heapq.heappush(queue, (cost + c, _next, path))

        if not queue: # return if no path exist from source - destination except via ignoreNode
            debug("Distance from {} to {} is {}".format(start, end, cost))
            return cost, None

def calculateAngularDistance(angleVectorI, angleVectorJ):
    """
    For hyperbolic/geohyperbolic routing algorithm, this function computes angular distance between
    two nodes. A node can have two or more than two angular coordinates.

    :param AngleVectorI angleVectorI: list of angular coordinate of a give node I
    :param AngleVectorJ angleVectorJ: list of angular coordinate of a give node J

    ref: https://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates

    """
    innerProduct = 0.0
    if len(angleVectorI) != len(angleVectorJ):
        error("Angle vector sizes do not match")
        return UNKNOWN_DISTANCE

    # Calculate x0 of the vectors
    x0i = cos(angleVectorI[0])
    x0j = cos(angleVectorJ[0])

    # Calculate xn of the vectors
    xni = sin(angleVectorI[len(angleVectorI) - 1])
    xnj = sin(angleVectorJ[len(angleVectorJ) - 1])

    # Do the aggregation of the (n-1) coordinates (if there is more than one angle)
    # i.e contraction of all (n-1)-dimensional angular coordinates to one variable
    for k in range(0, len(angleVectorI)-1):
        xni *= sin(angleVectorI[k])
        xnj *= sin(angleVectorJ[k])

    innerProduct += (x0i * x0j) + (xni * xnj)

    if len(angleVectorI) > 1:
        for m in range(1, len(angleVectorI)):
            # Calculate euclidean coordinates given the angles and assuming R_sphere = 1
            xmi = cos(angleVectorI[m])
            xmj = cos(angleVectorJ[m])
            for l in range(0, m):
                xmi *= sin(angleVectorI[l])
                xmj *= sin(angleVectorJ[l])

        innerProduct += xmi * xmj

    # ArcCos of the inner product gives the angular distance
    # between two points on a d-dimensional sphere
    angularDist = acos(innerProduct)
    debug("Angular distance from {} to {} is {}".format(angleVectorI, angleVectorJ, angularDist))
    return angularDist

def getHyperbolicDistance(sourceNode, destNode):
    """
    Return hyperbolic or geohyperbolic distance between two nodes. The distance is computed
    on the basis of following algorithm/mathematics
    ref: https://en.wikipedia.org/wiki/Hyperbolic_geometry
    """
    r1 = [key for key in sourceNode][0]
    r2 = [key for key in destNode][0]
    zeta = 1.0
    dtheta = calculateAngularDistance(sourceNode[r1], destNode[r2])
    hyperbolicDistance = (1./zeta) * acosh(cosh(zeta * r1) * cosh(zeta * r2) -\
                                           sinh(zeta * r1) * sinh(zeta * r2) * cos(dtheta))

    debug("Distance from {} to {} is {}".format(sourceNode, destNode, hyperbolicDistance))
    return hyperbolicDistance

class _CalculateRoutes(object):
    """
    Creates a route calculation object, which is used to compute routes from a node to
    every other nodes in a given topology topology using hyperbolic or geohyperbolic
    routing algorithm

    :param NetObject netObj: Mininet net object
    :param RoutingType routingType: (optional) Routing algorithm, link-state or hr etc
    """
    def __init__(self, netObj, routingType):
        self.adjacenctMatrix = defaultdict(dict)
        self.nodeDict = defaultdict(dict)
        self.routingType = routingType
        self.isHrConfigValid = True
        for host in netObj.hosts:
            if 'radius' in host.params['params']:
                radius = float(host.params['params']['radius'])
            else:
                self.isHrConfigValid = False
                radius = 0.0
            if 'angle' in host.params['params']:
                angles = [float(x) for x in host.params['params']['angle'].split(',')]
            else:
                self.isHrConfigValid = False
                angles = [0.0]
            self.nodeDict[host.name][radius] = angles
        for link in netObj.topo.links(withInfo=True):
            linkDelay = int(link[2]['delay'].replace("ms", ""))
            self.adjacenctMatrix[link[0]][link[1]] = linkDelay
            self.adjacenctMatrix[link[1]][link[0]] = linkDelay

    def getNestedDictionary(self):
        return defaultdict(self.getNestedDictionary)

    def getRoutes(self, nFaces):
        resultMatrix = self.getNestedDictionary()
        routes = defaultdict(list)

        if self.routingType == "link-state":
            if nFaces == 1:
                resultMatrix = self.computeDijkastra() # only best routes.
            else:
                resultMatrix = self.computeDijkastraAll() # all possible routes
        elif self.routingType == "hr":
            if self.isHrConfigValid == True:
                # Note: For hyperbolic, only way to find the best routes is by
                # computing all possible routes and getting the best one.
                resultMatrix = self.computeHyperbolic()
            else:
                warn('Hyperbolic coordinates in topology file are either missing or misconfigured.\n')
                warn('Check that each node has one radius value and one or two angle value(s).\n')
                return None

        for node in resultMatrix:
            for destinationNode in resultMatrix[node]:
                # Sort node - destination via neighbor based on their cost
                tempDict = resultMatrix[node][destinationNode]
                shortedTempDict = sorted(tempDict.items(), key=operator.itemgetter(1))
                # nFaces option gets n-best faces based on shortest distance, default is all
                if nFaces == 0:
                    for item in shortedTempDict:
                        viaNeighbor = item[0]
                        cost = item[1]
                        routes[node].append([destinationNode, str(cost), viaNeighbor])
                else:
                    for index, item in enumerate(shortedTempDict):
                        if index >= nFaces:
                            break
                        viaNeighbor = item[0]
                        cost = item[1]
                        routes[node].append([destinationNode, str(cost), viaNeighbor])

        debug("-routes----", routes)
        return routes

    def getNodeNames(self):
        return [k for k in self.nodeDict]

    def computeHyperbolic(self):
        paths = self.getNestedDictionary()
        nodeNames = self.getNodeNames()
        for node in self.nodeDict:
            neighbors = [k for k in self.adjacenctMatrix[node]]
            for viaNeighbor in neighbors:
                others = [x for x in nodeNames if x not in [viaNeighbor, node]]
                paths[node][viaNeighbor][viaNeighbor] = 0
                # Compute distance from neighbors to no-neighbors
                for destinationNode in others:
                    hyperbolicDistance = getHyperbolicDistance(self.nodeDict[viaNeighbor],
                                                               self.nodeDict[destinationNode])
                    hyperbolicCost = int(HYPERBOLIC_COST_ADJUSTMENT_FACTOR \
                                         * round(hyperbolicDistance, 6))
                    paths[node][destinationNode][viaNeighbor] = hyperbolicCost
        debug("Shortest Distance Matrix: {}".format(json.dumps(paths)))
        return paths

    def computeDijkastra(self):
        """
        Dijkstra computation: Compute all the shortest paths from nodes to the destinations.
        And fills the distance matrix with the corresponding source to destination cost
        """
        distanceMatrix = self.getNestedDictionary()
        nodeNames = self.getNodeNames()
        for node in nodeNames:
            others = [x for x in nodeNames if x not in [node]]
            for destinationNode in others:
                cost, path = dijkstra(self.adjacenctMatrix, node, destinationNode)
                viaNeighbor = path[1]
                distanceMatrix[node][destinationNode][viaNeighbor] = cost

        debug("Shortest Distance Matrix: {}".format(json.dumps(distanceMatrix)))
        return distanceMatrix

    def computeDijkastraAll(self):
        """
        Multi-path Dijkastra computation: Compute all the shortest paths from nodes to the
        destinations via all of its neighbors individually. And fills the distanceMatrixViaNeighbor
        with a corresponding source to its destination cost

        Important: distanceMatrixViaNeighbor represents the shortest distance from a source to a
        destination via specific neighbors
        """
        distanceMatrixViaNeighbor = self.getNestedDictionary()
        nodeNames = self.getNodeNames()
        for node in nodeNames:
            neighbors = [k for k in self.adjacenctMatrix[node]]
            for viaNeighbor in neighbors:
                directCost = self.adjacenctMatrix[node][viaNeighbor]
                distanceMatrixViaNeighbor[node][viaNeighbor][viaNeighbor] = directCost
                others = [x for x in nodeNames if x not in [viaNeighbor, node]]
                for destinationNode in others:
                    nodeNeighborCost = self.adjacenctMatrix[node][viaNeighbor]
                    # path variable is not used for now
                    cost, path = dijkstra(self.adjacenctMatrix, viaNeighbor, destinationNode, node)
                    if cost != 0 and path != None:
                        totalCost = cost + nodeNeighborCost
                        distanceMatrixViaNeighbor[node][destinationNode][viaNeighbor] = totalCost

        debug("Shortest Distance Matrix: {}".format(json.dumps(distanceMatrixViaNeighbor)))
        return distanceMatrixViaNeighbor

class NdnRoutingHelper(object):
    """
    This module is a helper class which helps to create face and register routes
    to NFD from a given node to all of its neighbors.

    :param NetObject netObject: Mininet net object
    :param FaceType faceType: UDP, Ethernet etc.
    :param Routing routingType: (optional) Routing algorithm, link-state or hr etc

    """
    def __init__(self, netObject, faceType=nfdc.PROTOCOL_UDP, routingType="link-state", permanentFaces=False):
        self.net = netObject
        self.faceType = faceType
        self.routingType = routingType
        self.permanentFaces = permanentFaces
        self.routes = []
        self.namePrefixes = {host_name.name: [] for host_name in self.net.hosts}
        self.routeObject = _CalculateRoutes(self.net, self.routingType)

    def globalRoutingHelperHandler(self):
        info('Creating faces and adding routes to FIB\n')

        res = Parallel(n_jobs=-1, require='sharedmem',
                       prefer="threads", verbose=1)(delayed(self.addNodeRoutes)(host) for host in self.net.hosts)

        info('Processed all the routes to NFD\n')

    def addNodeRoutes(self, node):
        """
        Create faces to neighbors and add all routes for one node

        :param Node node: Node from net object
        """
        neighborIPs = self.getNeighbor(node)
        neighborFaces = self.createFaces(node, neighborIPs)
        self.routeAdd(node, neighborFaces)

    def addOrigin(self, nodes, prefix):
        """
        Add prefix/s as origin on node/s

        :param Prefix prefix: Prefix that is originated by node/s (as producer) for this prefix
        :param Nodes nodes: List of nodes from net object
        """
        for node in nodes:
            if not node.name in self.namePrefixes:
                self.namePrefixes[node.name] = []
            self.namePrefixes[node.name] += prefix

    def calculateNPossibleRoutes(self, nFaces=0):
        """
        By default, calculates all possible routes i.e. routes via all the faces of a node.
        pass nFaces if want to compute routes via n number of faces. e.g. 2. For larger topology
        the computation might take huge amount of time.

        :param int nFaces: (optional) number of faces to consider while computing routes. Default
          i.e. nFaces = 0 will compute all possible routes

        """
        self.routes = self.routeObject.getRoutes(nFaces)
        if self.routes is not None:
            info('Route computation completed\n')
            self.globalRoutingHelperHandler()
        else:
            warn('Route computation failed\n')
            self.net.stop()
            sys.exit(1)

    def calculateRoutes(self):
        # Calculate shortest path for every node
        self.calculateNPossibleRoutes(nFaces=1)

    def createFaces(self, node, neighborIPs):
        neighborFaces = {}
        for k, ip in neighborIPs.items():
            faceID = nfdc.createFace(node, ip, self.faceType, self.permanentFaces)
            if not isinstance(faceID, str): raise ValueError(faceID)
            neighborFaces[k] = faceID
        return neighborFaces


    def routeAdd(self, node, neighborFaces):
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
                nfdc.registerRoute(node, prefix, neighborFaces[nextHop], cost=cost)
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
