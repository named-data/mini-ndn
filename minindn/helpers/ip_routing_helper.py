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

from igraph import Graph
from mininet.log import info, debug


class LinkInfo(object):
    """
    This class is used to encapsule link information (IP and interface names).
    """

    def __init__(self, start_intf_name, start_ip, end_intf_name, end_ip):
        self.start_intf_name = start_intf_name
        self.start_intf_ip = start_ip
        self.end_intf_name = end_intf_name
        self.end_ip = end_ip


class IPRoutingHelper(object):
    """The routing helper allows to run IP-based evaluations with Mini-NDN. It configures static IP
    routes to all nodes, which means that all nodes can reach all other nodes in the network
    reachable, even when relaying is required.

     Usage from Experiment folder: `IPRoutingHelper.calcAllRoutes(self.net)`
    """

    @staticmethod
    def findLinkInformation(links, first_node, second_node):
        """ This method returns link information of a link connecting two nodes.

        :param links: All links in the emulation topology
        :param first_node: Current node which is looked at
        :param second_node: Target node (neighbour  of first_node)
        :return: Link information as LinkInfo object, or returns null None if the
            nodes are not directly connected
        """
        for link in links:
            if link.intf1.node.name == first_node and link.intf2.node.name == second_node:
                return LinkInfo(link.intf1.name, link.intf1.ip, link.intf2.name, link.intf2.ip)
            elif link.intf2.node.name == first_node and link.intf1.node.name == second_node:
                return LinkInfo(link.intf2.name, link.intf2.ip, link.intf1.name, link.intf1.ip)

        return None

    @staticmethod
    def calculateAllSubPaths(path):
        """ This method returns all subpaths in forward and reverse order of a given path

        :param path: Given path for which subpaths are calculated
        :return: List of all subpaths
        """
        paths = []

        # Append original path and reversed path
        paths.append(path)
        reversed = path[:]
        reversed.reverse()
        paths.append(reversed)

        # Iterate over all possible lengths for subpaths
        for subpath_length in range(2, len(path)):
            # Get all subpaths of length subpath_lenght of the given path
            for start_index in range(0, len(path) - subpath_length + 1):
                subpath = path[start_index: start_index + subpath_length]
                paths.append(subpath)
                subpath = subpath[:]
                subpath.reverse()
                paths.append(subpath)
        return paths

    @staticmethod
    def replaceExistingSubpaths(path, existing_paths):

        subpaths = []
        for subpath_length in range(3, len(path)):
            for start_index in range(0, len(path) - subpath_length + 1):
                subpaths.append(path[start_index: start_index + subpath_length])
        subpaths.reverse()

        for subpath in subpaths:
            if len(subpath) == len(path):
                continue
            if (subpath[0], subpath[-1]) in existing_paths:
                existing = existing_paths[(subpath[0], subpath[-1])]
                path = path[:path.index(existing[0])] + existing[:] + path[
                                                                      path.index(existing[-1]) + 1:]
                break
        return path

    @staticmethod
    def calcAllRoutes(net):
        """ Configures IP routes between all nodes in the emulation topology. This is done in three
         steps:

        1) IP forwarding is enabled on all nodes
        2) The igraph lib is used to calculate all shortest paths between the nodes
        3) Route add commands are used to actually configure the ip routes

        :param net:
        """

        mini_nodes = net.hosts
        mini_links = net.links

        # Enabling IP forwaring on all nodes
        info('Configure IP forwarding on all nodes\n')
        for node in mini_nodes:
            node.cmd('sysctl -w net.ipv4.ip_forward=1')

        # Create the network graph to calculate all shortest paths between nodes
        node_names = [node.name for node in mini_nodes]
        links = []
        for link in mini_links:
            links.append((link.intf1.node.name, link.intf2.node.name))
            links.append((link.intf2.node.name, link.intf1.node.name))
        networkGraph = Graph()
        networkGraph = networkGraph.as_directed()
        for node in node_names:
            networkGraph.add_vertex(node)
        for (a, b) in links:
            networkGraph.add_edges([(a, b), (b, a)])

        existing_paths = {}  # Variable existing_paths stores all paths that are installed
        shortest_paths = []  # List of calculated shorted paths betweeen all nodes

        # Calculate shortest paths between all nodes using libigraph
        for from_node in node_names:
            for to_node in node_names:
                if from_node != to_node:
                    if (from_node, to_node) in existing_paths \
                            or (to_node, from_node) in existing_paths:
                        continue
                    paths = networkGraph.get_all_shortest_paths(from_node, to_node)
                    if len(paths) == 0:
                        continue
                    paths.sort(key=lambda x: str(x))
                    paths.sort(key=lambda x: len(x))
                    shortest_path = paths[0]  # Shortest path with node indizes as nodes
                    # Translate node indizes to node names
                    shortest_path_nodenames = [networkGraph.vs['name'][node]
                                               for node in shortest_path]
                    shortest_paths.append(shortest_path_nodenames)

        # Iterate over shortest paths and store subpaths that need to be installed on the nodes.
        # Also, it is made sure that all paths and reverse paths are the same
        shortest_paths.sort(key=lambda x: len(x), reverse=True)
        for path in shortest_paths:
            # Replace already existing subpaths of the path to make sure that no two paths between
            # two nodes exist
            path = IPRoutingHelper.replaceExistingSubpaths(path, existing_paths)

            # Mark all subpaths of path to install on nodes, unless they already exist
            subpaths = IPRoutingHelper.calculateAllSubPaths(path)
            for subpath in subpaths:
                if (subpath[0], subpath[-1]) not in existing_paths:
                    existing_paths[(subpath[0], subpath[-1])] = subpath

        # Iterate over all paths and configure the routes using the 'route add'
        info('Configure routes on all nodes\n')
        for path in existing_paths.values():
            start_node = path[0]
            end_node = path[-1]
            mini_start = net.get(start_node)
            mini_end = net.get(end_node)

            link_info = IPRoutingHelper.findLinkInformation(mini_links, path[0], path[1])
            start_intf = link_info.start_intf_name

            # Configure the route for every IP address of the destination
            for intf in mini_end.intfs:
                addr = mini_end.intfs[intf].ip
                if len(path) == 2:
                    # For direct connection, configure exit interface
                    debug('[{}] route add -host {} dev {}\n'.format(start_node, addr, start_intf))
                    mini_start.cmd('route add -host {} dev {}'.format(addr, start_intf))
                elif len(path) > 2:
                    # For longer paths, configure next hop as gateway
                    gateway_ip = link_info.end_ip
                    debug('[{}] route add -host {} dev {} gw {}\n'
                          .format(start_node, addr, start_intf, gateway_ip))
                    mini_start.cmd('route add -host {} dev {} gw {}'
                                   .format(addr, start_intf, gateway_ip))
