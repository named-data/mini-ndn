#!/usr/bin/env python3
# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
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

# This script generates a testbed topology based on current data. Note
# that this topology is memory intensive and can have issues on lower specced
# systems due to its size.
# To use, run with python3

import argparse
import datetime
import json
import logging
from os import path
from urllib.request import urlopen

def testbedGen():
    """Returns a string with the Mini-NDN topology version of the testbed"""
    topology = None
    connections = None
    hosts = []
    links = []
    try:
        with urlopen("https://ndndemo.arl.wustl.edu/testbedNodes.json") as url:
            topology = json.loads(url.read().decode())
        with urlopen("https://ndndemo.arl.wustl.edu/links.json") as url:
            connections = json.loads(url.read().decode())
    except:
        logging.error("Failed to retrieve testbed info from WUSTL servers")
        if __name__ == '__main__':
            from sys import exit
            exit(1)
        raise

    logging.info("Generating testbed topology...")
    for node_name in topology:
        node = topology[node_name]
        if node['neighbors']:
            radius = node['hr_radius']
            angle = node['hr_angle']
            host_str = "{}: _ radius={} angle={}\n".format(node_name, radius, angle)
            hosts.append(host_str)
            logging.debug("Add node: {}".format(host_str)[:-1])
        else:
            # A node without neighbors shouldn't be considered part of the testbed
            # for testing purposes
            logging.debug("Node {} has no neighbors, passing...".format(node_name))
    for link in connections:
        node1 = link['start']
        node2 = link['end']
        # This value is equivalent to RTT in the testbed
        delay = link['nlsr_weight']
        link_str = "{}:{} delay={}ms\n".format(node1, node2, delay)
        logging.debug("Add link: {}".format(link_str)[:-1])
        links.append(link_str.strip())

    topo_str = "[nodes]\n"
    for host in hosts:
        topo_str = topo_str + host
    topo_str = topo_str + "[links]\n"
    for link in links:
        topo_str = topo_str + link
    return topo_str.strip()

if __name__ == '__main__':
    default_path = path.dirname(__file__) + '/../topologies/testbed{}.conf'.format(str(datetime.date.today()))
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log_level", help="Log level to output", default="info", choices=["debug", "info", "warning", "error"])
    parser.add_argument("-o", "--output_dir", help="File output location", default=default_path)
    args = parser.parse_args()
    log_level = getattr(logging, args.log_level.upper())
    topologies_path = path.abspath(args.output_dir)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    topo = testbedGen()
    logging.info("Testbed generated, writing to file...")
    with open(topologies_path, "w") as file:
        file.writelines(topo)
    logging.info("Finished")