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

from time import sleep
import subprocess

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

def sendFile(node, prefix, file):
    info ("File published:", file)
    cmd = 'ndnputchunks {}/{} < {} > putchunks.log 2>&1 &'.format(prefix, "fname", file)
    node.cmd(cmd)
    # Sleep for appropriate time based on the file size
    sleep(5)

def receiveFile(node, prefix, filename):
    info ("Fething file: ", filename)
    cmd = 'ndncatchunks {}/{} > {} 2> catchunks.log &'.format(prefix, "fname", filename)
    node.cmd(cmd)

if __name__ == '__main__':
    setLogLevel('info')

    # Create a test file to publish
    testFile = "/tmp/test-chunks"
    cmd = 'echo "demonstrate file transfer using catchunks and putchunks" > {}'.format(testFile)
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()

    Minindn.cleanUp()
    Minindn.verifyDependencies()
    ndn = Minindn()
    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(70)

    #   Default topology is used in this experiment "/topologies/default-topology.conf"
    #   lets make node "a" as a producer node, and node "c" as a conumer node
    producer  = ndn.net['a']
    producerPrefix = "/test-producer" # prefix under which the file will be published
    consumer = ndn.net['c']

    # Advertise the producer prefix to the network
    producer.cmd('nlsrc advertise {}'.format(producerPrefix))
    sleep (5) # sleep for routing convergence. 

    sendFile(producer, producerPrefix, testFile)
    receiveFile(consumer, producerPrefix, "test-chunks")

    MiniNDNCLI(ndn.net)
    ndn.stop()