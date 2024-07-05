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
from minindn.util import MACToEther, getPopen

from subprocess import PIPE

# If needed (e.g. to speed up the process), use a smaller (or larger value)
# based on your machines resource (CPU, memory)
SLEEP_TIME = 0.0015

class _NfdcBase(object):
    STRATEGY_ASF = 'asf'
    STRATEGY_BEST_ROUTE = 'best-route'
    STRATEGY_MULTICAST = 'multicast'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_TCP = 'tcp'
    PROTOCOL_ETHER = 'ether'

def _registerRoute(namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255,
                    cost=0, inheritFlag=True, captureFlag=False, expirationInMillis=None):
    cmd = ""
    if remoteNode.isdigit() and not protocol == "fd":
        cmd = f'route add {namePrefix} {remoteNode} origin {origin} cost {cost}'
    else:
        if protocol == "ether":
            remoteNode = MACToEther(remoteNode)
        cmd = f'route add {namePrefix} {protocol}://{remoteNode} origin {origin} cost {cost}'
    if not inheritFlag:
        cmd += " no-inherit"
    if captureFlag:
        cmd += " capture"
    if expirationInMillis:
        cmd += f" expires {expirationInMillis}"
    return cmd

def _unregisterRoute(namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255):
    cmd = ""
    if remoteNode.isdigit() and not protocol == "fd":
        cmd = f'route remove {namePrefix} {remoteNode} origin {origin}'
    else:
        if protocol == "ether":
            remoteNode = MACToEther(remoteNode)
        cmd = f'route remove {namePrefix} {protocol}://{remoteNode} origin {origin}'
    return cmd

def _createFace(remoteNodeAddress, protocol=_NfdcBase.PROTOCOL_UDP, isPermanent=False, localInterface=''):
    '''Create face in node's NFD instance. Returns FaceID of created face or -1 if failed.'''
    if protocol == "ether" and not localInterface:
        warn("Cannot create ethernet face without local interface!")
        return
    elif protocol != "ether" and localInterface:
        warn("Cannot create non-ethernet face with local interface specified!")
        return
    elif protocol == "ether" and localInterface:
        remoteNodeAddress = MACToEther(remoteNodeAddress)
    cmd = (f'face create {protocol}://{remoteNodeAddress} '
           f'{f"local dev://{localInterface} " if localInterface else ""}'
           f'{"persistency permanent" if isPermanent else "persistency persistent"}')
    return cmd

def _destroyFace(remoteNode, protocol=_NfdcBase.PROTOCOL_UDP):
    cmd = ""
    if remoteNode.isdigit() and not protocol == "fd":
        cmd = f'face destroy {remoteNode}'
    else:
        if protocol == "ether":
            remoteNode = MACToEther(remoteNode)
        cmd = f'face destroy {protocol}://{remoteNode}'
    return cmd

def _setStrategy(namePrefix, strategy):
    cmd = f'strategy set {namePrefix} ndn:/localhost/nfd/strategy/{strategy}'
    return cmd

def _unsetStrategy(namePrefix):
    cmd = f'strategy unset {namePrefix}'
    return cmd

