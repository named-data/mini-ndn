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

from mininet.log import debug, warn
from minindn.minindn import Minindn

# If needed (e.g. to speed up the process), use a smaller (or larger value) 
# based on your machines resource (CPU, memory)
SLEEP_TIME = 0.0015

class Nfdc(object):
    STRATEGY_ASF = 'asf'
    STRATEGY_BEST_ROUTE = 'best-route'
    STRATEGY_MULTICAST = 'multicast'
    STRATEGY_NCC = 'ncc'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_TCP = 'tcp'
    PROTOCOL_ETHER = 'ether'

    @staticmethod
    def registerRoute(node, namePrefix, remoteNode, protocol=PROTOCOL_UDP, origin=255,
                      cost=0, inheritFlag=True, captureFlag=False, expirationInMillis=None):
        cmd = ""
        if remoteNode.isdigit() and not protocol == "fd":
            cmd = ('nfdc route add {} {} origin {} cost {} {}{}{}').format(
                namePrefix,
                remoteNode,
                origin,
                cost,
                'no-inherit ' if not inheritFlag else '',
                'capture ' if captureFlag else '',
                'expires {}'.format(expirationInMillis) if expirationInMillis else ''
            )
        else:
            cmd = ('nfdc route add {} {}://{} origin {} cost {} {}{}{}').format(
                namePrefix,
                protocol,
                remoteNode,
                origin,
                cost,
                'no-inherit ' if not inheritFlag else '',
                'capture ' if captureFlag else '',
                'expires {}'.format(expirationInMillis) if expirationInMillis else ''
            )
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unregisterRoute(node, namePrefix, remoteNode, origin=255):
        cmd = ""
        if remoteNode.isdigit() and not protocol == "fd":
            cmd = 'nfdc route remove {} {} {}'.format(namePrefix, remoteNode, origin)
        else:
            cmd = 'nfdc route remove {} {} {}'.format(namePrefix, remoteNode, origin)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def createFace(node, remoteNodeAddress, protocol='udp', isPermanent=False, allowExisting=True):
        '''Create face in node's NFD instance. Returns FaceID of created face or -1 if failed.'''
        cmd = ('nfdc face create {}://{} {}'.format(
            protocol,
            remoteNodeAddress,
            'permanent' if isPermanent else 'persistent'
        ))
        output = node.cmd(cmd)
        debug(output)
        Minindn.sleep(SLEEP_TIME)
        if "face-created" in output or (allowExisting and "face-exists" in output):
            faceID = output.split(" ")[1][3:]
            return faceID
        warn("["+ node.name + "] Face register failed: " + output)
        return -1

    @staticmethod
    def destroyFace(node, remoteNode, protocol='udp'):
        if remoteNode.isdigit() and not protocol == "fd":
            debug(node.cmd('nfdc face destroy {}'.format(protocol, remoteNode)))
        else:
            debug(node.cmd('nfdc face destroy {}://{}'.format(protocol, remoteNode)))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def setStrategy(node, namePrefix, strategy):
        cmd = 'nfdc strategy set {} ndn:/localhost/nfd/strategy/{}'.format(namePrefix, strategy)
        out = node.cmd(cmd)
        if out.find('error') != -1:
            warn("[" + node.name + "] Error on strategy set out: " + out)
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unsetStrategy(node, namePrefix):
        debug(node.cmd("nfdc strategy unset {}".format(namePrefix)))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def getFaceId(node, remoteNodeAddress, localEndpoint=None, protocol="udp", portNum="6363"):
        '''Returns the faceId for a remote node based on FaceURI, or -1 if a face is not found'''
        #Should this be cached or is the hit not worth it?
        local = ""
        if localEndpoint:
            local = " local {}".format(localEndpoint)
        output = node.cmd("nfdc face list remote {}://{}:{}{}".format(protocol, remoteNodeAddress, portNum, local))
        debug(output)
        Minindn.sleep(SLEEP_TIME)
        # This is fragile but we don't have that many better options
        if "faceid=" not in output:
            return -1
        faceId = output.split(" ")[0][7:]
        return faceId
