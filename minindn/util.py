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

import sys
from os.path import isfile
from subprocess import call
from six.moves.urllib.parse import quote

from mininet.cli import CLI

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
    # https://named-data.net/doc/NDN-packet-spec/current/changelog.html#version-0-3
    namePrefix= "/" + ("/".join(filter(None, namePrefix.split("/"))))
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

def copyExistentFile(node, fileList, destination):
    for f in fileList:
        if isfile(f):
            node.cmd('cp {} {}'.format(f, destination))
            break
    if not isfile(destination):
        fileName = destination.split('/')[-1]
        raise IOError('{} not found in expected directory.'.format(fileName))

def popenGetEnv(node, envDict=None):
    env = {}
    homeDir = node.params['params']['homeDir']
    printenv = node.popen('printenv'.split(), cwd=homeDir).communicate()[0].decode('utf-8')
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
    return host.popen(cmd, cwd=host.params['params']['homeDir'],
                      env=popenGetEnv(host, envDict), **params)

class MiniNDNCLI(CLI):
    prompt = 'mini-ndn> '
    def __init__(self, mininet, stdin=sys.stdin, script=None):
        CLI.__init__(self, mininet, stdin, script)

try:
    from mn_wifi.cli import CLI as CLI_wifi

    class MiniNDNWifiCLI(CLI_wifi):
        prompt = 'mini-ndn-wifi> '
        def __init__(self, mininet, stdin=sys.stdin, script=None):
            CLI_wifi.__init__(self, mininet, stdin, script)

except ImportError:
    class MiniNDNWifiCLI:
        def __init__(self):
            raise ImportError('Mininet-WiFi is not installed')
