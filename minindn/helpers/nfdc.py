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

from mininet.log import debug
from minindn.minindn import Minindn

SLEEP_TIME = 0.2

class Nfdc(object):
    STRATEGY_ASF = 'asf'
    STRATEGY_BEST_ROUTE = 'best-route'
    STRATEGY_MULTICAST = 'multicast'
    STRATEGY_NCC = 'ncc'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_TCP = 'tcp'
    PROTOCOL_ETHER = 'ether'

    @staticmethod
    def registerRoute(node, namePrefix, remoteNodeAddress, protocol=PROTOCOL_UDP, origin=255,
                      cost=0, inheritFlag=True, captureFlag=False, expirationInMillis=None):
        cmd = ('nfdc route add {} {}://{} origin {} cost {} {}{}{}').format(
            namePrefix,
            protocol,
            remoteNodeAddress,
            origin,
            cost,
            'no-inherit ' if not inheritFlag else '',
            'capture ' if captureFlag else '',
            'expires {}'.format(expirationInMillis) if expirationInMillis else ''
        )

        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unregisterRoute(node, namePrefix, remoteNodeAddress, origin=255):
        cmd = 'nfdc route remove {} {} {}'.format(namePrefix, remoteNodeAddress, origin)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def createFace(node, remoteNodeAddress, protocol='udp', isPermanent=False):
        cmd = ('nfdc face create {}://{} {}'.format(
            protocol,
            remoteNodeAddress,
            'permanent' if isPermanent else 'persistent'
        ))
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def destroyFace(node, remoteNodeAddress, protocol='udp'):
        debug(node.cmd('nfdc face destroy {}://{}'.format(protocol, remoteNodeAddress)))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def setStrategy(node, namePrefix, strategy):
        cmd = 'nfdc strategy set {} ndn:/localhost/nfd/strategy/{}'.format(namePrefix, strategy)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unsetStrategy(node, namePrefix):
        debug(node.cmd("nfdc strategy unset {}".format(namePrefix)))
        Minindn.sleep(SLEEP_TIME)
