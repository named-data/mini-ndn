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
#   Mininet 2.3.0d1 License
#
#   Copyright (c) 2013-2016 Open Networking Laboratory
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

from mn_wifi.node import Station, Car
from ndn.ndn_host import NdnHostCommon
from ndn.nfd import Nfd

class NdnStation(Station, NdnHostCommon):
    "NDNStation is a Host that always runs NFD, and is wifi-enabled"

    def __init__(self, name, **kwargs):

        Station.__init__(self, name, **kwargs)
        if not self.inited:
            NdnHostCommon.init()

        # Create home directory for a node
        self.homeFolder = "%s/%s" % ("/tmp/minindn", self.name) # Xian: using workDir will occur erro
        self.cmd("mkdir -p %s" % self.homeFolder)
        self.cmd("cd %s" % self.homeFolder)
        print("NdnStation Constructor.")
        self.nfd = None

        self.peerList = {}

    def config(self, app=None, cache=None, **params):

        r = super(NdnStation, self).config(**params)

        self.setParam(r, 'app', app=app)
        self.setParam(r, 'cache', cache=cache)
        print "ndn_host.py------------NdnHost cla-----config() method-----------"
        return r

    def terminate(self):
        "Stop node."
        if self.nfd is not None:
          self.nfd.stop()
        super(NdnStation, self).terminate()

class NdnCar(Car, NdnHostCommon):
    "NdnCar is a Car that always runs NFD, and is wifi-enabled."

    def __init__(self, name, **kwargs):
        Car.__init__(self, name, **kwargs)
        if not self.inited:
            NdnHostCommon.init()
        print("NdnCar constructor.")
        # Create home directory for a node
        self.homeFolder = "%s/%s" % ("/tmp/minindn", self.name) # Xian: using workDir will occur erro
        self.cmd("mkdir -p %s" % self.homeFolder)
        self.cmd("cd %s" % self.homeFolder)

        self.nfd = None

        self.peerList = {}

    def config(self, app=None, cache=None, **params):

        r = super(NdnCar, self).config(**params)

        self.setParam(r, 'app', app=app)
        self.setParam(r, 'cache', cache=cache)
        print "ndn_host.py------------NdnCar cla-----config() method-----------"
        return r

    def terminate(self):
        "Stop node."
        if self.nfd is not None:
          self.nfd.stop()
        super(NdnCar, self).terminate()
