# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2025, The University of Memphis,
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

import re
import sys
from os.path import isfile
from subprocess import call, PIPE

from six.moves.urllib.parse import quote

from mininet.cli import CLI
from mininet.log import error
from mininet.node import Host
from mininet.net import Mininet


sshbase = ['ssh', '-q', '-t', '-i/home/mininet/.ssh/id_rsa']
scpbase = ['scp', '-i', '/home/mininet/.ssh/id_rsa']
devnull = open('/dev/null', 'w')

def getSafeName(namePrefix):
    """
    Check if the prefix/string is safe to use with ndn commands or not.
        return safe prefix.
    :param namePrefix: name of the prefix
    """
    # remove redundant "/"es, multiple "/"es are an invalid representation for empty name component
    namePrefix = "/" + "/".join(filter(None, namePrefix.split("/")))
    return quote(namePrefix, safe='/')

def ssh(login, cmd):
    rcmd = sshbase + [login, cmd]
    call(rcmd, stdout=devnull, stderr=devnull)

def scp(*args):
    tmp = []
    for arg in args:
        tmp.append(arg)
    rcmd = scpbase + tmp
    call(rcmd, stdout=devnull, stderr=devnull)

def copyExistentFile(host, fileList, destination):
    for f in fileList:
        if isfile(f):
            host.cmd('cp {} {}'.format(f, destination))
            break
    if not isfile(destination):
        fileName = destination.split('/')[-1]
        raise IOError('{} not found in expected directory.'.format(fileName))

def popenGetEnv(host, envDict=None):
    '''Helper method to set environment variables for Popen on nodes'''
    env = {}
    homeDir = host.params['params']['homeDir']
    printenv = host.popen('printenv'.split(), cwd=homeDir).communicate()[0].decode('utf-8')
    for var in printenv.split('\n'):
        if var == '':
            break
        p = var.split('=')
        env[p[0]] = p[1]
    env['HOME'] = homeDir

    if envDict is not None:
        for key, value in envDict.items():
            env[key] = str(value)

    return env

def getPopen(host, cmd, envDict=None, **params):
    '''Return Popen object for process on node with correctly set environmental variables'''
    return host.popen(cmd, cwd=host.params['params']['homeDir'],
                      env=popenGetEnv(host, envDict), **params)

def MACToEther(mac):
    # We use the regex filters from face-uri.cpp in ndn-cxx with minor modifications
    if re.match('^\[((?:[a-fA-F0-9]{1,2}\:){5}(?:[a-fA-F0-9]{1,2}))\]$', mac):
        return mac
    elif re.match('^((?:[a-fA-F0-9]{1,2}\:){5}(?:[a-fA-F0-9]{1,2}))$', mac):
        # URI syntax requires nfdc to use brackets for MAC and ethernet addresses due
        # to the use of colons as separators. Incomplete brackets are a code issue.
        return '[%s]' % mac
    error('Potentially malformed MAC address, passing without alteration: %s' % mac)
    return mac

class MiniNDNCLI(CLI):
    prompt = 'mini-ndn> '
    def __init__(self, mininet, stdin=sys.stdin, script=None):
        CLI.__init__(self, mininet, stdin, script)

try:
    from mn_wifi.cli import CLI as CLI_wifi
    from mn_wifi.node import Station as mn_wifi_station
    HAS_WIFI = True
    class MiniNDNWifiCLI(CLI_wifi):
        prompt = 'mini-ndn-wifi> '
        def __init__(self, mininet, stdin=sys.stdin, script=None):
            CLI_wifi.__init__(self, mininet, stdin, script)

except ImportError:
    HAS_WIFI = False
    class MiniNDNWifiCLI:
        def __init__(self):
            raise ImportError('Mininet-WiFi is not installed')

def is_valid_hostid(net: Mininet, host_id: str):
    """Check if a hostId is a host"""
    if host_id not in net:
        return False

    if not isinstance(net[host_id], Host) and \
        (HAS_WIFI and not isinstance(net[host_id], mn_wifi_station)):
        return False

    return True

def run_popen(host, cmd):
    """Helper to run command on node asynchronously and get output (blocking)"""
    process = getPopen(host, cmd, stdout=PIPE)
    return process.communicate()[0]

def run_popen_readline(host, cmd):
    """Helper to run command on node asynchronously and get output line by line (blocking)"""
    process = getPopen(host, cmd, stdout=PIPE)
    while True:
        line: bytes = process.stdout.readline()
        if not line:
            break
        yield line

def host_home(host) -> str | None:
    """Get home directory for host"""
    if 'params' not in host.params or 'homeDir' not in host.params['params']:
        return None
    return host.params['params']['homeDir']
