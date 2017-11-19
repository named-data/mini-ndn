#!/usr/bin/env python
# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
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
#
# This file incorporates work covered by the following copyright and
# permission notice:
#
#   Mininet 2.2.1 License
#
#   Copyright (c) 2013-2015 Open Networking Laboratory
#   Copyright (c) 2009-2012 Bob Lantz and The Board of Trustees of
#   The Leland Stanford Junior University
#
#   Original authors: Bob Lantz and Brandon Heller
#
#   We are making Mininet available for public use and benefit with the
#   expectation that others will use, modify and enhance the Software and
#   contribute those enhancements back to the community. However, since we
#   would like to make the Software available for broadest use, with as few
#   restrictions as possible permission is hereby granted, free of charge, to
#   any person obtaining a copy of this Software to deal in the Software
#   under the copyrights without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#   The name and trademarks of copyright holder(s) may NOT be used in
#   advertising or publicity pertaining to the Software or any derivatives
#   without specific, written prior permission.

import ConfigParser, re
import shlex

class confNDNHost():

    def __init__(self, name, app='', params='', cpu=None, cores=None, cache=None):
        self.name = name
        self.app = app
        self.uri_tuples = params
        self.params = params
        self.cpu = cpu
        self.cores = cores
        self.cache = cache

        # For now assume leftovers are NLSR configuration parameters
        self.nlsrParameters = params

    def __repr__(self):
        return 'Name: '    + self.name + \
               ' App: '    + self.app + \
               ' URIS: '   + str(self.uri_tuples) + \
               ' CPU: '    + str(self.cpu) + \
               ' Cores: '  + str(self.cores) + \
               ' Cache: '  + str(self.cache) + \
               ' Radius: ' + str(self.radius) + \
               ' Angle: '  + str(self.angle) +\
               ' NLSR Parameters: ' + self.nlsrParameters

# add class confNdnCar for vndn
class confNdnCar():

    def __init__(self, name, app='', params='', cpu=None, cores=None, cache=None, radius=0, angle=0):
        self.name = name
        self.app = app
        self.uri_tuples = params
        self.params = params
        self.cpu = cpu
        self.cores = cores
        self.cache = cache
        # add the following parameters because a error
        self.radius = radius 
        self.angle = angle 

        # For now assume leftovers are NLSR configuration parameters
        #self.nlsrParameters = params

    def __repr__(self):
        return 'Name: '    + self.name + \
               ' App: '    + self.app + \
               ' URIS: '   + str(self.uri_tuples) + \
               ' CPU: '    + str(self.cpu) + \
               ' Cores: '  + str(self.cores) + \
               ' Cache: '  + str(self.cache) + \
               ' Radius: ' + str(self.radius) + \
               ' Angle: '  + str(self.angle)
               #' NLSR Parameters: ' + self.nlsrParameters

# add class confNdnStation
class confNdnStation():
    def __init__(self, name, app='', params='', cpu=None, cores=None, cache=None, radius=0, angle=0):
        self.name = name
        self.app = app
        self.uri_tuples = params
        self.params = params
        self.cpu = cpu
        self.cores = cores
        self.cache = cache
       # add the following parameters because a error
        self.radius = radius 
        self.angle = angle 

        # For now assume leftovers are NLSR configuration parameters
        #self.nlsrParameters = params

    def __repr__(self):
        return 'Name: '    + self.name + \
               ' App: '    + self.app + \
               ' URIS: '   + str(self.uri_tuples) + \
               ' CPU: '    + str(self.cpu) + \
               ' Cores: '  + str(self.cores) + \
               ' Cache: '  + str(self.cache) + \
               ' Radius: ' + str(self.radius) + \
               ' Angle: '  + str(self.angle)
               #' NLSR Parameters: ' + self.nlsrParameters

# add class confNdnAccessPoint
class confNdnAccessPoint:
    def __init__(self, name):
        self.name=name

class confNdnSwitch:
    def __init__(self, name):
        self.name = name

class confNDNLink():

    def __init__(self,h1,h2,linkDict=None):
        self.h1 = h1
        self.h2 = h2
        self.linkDict = linkDict

    def __repr__(self):
        return 'h1: ' + self.h1 + ' h2: ' + self.h2 + ' params: ' + str(self.linkDict)

