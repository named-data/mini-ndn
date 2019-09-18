# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2019, The University of Memphis,
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

from mininet.node import Node

class AppManager(object):
    def __init__(self, minindn, hosts, cls, **appParams):
        self.cls = cls
        self.apps = []
        for host in hosts:
            # Don't run NDN apps on switches
            if isinstance(host, Node):
                self.startOnNode(host, **appParams)

        minindn.cleanups.append(self.cleanup)

    def startOnNode(self, host, **appParams):
        app = self.cls(host, **appParams)
        app.start()
        self.apps.append(app)

    def cleanup(self):
        for app in self.apps:
            app.stop()

    def __getitem__(self, nodeName):
        for app in self.apps:
            if app.node.name == nodeName:
                return app
        return None

    def __iter__(self):
        return self.apps.__iter__()

    def __next__(self):
        return self.apps.__next__()