class Nfdc(_NfdcBase):
    @staticmethod
    def registerRoute(node, namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255,
                      cost=0, inheritFlag=True, captureFlag=False, expirationInMillis=None):
        cmd = "nfdc " + _registerRoute(namePrefix, remoteNode, protocol, origin, cost, inheritFlag, captureFlag, expirationInMillis)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unregisterRoute(node, namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255):
        cmd = "nfdc " + _unregisterRoute(namePrefix, remoteNode, protocol, origin)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def createFace(node, remoteNodeAddress, protocol=_NfdcBase.PROTOCOL_UDP, isPermanent=False, localInterface='', allowExisting=True):
        '''Create face in node's NFD instance. Returns FaceID of created face or -1 if failed.'''
        cmd = "nfdc " + _createFace(remoteNodeAddress, protocol, isPermanent, localInterface)
        output = node.cmd(cmd)
        debug(output)
        Minindn.sleep(SLEEP_TIME)
        if "face-created" in output or (allowExisting and ("face-exists" in output or "face-updated" in output)):
            faceID = output.split(" ")[1][3:]
            if "face-exists" in output or "face-updated" in output:
               debug(f'[{node.name}] Existing face found: {faceID}\n')
            return faceID
        warn(f'[{node.name}] Face register failed: {output}\n')
        return -1

    @staticmethod
    def destroyFace(node, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP):
        cmd = "nfdc " + _destroyFace(remoteNode, protocol)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def setStrategy(node, namePrefix, strategy):
        cmd = "nfdc " + _setStrategy(namePrefix, strategy)
        out = node.cmd(cmd)
        if out.find('error') != -1:
            warn(f'[{node.name}] Error on strategy set out: {out}')
        debug(out)
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def unsetStrategy(node, namePrefix):
        cmd = "nfdc " + _unsetStrategy(namePrefix)
        debug(node.cmd(cmd))
        Minindn.sleep(SLEEP_TIME)

    @staticmethod
    def getFaceId(node, remoteNodeAddress, localEndpoint=None, protocol=_NfdcBase.PROTOCOL_UDP, portNum="6363"):
        '''Returns the faceId for a remote node based on FaceURI, or -1 if a face is not found'''
        # Because this is an interactive helper method, we don't split this into _NfdcBase.
        local = ""
        if localEndpoint:
            local = f' local {localEndpoint}'
        if protocol == "ether":
            remoteNodeAddress = MACToEther(remoteNodeAddress)
            output = node.cmd(f'nfdc face list remote {protocol}://{remoteNodeAddress}{local}')
        else:
            output = node.cmd(f'nfdc face list remote {protocol}://{remoteNodeAddress}:{portNum}{local}')
        debug(output)
        Minindn.sleep(SLEEP_TIME)
        # This is fragile but we don't have that many better options
        if "faceid=" not in output:
            return -1
        faceId = output.split(" ")[0][7:]
        return faceId

class NfdcBatch(_NfdcBase):
    '''Helper for writing and passing an Nfdc batch file to Nfd'''
    def __init__(self):
        self.batch_commands = []

    def executeBatch(self, node, batch_file_name = None):
        '''Execute batch file on node given as argument.
        Optional: batch_file_name is the name of the file that will be created in the node's home dir.'''
        # The intended use of this method is to either use it for a universal configuration or to use an
        # individual object for each node.
        if batch_file_name == None:
            batch_file_name = "nfdc_helper.batch"
        batch_str = "\n".join(self.batch_commands)
        file_path = f'{node.params["params"]["homeDir"]}/{batch_file_name}'
        with open(file_path, "w") as f:
            f.write(batch_str)
        process = getPopen(node, f'nfdc --batch {file_path}')
        # End user can poll if process has finished if desirable; this is also why we do not clean up the
        # temporary files.
        return process

    def registerRoute(self, namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255,
                      cost=0, inheritFlag=True, captureFlag=False, expirationInMillis=None):
        self.batch_commands.append(_registerRoute(namePrefix, remoteNode, protocol, origin, cost, inheritFlag, captureFlag, expirationInMillis))

    def unregisterRoute(self, namePrefix, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP, origin=255):
        self.batch_commands.append(_unregisterRoute(namePrefix, remoteNode, protocol, origin))

    def createFace(self, remoteNodeAddress, protocol=_NfdcBase.PROTOCOL_UDP, isPermanent=False, localInterface=''):
        self.batch_commands.append(_createFace(remoteNodeAddress, protocol, isPermanent, localInterface))

    def destroyFace(self, remoteNode, protocol=_NfdcBase.PROTOCOL_UDP):
        self.batch_commands.append(_destroyFace(remoteNode, protocol))

    def setStrategy(self, namePrefix, strategy):
        self.batch_commands.append(_setStrategy(namePrefix, strategy))

    def unsetStrategy(self, namePrefix):
        self.batch_commands.append(_unsetStrategy(namePrefix))