def parse_hosts(conf_arq):
    'Parse hosts section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    hosts = []

    items = config.items('nodes')

        #makes a first-pass read to hosts section to find empty host sections
    for item in items:
        name = item[0]
        rest = item[1].split()
        if len(rest) == 0:
            config.set('nodes', name, '_')
        #updates 'items' list
    items = config.items('nodes')

        #makes a second-pass read to hosts section to properly add hosts
    for item in items:

        name = item[0]

        rest = shlex.split(item[1])

        uris = rest
        params = {}
        cpu = None
        cores = None
        cache = None

        for uri in uris:
            if re.match("cpu",uri):
                cpu = float(uri.split('=')[1])
            elif re.match("cores",uri):
                cores = uri.split('=')[1]
            elif re.match("cache",uri):
                cache = uri.split('=')[1]
            elif re.match("mem",uri):
                mem = uri.split('=')[1]
            elif re.match("app",uri):
                app = uri.split('=')[1]
            elif re.match("_", uri):
                app = ""
            else:
                params[uri.split('=')[0]] = uri.split('=')[1]

        hosts.append(confNDNHost(name, app, params, cpu, cores, cache))

    return hosts

# Add the parse_cars() for vndn
def parse_cars(conf_arq):
    'Parse cars section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)
    cars = []
    items = config.items('cars')

    #makes a first-pass read to cars section to find empty car sections
    for item in items:
        name = item[0]
        rest = item[1].split()
        if len(rest) == 0:
            config.set('cars', name, '_')

    #updates 'items' list
    items = config.items('cars')
    #makes a second-pass read to cars section to properly add cars
    for item in items:
        name = item[0]

        rest = shlex.split(item[1])

        uris = rest
        params = {}
        cpu = None
        cores = None
        cache = None
        for uri in uris:
            if re.match("cpu",uri):
                cpu = float(uri.split('=')[1])
            elif re.match("cores",uri):
                cores = uri.split('=')[1]
            elif re.match("cache",uri):
                cache = uri.split('=')[1]
            elif re.match("mem",uri):
                mem = uri.split('=')[1]
            elif re.match("app",uri):
                app = uri.split('=')[1]
            elif re.match("_", uri):
                app = ""
            else:
                params[uri.split('=')[0]] = uri.split('=')[1]

        cars.append(confNdnCar(name, app, params, cpu, cores, cache))
    return cars

# add the parse_stations() and parse_accessPoint() for wifi 
def parse_stations(conf_arq):
    'Parse stations section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    stations = []

    items = config.items('stations')

        #makes a first-pass read to stations section to find empty station sections
    for item in items:
        name = item[0]
        rest = item[1].split()
        if len(rest) == 0:
            config.set('stations', name, '_')
        #updates 'items' list
    items = config.items('stations')

        #makes a second-pass read to stations section to properly add stations
    for item in items:
        name = item[0]

        rest = shlex.split(item[1])

        uris = rest
        params = {}
        cpu = None
        cores = None
        cache = None

        for uri in uris:
            if re.match("cpu",uri):
                cpu = float(uri.split('=')[1])
            elif re.match("cores",uri):
                cores = uri.split('=')[1]
            elif re.match("cache",uri):
                cache = uri.split('=')[1]
            elif re.match("mem",uri):
                mem = uri.split('=')[1]
            elif re.match("app",uri):
                app = uri.split('=')[1]
            elif re.match("_", uri):
                app = ""
            else:
                params[uri.split('=')[0]] = uri.split('=')[1]

        stations.append(confNdnStation(name, app, params, cpu, cores, cache))
    return stations
def parse_accessPoints(conf_arq):
    'Parse accessPoints section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    accessPoints = []

    try:
        items = config.items('accessPoints')
    except ConfigParser.NoSectionError:
        return accessPoints

    for item in items:
        name = item[0]
        accessPoints.append(confNdnAccessPoint(name))

    return accessPoints


def parse_switches(conf_arq):
    'Parse switches section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    switches = []

    try:
        items = config.items('switches')
    except ConfigParser.NoSectionError:
        return switches

    for item in items:
        name = item[0]
        switches.append(confNdnSwitch(name))

    return switches

def parse_links(conf_arq):
    'Parse links section from the conf file.'
    arq = open(conf_arq,'r')

    links = []

    while True:
        line = arq.readline()
        if line == '[links]\n':
            break

    while True:
        line = arq.readline()
        if line == '':
            break

        args = line.split()

        #checks for non-empty line
        if len(args) == 0:
            continue

        h1, h2 = args.pop(0).split(':')

        link_dict = {}

        for arg in args:
            arg_name, arg_value = arg.split('=')
            key = arg_name
            value = arg_value
            if key in ['bw','jitter','max_queue_size']:
                value = int(value)
            if key in ['loss']:
                value = float(value)
            link_dict[key] = value

        links.append(confNDNLink(h1,h2,link_dict))


    return links
